import json
import requests
import pandas
import json
import http.client, urllib
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    ONTARIO_COVID_RESULTS_URL = "https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv"

    def read_data(url):
        return pandas.read_csv(url)

    def get_reported_date(data):
        reported_date = data['Reported Date'].iat[-1]
        return datetime.strptime(reported_date, '%Y-%m-%d')

    def get_new_cases(data):
        today_cases = data['Total Cases'].iat[-1]
        yesterday_cases = data['Total Cases'].iat[-2]
        new_cases = today_cases - yesterday_cases
        return "{:.0f}".format(new_cases)

    def is_data_fresh(reported_date):
        return datetime.today().date() == reported_date.date() and datetime.today() >= reported_date

    data = read_data(ONTARIO_COVID_RESULTS_URL)
    new_cases = get_new_cases(data)
    reported_date = get_reported_date(data)
    is_fresh = is_data_fresh(reported_date)
    region = "Ontario"

    message = "Could not retrieve info.   Please try again later"
    
    if is_fresh:
        message = f'{region} is reporting {new_cases} today'
    else:
        message = f'{region} reported {new_cases} new cases yesterday'

    request_data = {
        "token": os.environ['pushoverToken'],
        "user": os.environ['pushoverUser'],
        "message": message
    }

    response = requests.post("https://api.pushover.net/1/messages.json", request_data)

    return {
        "statusCode": response.status_code,
        "body": json.dumps(response.json()),
    }
