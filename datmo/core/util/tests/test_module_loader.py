"""
Tests for __init__.py
"""

from datmo.core.util import get_class_contructor

class TestModuleLoader():
    def test_loader(self):
        constructor = get_class_contructor(
            'datmo.core.util.exceptions.InvalidProjectPath')
        loaded = constructor()
        assert loaded
