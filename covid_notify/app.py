import json
import requests
import pandas
import json
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

    def format_output(output_format, new_cases, reported_date, isDataFresh, region, message):
        output = {}
        if output_format == "googleaction":
            request_data = json.loads(event['body'])

            output['session'] = {}
            output['session']['id'] = request_data['session']['id']
            output['session']['params'] = request_data['session']['params']
            output['prompt'] = {}
            output['prompt']['override'] = False
            output['prompt']['firstSimple'] = {}
            output['prompt']['firstSimple']['speech'] = message
            output['prompt']['firstSimple']['text'] = message
        else:
            output['newCases'] = new_cases
            output['reportedDate'] = reported_date.strftime('%Y-%m-%d')
            output['isDataFresh'] = is_fresh
            output['region'] = region
            output['message'] = message

        return output

    data = read_data(ONTARIO_COVID_RESULTS_URL)
    new_cases = get_new_cases(data)
    reported_date = get_reported_date(data)
    is_fresh = is_data_fresh(reported_date)
    region = "Ontario"

    message = "Could not retrieve info.   Please try again later"
    
    if is_fresh:
        message = f'<speak>{region} is reporting <say-as interpret-as=\"cardinal\">{new_cases}</say-as> new cases today.</speak>'
    else:
        message = f'<speak>{region} reported <say-as interpret-as=\"cardinal\">{new_cases}</say-as> new cases yesterday. Please check again later for today\'s numbers.</speak>'

    output_format = event['queryStringParameters']['format'] if event['queryStringParameters'] is not None else 'default'
    output = format_output(output_format, new_cases, reported_date, is_fresh, region, message)

    return {
        "statusCode": 200,
        "body": json.dumps(output),
    }
