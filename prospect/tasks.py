from celery import shared_task
import requests
import pandas as pd
import os
from datetime import date, timedelta
from django.utils.dateparse import parse_date
from .models import ProspectData
import xgboost as xgb
from .models import Prospect, SREOData
import openai
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from django.apps import apps
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import datetime
import json
import logging

logger = logging.getLogger(__name__)

# Define function to get access token
def get_access_token():
    url = "https://api.trepp.com/v2.0/oauth/token"
    payload = {"username": "sam@dim3nsion.co", "password": "Treppdata2023$"}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("access_token")

# Function to fetch data from API
def get_data_from_api(access_token, file_path='temp.parquet'):
    yesterday_date = date.today() - timedelta(days=1)
    url = f"https://api.trepp.com/v2.0/datafeeds/daily?start_date={yesterday_date}"
    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(response.json())
    for res in response.json():
        print(res)
        for url in res['urls']:
            response = requests.get(url['url'])
            filename = 'temp.parquet'
            cwd = os.getcwd()
            with open(os.path.join(cwd, filename), 'wb') as f:
                f.write(response.content)
            return filename

def preprocess_dlq(row):
    if row == 'A':
        return 0
    if row == "B":
        return 1
    return row


# Load and preprocess the data
def preprocess_data(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
    else:
        raise ValueError("Unsupported file format")

    columns = ["amortTerm", "secltv", "originationdt", "noi", "ncf", "uweffectivegrossincome", "revenues", "curdlqcode", "impliedCapRateNOI", "curAmortType", "defeasStatus", "occRate", "curLoanBal","apprValPerSqFtOrUnit", "appValue", "modPrePayPenAmt", "prepayPenalty", "vacancyRate", "curBal", "originationYear", "curCpn", "relatedrecordscount", 'loanuniversepropid']
    columns = [col.lower() for col in columns]
    df = df[columns].copy()
    
    df['defeasstatus'] = df['defeasstatus'].fillna(0)
    df['modprepaypenamt'] = df['modprepaypenamt'].fillna(0)
    df['vacancyrate'] = df['vacancyrate'].fillna(0)
    df['occrate'] = df['occrate'].fillna(-1)
    df['curdlqcode'] = df['curdlqcode'].fillna(0)
    
    df = df.dropna()
    propid = df['loanuniversepropid']
    
    today = pd.to_datetime(datetime.date.today())  # Convert to pandas Timestamp
    df['months_passed'] = (today - pd.to_datetime(df['originationdt'])).dt.days // 30
    
    df = df.drop(['originationdt', 'modprepaypenamt', 'loanuniversepropid'], axis=1)
    df['curdlqcode'] = df['curdlqcode'].apply(preprocess_dlq).astype(float)
    
    df = pd.get_dummies(df, columns=['defeasstatus'], prefix='defeasstatus')
    for status in ['F', 'N', 'P']:
        if f'defeasstatus_{status}' not in df.columns:
            df[f'defeasstatus_{status}'] = 0
    
    df = df.astype(float)
    print("final df: ", df)
    return df, propid

# Get the model ready for predictions
def get_model():
    xgb_classifier = xgb.XGBClassifier(enable_categorical=True)
    xgb_classifier.load_model('static/models/xgb_model.json')
    return xgb_classifier

# Make predictions
def make_predictions(df):
    # Assuming 'df' is preprocessed and ready for prediction
    model = get_model()
    predictions = model.predict_proba(df)
    final_predictions = [(int(prob[1]*10)) for prob in predictions]
    return final_predictions

@shared_task
def process_and_store_data():
    access_token = get_access_token()
    data_file = get_data_from_api(access_token)
    df, propid = preprocess_data(data_file)
    predictions = make_predictions(df)

    if data_file.endswith('.csv'):
        newdf = pd.read_csv(data_file)
    elif data_file.endswith('.parquet'):
        newdf = pd.read_parquet(data_file)
    else:
        raise ValueError("Unsupported file format")

    columns_of_interest = ["propname", "city", "loanuniversepropid"]
    newdf = newdf[columns_of_interest]
    filtered_df = newdf[newdf['loanuniversepropid'].isin(propid)].copy()
    filtered_df['predictions'] = predictions

    ProspectData.objects.all().delete()

    for _, row in filtered_df.iterrows():
        prospect_data = ProspectData(
            data=row.to_dict()  # This ensures the data is saved as a JSON object
        )
        prospect_data.save()
        # ProspectData.objects.create(data=row.to_dict())
    os.remove(data_file)


@shared_task
def process_custom_data(data_upload_pk):
    print("processing custom data celery...")
    from .models import DataUpload
    from django.utils import timezone
    data_upload = DataUpload.objects.get(pk = data_upload_pk)
    data_upload.analyze_start_time = timezone.now()
    data_upload.save()
    try:
        file_path = data_upload.file.path
        print("done 1")
        df, propid = preprocess_data(file_path)
        print("done 2")
        predictions = make_predictions(df)
        print("done 3")
    except Exception as e:
        print("error: ", e)


    if file_path.endswith('.csv'):
        newdf = pd.read_csv(file_path)
    columns_of_interest = ["propname", "city", "loanuniversepropid"]
    newdf = newdf[columns_of_interest]
    filtered_df = newdf[newdf['loanuniversepropid'].isin(propid)]
    filtered_df['predictions'] = predictions

    for _, row in filtered_df.iterrows():
        prospect_data = ProspectData(
            data=row.to_dict(),
            upload = data_upload
        )
        prospect_data.save()
    
    data_upload.analyze_end_time = timezone.now()
    data_upload.save()


@shared_task
def process_sreo_document(prospect_id):
    Prospect = apps.get_model('prospect', 'Prospect')
    SREOData = apps.get_model('prospect', 'SREOData')
    
    logger.info(f"Starting SREO document processing for prospect {prospect_id}")

    try:
        prospect = Prospect.objects.get(id=prospect_id)
    except Prospect.DoesNotExist:
        logger.error(f"Prospect with id {prospect_id} does not exist")
        return

    # Read the SREO document
    try:
        with prospect.sreo_document.open('r') as file:
            sreo_content = file.read().decode('utf-8')
    except Exception as e:
        logger.error(f"Error reading SREO document for prospect {prospect_id}: {str(e)}")
        return

    # Use ChatGPT to extract information
    openai.api_key = settings.OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts property information from SREO documents and returns it in JSON format."},
                {"role": "user", "content": f"""
                Extract the following information for each property in this SREO document:
                - Property Name and/or Address
                - Property Type
                - Number of Units
                - Acq. Date
                - Acq. Cost
                - Estimated Current Market Value
                - Market Value Based
                - Lender Name
                - Contact Phone #
                - Loan Number
                - Estimated Current Loan Balance
                - Gross Monthly Income
                - Monthly Loan Payment
                - Monthly Property Tax Amt.
                - Average Monthly Expenses
                - Monthly Cash Flow

                Return the data as a JSON array of objects, where each object represents a property. Use 'N/A' for any missing values.
                Here's the document content: {sreo_content}
                """}
            ]
        )
    except Exception as e:
        logger.error(f"Error in OpenAI API call for prospect {prospect_id}: {str(e)}")
        return

    # Parse the ChatGPT response
    try:
        extracted_data = json.loads(response.choices[0].message['content'])
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from OpenAI response for prospect {prospect_id}")
        return

    # Initialize geocoder
    geolocator = Nominatim(user_agent="neuroprop")

    # Process each property and prepare for bulk create
    sreo_objects = []
    for property_data in extracted_data:
        address = property_data.get('Property Name and/or Address', 'N/A')
        
        # Geocode the address
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                latitude = location.latitude
                longitude = location.longitude
            else:
                latitude = None
                longitude = None
                logger.warning(f"No geocoding results found for address: {address}")
        except (GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable) as e:
            logger.warning(f"Geocoding error for address '{address}': {str(e)}")
            latitude = None
            longitude = None

        # Parse number of units
        try:
            number_of_units = int(property_data.get('Number of Units', 0))
        except ValueError:
            number_of_units = 0
            logger.warning(f"Invalid 'Number of Units' value for property: {address}")

        # Prepare SREOData object
        sreo_objects.append(SREOData(
            prospect=prospect,
            created_by=prospect.created_by,
            property_name=address,
            address=address,
            property_type=property_data.get('Property Type', 'N/A'),
            number_of_units=number_of_units,
            acquisition_date=parse_date_with_timezone(property_data.get('Acq. Date', 'N/A')),
            acquisition_cost=parse_decimal(property_data.get('Acq. Cost', 'N/A')),
            estimated_current_market_value=parse_decimal(property_data.get('Estimated Current Market Value', 'N/A')),
            market_value_based=property_data.get('Market Value Based', 'N/A'),
            lender_name=property_data.get('Lender Name', 'N/A'),
            contact_phone=property_data.get('Contact Phone #', 'N/A'),
            loan_number=property_data.get('Loan Number', 'N/A'),
            estimated_current_loan_balance=parse_decimal(property_data.get('Estimated Current Loan Balance', 'N/A')),
            gross_monthly_income=parse_decimal(property_data.get('Gross Monthly Income', 'N/A')),
            monthly_loan_payment=parse_decimal(property_data.get('Monthly Loan Payment', 'N/A')),
            monthly_property_tax_amount=parse_decimal(property_data.get('Monthly Property Tax Amt.', 'N/A')),
            average_monthly_expenses=parse_decimal(property_data.get('Average Monthly Expenses', 'N/A')),
            monthly_cash_flow=parse_decimal(property_data.get('Monthly Cash Flow', 'N/A')),
            latitude=latitude,
            longitude=longitude
        ))

    # Bulk create SREOData objects
    try:
        SREOData.objects.bulk_create(sreo_objects)
        logger.info(f"Completed SREO document processing for prospect {prospect_id}. Processed {len(sreo_objects)} properties.")
    except Exception as e:
        logger.error(f"Error bulk creating SREOData objects for prospect {prospect_id}: {str(e)}")

def parse_date_with_timezone(date_string):
    naive_date = parse_date(date_string)
    if naive_date:
        return timezone.make_aware(datetime.combine(naive_date, datetime.min.time()))
    return None

def parse_decimal(value):
    try:
        return Decimal(value.replace('$', '').replace(',', ''))
    except:
        return Decimal('0.00')
