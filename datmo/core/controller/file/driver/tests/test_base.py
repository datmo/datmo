"""
Tests for FileDriver
"""

import unittest
from datmo.core.controller.file.driver import FileDriver

class TestFileDriver(unittest.TestCase):
    def test_init(self):
        failed = False
        try:
            self.file_driver = FileDriver()
        except TypeError:
            failed = True
        assert failed
