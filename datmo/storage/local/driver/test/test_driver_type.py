"""
Tests for driver_type.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datmo.storage.local.driver.driver_type import DriverType


class TestDataDriverTypes():
    """
    Checks enum values for DriverTypes
    """

    def test_enum_values(self):
        assert len(DriverType) == 2
        assert DriverType.FILE == 0x01
        assert DriverType.SERVICE == 0x02
