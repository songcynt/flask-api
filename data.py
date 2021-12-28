"""Data storage class"""

from os.path import abspath
import pandas
from pathlib import Path
import os

_VALID_DATES_FILEPATH = 'data/valid_dates.txt'
_TIMESERIES_DATA_FILEPATH = 'data/test_timeseries_report.csv'
_DAILY_REPORT_DATA_FILEPATH = 'data/test_daily_report.csv'

DATA_FILEPATH = 'data/data.pkl'


class MockData:
    def __init__(self):
        self.valid_dates = None
        self.timeseries_data = None
        self.daily_report_data = None

    def get_valid_dates(self):
        """Returns dates columns in a valid timeseries data csv

        Returns:
            list
        """
        if not self.valid_dates:
            with open(abspath(_VALID_DATES_FILEPATH), 'r') as file:
                self.valid_dates = file.readline().strip().split(',')
        return self.valid_dates

    def get_timeseries_data(self):
        """Returns mock timeseries data

        Returns:
            pandas.DataFrame
        """
        if not self.timeseries_data:
            self.timeseries_data = pandas.read_csv(_TIMESERIES_DATA_FILEPATH)
        return self.timeseries_data

    def get_daily_report_data(self):
        """Returns mock daily report data

        Returns:
            pandas.DataFrame
        """
        if not self.daily_report_data:
            self.daily_report_data = pandas.read_csv(
                _DAILY_REPORT_DATA_FILEPATH)
        return self.daily_report_data


class ReportData:
    def __init__(self):
        self.df = None

    def update_data(self, df):
        self.df = df
        self.df.to_pickle(abspath(DATA_FILEPATH))

    def get_data(self):
        if self.df is None:
            try:
                self.df = pandas.read_pickle(abspath(DATA_FILEPATH))
            except FileNotFoundError:
                self.df = None

        return self.df


def clear_data_storage():
    filepath = abspath(DATA_FILEPATH)
    if Path(filepath).is_file():
        os.remove(abspath(DATA_FILEPATH))
