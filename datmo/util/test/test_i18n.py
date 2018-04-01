"""
Tests for i18n
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datmo.util.i18n import get

class Testi18n():

    def test_get(self):
        msg = get('general.line')
        assert msg == '=============================================================='

    def test_get_dict(self):
        msg = get('test.dict.replacements', {"foo":"hello", "bar":"world"})
        assert msg == "hello - world"

    def test_get_string(self):
        msg = get('general.echo.input', "disco")
        assert msg == "You entered: disco"

    def test_get_tuple(self):
        msg = get('test.tuple.replacements', ("disco", "inferno"))
        assert msg == "disco, inferno"
