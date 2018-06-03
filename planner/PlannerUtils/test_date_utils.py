import unittest
from datetime import datetime
from .date_utils import *

class test_ISO_to_datetime(unittest.TestCase):

    def setUp(self):
        # NOAA date string format
        self.test_ISO = "2018-06-02T18:00:00-05:00"
        self.year = 2018
        self.month = 6
        self.day = 2
        self.hour = 18
        self.minute = 0
        self.second = 0

    def convert_valid_ISO_date_string(self):
        self.assertIsInstance(ISO_to_datetime(self.test_ISO), datetime)

    def test_correct_year(self):
        dt = ISO_to_datetime(self.test_ISO)
        self.assertEqual(dt.year, self.year)

    def test_correct_month(self):
        dt = ISO_to_datetime(self.test_ISO)
        self.assertEqual(dt.month, self.month)

    def test_correct_day(self):
        dt = ISO_to_datetime(self.test_ISO)
        self.assertEqual(dt.day, self.day)

    def test_correct_hour(self):
        dt = ISO_to_datetime(self.test_ISO)
        self.assertEqual(dt.hour, self.hour)

    def test_correct_minute(self):
        dt = ISO_to_datetime(self.test_ISO)
        self.assertEqual(dt.minute, self.minute)

    def test_correct_second(self):
        dt = ISO_to_datetime(self.test_ISO)
        self.assertEqual(dt.second, self.second)
