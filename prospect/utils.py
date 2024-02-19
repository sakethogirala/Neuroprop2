import requests
import pandas as pd
import json
import datetime
from django.templatetags.static import static
import xgboost as xgb
import os
from datetime import date, timedelta

def get_access_token():
    url = "https://api.trepp.com/v2.0/oauth/token"
    payload = {
        "username": "sam@dim3nsion.co",
        "password": "Treppdata2023$"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    response = requests.post(
        url,
        json=payload,
        headers=headers
    )
    print(response)
    access_token = response.json()["access_token"]
    return access_token

def get_data(
    file_path :str, 
) -> pd.DataFrame:
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(file_path)
    columns = ["amortTerm", "secltv", "originationdt", "noi", "ncf", "uweffectivegrossincome", "revenues", "curdlqcode", "impliedCapRateNOI", "curAmortType", "defeasStatus", "occRate", "curLoanBal","apprValPerSqFtOrUnit", "appValue", "modPrePayPenAmt", "prepayPenalty", "vacancyRate", "curBal", "originationYear", "curCpn", "relatedrecordscount", 'loanuniversepropid']
    columns = [col.lower() for col in columns]
    final_df = df[columns]
    final_df.fillna({"defeasstatus": 0 ,"modprepaypenamt": 0, "vacancyrate": 0, "longitude": -1, "latitude": -1, "occrate": -1, "curdlqcode":0}, inplace=True)
    df = final_df.dropna()

    return df

def preprocess_dlq(row):
    if row == 'A':
        return 0
    if row == "B":
        return 1
    return row


def preprocess(
    df: pd.DataFrame,
) -> pd.DataFrame:
    propid = df['loanuniversepropid']
    today = datetime.date.today()
    try:
        df['months_passed'] = df['originationdt'].apply(lambda x: today - datetime.datetime.strptime(x, "%Y-%m-%d").date())
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
    return final_df, propid


def get_model() -> xgb.XGBClassifier:
    xgb_classifier = xgb.XGBClassifier()
    xgb_classifier.load_model('static/models/xgb_model.json')
    return xgb_classifier

def predict(
    data: pd.DataFrame,
):
    model = get_model()
    predictions = model.predict_proba(data)
    final_predictions = [(int(prob[1]*10)) for prob in predictions]
    return final_predictions


def main(data_file, samples):
    df = get_data(data_file).head(samples)
    final_df, propid = preprocess(df)
    final_df = final_df.astype(float)
    if data_file.endswith('.csv'):
        newdf = pd.read_csv(data_file)
    if data_file.endswith('.parquet'):
        print(data_file)
        newdf = pd.read_parquet(data_file)
    newdf = newdf.loc[newdf['loanuniversepropid'].isin(propid)].head(samples)
    predictions = predict(final_df)
    newdf['predictions'] = predictions
    if "Unnamed: 0" in newdf.columns:
        newdf.drop("Unnamed: 0", axis=1, inplace=True)
    ansdf = newdf.to_dict("list")
    Data.objects.all().delete()
    data = Data(
        data=json.dumps(ansdf, default=str)
    )
    data.save()
    return predictions, propid



def get_data_from_api():
    yesterday_date = date.today() - timedelta(days=1)
    url = f"https://api.trepp.com/v2.0/datafeeds/daily?start_date={yesterday_date}"
    
    headers = {
        'Authorization': f"Bearer {get_access_token()}",
    }
    response = requests.get(
        url, 
        headers=headers,
    )
    print("working...\n")
    print(response.json)
    for res in response.json():
        print(res)
        for url in res['urls']:
            response = requests.get(url['url'])
            filename = 'temp.parquet'
            # Get the current working directory:
            cwd = os.getcwd()
            with open(os.path.join(cwd, filename), 'wb') as f:
                f.write(response.content)
            
            return filename
            
