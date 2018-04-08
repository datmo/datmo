"""
Tests for Datmo Project
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from ..util import get_class_contructor

class TestModuleLoader():
    def test_loader(self):
        constructor = get_class_contructor('datmo.util.class_stub.ClassStub')
        loaded = constructor(**{"name": "this"})
        assert loaded.name == "this"
        assert loaded.alpha is None

    def test_loader_params(self):
        constructor = get_class_contructor('datmo.util.class_stub.ClassStub')
        loaded = constructor(**{"name": "this", "alpha": 0})
        assert loaded.alpha == 0
