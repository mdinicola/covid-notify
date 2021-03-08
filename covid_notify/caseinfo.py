import csv
import json
import requests
from http import HTTPStatus
from datetime import datetime, timedelta
from pytz import timezone
from json import JSONEncoder


class CaseInfo:
    _ONTARIO_COVID_RESULTS_URL = "https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv"
    _eastern_timezone = timezone('Canada/Eastern')

    def __init__(self, region):
        self.region = region

    def fill(self, speak = False):
        data = self._read_data(self._ONTARIO_COVID_RESULTS_URL)
        self.reported_date = self._get_reported_date(data)
        self.new_cases = self._get_new_cases(data)
        self.message = self.format_message(speak)
        return self
    
    def _read_data(self, url):
        response = requests.get(url)
        if response.status_code != HTTPStatus.OK:
            print('Downloading file failed with status: ', response.status_code)
            raise Exception("Request failed")

        csvfile = csv.DictReader(response.text.strip().split('\n'))
        data = list(csvfile)
        return data

    def _get_reported_date(self, data):
        reported_date = data[-1]['Reported Date']
        return self._eastern_timezone.localize(datetime.strptime(reported_date, '%Y-%m-%d'))

    def _get_new_cases(self, data):
        today_cases = float(data[-1]['Total Cases'])
        yesterday_cases = float(data[-2]['Total Cases'])
        new_cases = today_cases - yesterday_cases
        return "{:.0f}".format(new_cases)

    def _is_stale(self):
        today = datetime.now(self._eastern_timezone).replace(hour=0,minute=0,second=0,microsecond=0)
        return (today > self.reported_date)

    def format_message(self, speak = False):
        message = ""
        message_open = message_close = number_open = number_close = ""

        if speak:
            message_open = '<speak>'
            message_close = '</speak>'
            number_open = '<say-as interpret-as=\"cardinal\">'
            number_close = '</say-as>'

        if self.is_stale():
            message = f'{message_open}{self.region} reported {number_open}{self.new_cases}{number_close} new cases yesterday{message_close}'
        else:
            message = f'{message_open}{self.region} is reporting {number_open}{self.new_cases}{number_close} new cases today{message_close}'

        return message

class CaseInfoEncoder(JSONEncoder):
    def default(self, o):
        output = {}
        output['newCases'] = o.new_cases
        output['reportedDate'] = o.reported_date.strftime('%Y-%m-%d')
        output['isStale'] = o.is_stale()
        output['region'] = o.region
        output['message'] = o.message
        return output