import pandas
from datetime import datetime, timedelta

class CaseInfo:
    _ONTARIO_COVID_RESULTS_URL = "https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv"

    def __init__(self, region):
        self.region = region

    def fill(self):
        data = self._read_data(self._ONTARIO_COVID_RESULTS_URL)
        self.reported_date = self._get_reported_date(data)
        self.new_cases = self._get_new_cases(data)
        self.message = ""
        return self
    
    def _read_data(self, url):
        return pandas.read_csv(url)

    def _get_reported_date(self, data):
        reported_date = data['Reported Date'].iat[-1]
        return datetime.strptime(reported_date, '%Y-%m-%d')

    def _get_new_cases(self, data):
        today_cases = data['Total Cases'].iat[-1]
        yesterday_cases = data['Total Cases'].iat[-2]
        new_cases = today_cases - yesterday_cases
        return "{:.0f}".format(new_cases)

    def is_stale(self):
        return not (datetime.today().date() == self.reported_date.date() and datetime.today() >= self.reported_date)

    def set_messsage(self, message):
        self.message = message