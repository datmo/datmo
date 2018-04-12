"""
Tests for Datmo Project
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datmo.util import get_class_contructor


class TestModuleLoader():
    def test_loader(self):
        constructor = get_class_contructor('datmo.util.exceptions.InvalidProjectPathException')
        loaded = constructor()
        assert loaded