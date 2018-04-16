"""
Tests for FileDriver
"""
from __future__ import division
from __future__ import unicode_literals

import unittest
from datmo.controller.file.driver import FileDriver


class TestFileDriver(unittest.TestCase):

    def test_init(self):
        try:
            self.file_driver = FileDriver()
        except TypeError:
            assert True