"""
Tests for __init__.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datmo.core.util import get_class_contructor


class TestModuleLoader():
    def test_loader(self):
        constructor = get_class_contructor('datmo.core.util.exceptions.InvalidProjectPathException')
        loaded = constructor()
        assert loaded