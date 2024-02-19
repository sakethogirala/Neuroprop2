from celery import shared_task
import requests
import pandas as pd
import os
from datetime import date, timedelta
from .models import ProspectData
import xgboost as xgb
import datetime
import json

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
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
    columns = ["amortTerm", "secltv", "originationdt", "noi", "ncf", "uweffectivegrossincome", "revenues", "curdlqcode", "impliedCapRateNOI", "curAmortType", "defeasStatus", "occRate", "curLoanBal","apprValPerSqFtOrUnit", "appValue", "modPrePayPenAmt", "prepayPenalty", "vacancyRate", "curBal", "originationYear", "curCpn", "relatedrecordscount", 'loanuniversepropid']
    columns = [col.lower() for col in columns]
    final_df = df[columns]
    final_df.fillna({"defeasstatus": 0 ,"modprepaypenamt": 0, "vacancyrate": 0, "longitude": -1, "latitude": -1, "occrate": -1, "curdlqcode":0}, inplace=True)
    df = final_df.dropna()

    propid = df['loanuniversepropid']
    today = datetime.date.today()
    try:
        df['months_passed'] = df['originationdt'].apply(lambda x: today - datetime.datetime.strptime(x, "%m/%d/%y").date())
    except:
        df['months_passed'] = df['originationdt'].apply(lambda x: today - x)
    df['months_passed'] = df['months_passed'].apply(lambda x: x.days // 30)
    df.drop(['originationdt', 'modprepaypenamt', 'loanuniversepropid'], inplace=True, axis=1)
    df['curdlqcode'] = df['curdlqcode'].apply(preprocess_dlq)
    df['curdlqcode'] = df['curdlqcode'].apply(lambda x: float(x))
    final_df = pd.get_dummies(df, columns=['defeasstatus'], drop_first=True)
    if 'defeasstatus_P' not in final_df:
        final_df['defeasstatus_P'] = [0 for row in range(len(final_df))]
    if 'defeasstatus_N' not in final_df:
        final_df['defeasstatus_N'] = [0 for row in range(len(final_df))]
    if 'defeasstatus_F' not in final_df:
        final_df['defeasstatus_F'] = [0 for row in range(len(final_df))]
    final_df = final_df.astype(float)
    print("final df: ", final_df)
    return final_df, propid

# Get the model ready for predictions
def get_model():
    xgb_classifier = xgb.XGBClassifier()
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
    if data_file.endswith('.parquet'):
        newdf = pd.read_parquet(data_file)
    columns_of_interest = ["propname", "city", "loanuniversepropid"]
    newdf = newdf[columns_of_interest]
    filtered_df = newdf[newdf['loanuniversepropid'].isin(propid)]
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


