"""
Tests for EnvironmentDriver
"""
from __future__ import division
from __future__ import unicode_literals

import unittest
from datmo.core.controller.environment.driver import EnvironmentDriver


class TestEnvironmentDriver(unittest.TestCase):

    def test_init(self):
        failed = False
        try:
            self.environment_driver = EnvironmentDriver()
        except TypeError:
            failed = True
        assert failed