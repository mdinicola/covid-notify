import csv
import requests
import statistics
from http import HTTPStatus
from datetime import datetime
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
        self.weekly_average_cases = self._get_average_cases(data, 7)
        self.new_icu = self._get_new_icu(data)
        self.weekly_average_icu = self._get_average_icu(data, 7)
        self.is_stale = self._is_stale()
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
        value = float(data[-1]['Total Cases']) - float(data[-2]['Total Cases'])
        return "{:.0f}".format(value)      

    def _get_average_cases(self, data, interval_days):
        values = []
        for x in range(1, interval_days + 1):
            daily_delta = float(data[x * -1]['Total Cases']) - float(data[(x + 1) * -1]['Total Cases'])
            values.append(daily_delta)
        return "{:.0f}".format(statistics.mean(values))

    def _get_new_icu(self, data):
        value = float(data[-1]['Number of patients in ICU due to COVID-19'])
        return "{:.0f}".format(value)

    def _get_average_icu(self, data, interval_days):
        values = []
        for x in range(1, interval_days + 1):
            values.append(float(data[x * -1]['Number of patients in ICU due to COVID-19']))
        return "{:.0f}".format(statistics.mean(values))

    def _is_stale(self):
        today = datetime.now(self._eastern_timezone).replace(hour=0,minute=0,second=0,microsecond=0)
        return (today > self.reported_date)

    def format_message(self, speak = False):
        message = ""
        message_open = message_close = number_open = number_close = message_pause = ""
        message_day = "Today"

        if speak:
            message_open = '<speak>'
            message_close = '</speak>'
            number_open = '<say-as interpret-as=\"cardinal\">'
            number_close = '</say-as>'
            message_pause = '<break time=\"1\" />'

        if self.is_stale:
            message_day = "Yesterday"

        message = f'{message_open}{message_day} in {self.region}: {number_open}{self.new_cases}{number_close} new cases, weekly average {number_open}{self.weekly_average_cases}{number_close};{message_pause} in ICU: {number_open}{self.new_icu}{number_close}, weekly average {number_open}{self.weekly_average_icu}{number_close}{message_close}'

        return message

class CaseInfoEncoder(JSONEncoder):
    def default(self, o):
        output = {}
        output['newCases'] = o.new_cases
        output['weeklyAverageCases'] = o.weekly_average_cases
        output['newICU'] = o.new_icu
        output['weeklyAverageICU'] = o.weekly_average_icu
        output['reportedDate'] = o.reported_date.strftime('%Y-%m-%d')
        output['isStale'] = o.is_stale
        output['region'] = o.region
        output['message'] = o.message
        return output