"""
simple tests

"""

from django.test import SimpleTestCase

from app import calc


class calcTests(SimpleTestCase):
    """Test the calc module"""

    def test_add_numbers(self):
        """Test the addition function"""
        res = calc.add(2, 3)
        self.assertEqual(res, 5)

    def test_subtract_numbers(self):
        """Test the subtraction numbers"""
        res = calc.subtract(5, 3)
        self.assertEqual(res, 2)
