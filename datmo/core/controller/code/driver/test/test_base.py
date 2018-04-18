"""
Tests for CodeDriver
"""
from __future__ import division
from __future__ import unicode_literals

import unittest
from datmo.core.controller.code.driver import CodeDriver


class TestCodeDriver(unittest.TestCase):

    def test_init(self):
        try:
            self.code_driver = CodeDriver()
        except TypeError:
            assert True