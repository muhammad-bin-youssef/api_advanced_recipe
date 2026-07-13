from app import calc
from django.test import SimpleTestCase


class TestCalc(SimpleTestCase):
    def test_add(self):
        res = calc.sum(2, 5)
        self.assertEqual(res, 7)

    def test_mult(self):
        res = calc.mult(2, 5)
        self.assertEqual(res, 10)

