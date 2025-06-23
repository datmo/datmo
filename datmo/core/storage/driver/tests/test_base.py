"""
Tests for DALDriver
"""

import unittest
from datmo.core.storage.driver import DALDriver

class TestDALDriver(unittest.TestCase):
    def test_init(self):
        failed = False
        try:
            self.dal_driver = DALDriver()
        except TypeError:
            failed = True
        assert failed
