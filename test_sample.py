"""Sample Python test file.

Run with either:
    python -m pytest test_sample.py
    python -m unittest test_sample.py
"""

import unittest


def add(a, b):
    return a + b


def is_even(n):
    return n % 2 == 0


class TestSample(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)

    def test_is_even(self):
        self.assertTrue(is_even(4))
        self.assertFalse(is_even(7))

    def test_string_upper(self):
        self.assertEqual("headroom".upper(), "HEADROOM")


if __name__ == "__main__":
    unittest.main()
