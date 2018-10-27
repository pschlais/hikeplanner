import unittest
from . import updateTable

class test_get_slice_indices(unittest.TestCase):

    def test_negative_length(self):
        length = -1
        self.assertRaises(ValueError, updateTable._get_slice_indices,
                          length, 5)

    def test_zero_length(self):
        length = 0
        self.assertRaises(ValueError, updateTable._get_slice_indices,
                          length, 5)

    def test_one_length(self):
        length = 1
        multiple = 5
        result = updateTable._get_slice_indices(length, multiple)
        self.assertEquals(result, [[0, length]])

    def test_length_less_than_multiple(self):
        length = 5
        multiple = 7
        result = updateTable._get_slice_indices(length, multiple)
        self.assertEquals(result, [[0, length]])

    def test_length_equals_multiple(self):
        length = 7
        multiple = 7
        result = updateTable._get_slice_indices(length, multiple)
        self.assertEquals(result, [[0, multiple]])

    def test_length_greater_than_multiple_unequal(self):
        # when length is not a multiple of "multiple"
        length = 19
        multiple = 7
        result = updateTable._get_slice_indices(length, multiple)
        self.assertEquals(result, [[0, 7], [7, 14], [14, 19]])

    def test_length_greater_than_multiple_clean(self):
        # when length is a multiple of "multiple"
        length = 21
        multiple = 7
        result = updateTable._get_slice_indices(length, multiple)
        self.assertEquals(result, [[0, 7], [7, 14], [14, 21]])
