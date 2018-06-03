import unittest
from .constructURL import *

class validLatLonTest(unittest.TestCase):

    def test_valid_latitude(self):
        self.lat = 0
        self.assertTrue(validLatLon(lat=self.lat))

    def test_valid_longitude(self):
        self.lon = 0
        self.assertTrue(validLatLon(lon=self.lon))

    def test_valid_latitude_longitude_combo(self):
        self.lat = 0
        self.lon = 0
        self.assertTrue(validLatLon(lat=self.lat, lon=self.lon))

    def test_invalid_latitude(self):
        self.lat = 200
        self.assertFalse(validLatLon(lat=self.lat),"returns True for invalid latitude above upper bound")
        self.lat = -200
        self.assertFalse(validLatLon(lat=self.lat),"returns True for invalid latitude below lower bound")

    def test_invalid_longitude(self):
        self.lon = 200
        self.assertFalse(validLatLon(lon=self.lon),"returns True for invalid longitude above upper bound")
        self.lon = -200
        self.assertFalse(validLatLon(lon=self.lon),"returns True for invalid longitude below lower bound")

    def test_valid_latitude_longitude_combo(self):
        self.lat = 0
        self.lon = 0
        self.assertTrue(validLatLon(lat=self.lat, lon=self.lon))

    def test_valid_latitude_invalid_longitude_combo(self):
        self.lat = 0
        self.lon = 200
        self.assertFalse(validLatLon(lat=self.lat, lon=self.lon))

    def test_invalid_latitude_valid_longitude_combo(self):
        self.lat = 200
        self.lon = 0
        self.assertFalse(validLatLon(lat=self.lat, lon=self.lon))

    def test_invalid_latitude_invalid_longitude_combo(self):
        self.lat = 200
        self.lon = 200
        self.assertFalse(validLatLon(lat=self.lat, lon=self.lon))


# if __name__ == '__main__':
#     unittest.main()
