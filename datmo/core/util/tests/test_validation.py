"""
Tests for file_storage.py
"""
try:
    to_unicode = str
except NameError:
    to_unicode = str

from datmo.core.util.validation import validate
from datmo.core.util.exceptions import ValidationFailed, ValidationSchemaMissing

class TestJSONStore():
    def test_validate_success(self):
        assert validate("create_project", {
            "name": "foobar",
            "description": "barbaz"
        })

    def test_validate_fail(self):
        failed = False
        try:
            validate("create_project", {"name": 3})
        except ValidationFailed as e:
            failed = True
            assert e.errors
            assert isinstance(e.errors, dict)
        assert failed

    def test_invalid_scheme(self):
        failed = False
        try:
            validate("invalid_schema", {"name": "foobar"})
        except ValidationSchemaMissing as e:
            failed = True
        assert failed
