"""
Tests for i18n
"""

from datmo.core.util.i18n import get

class Testi18n():
    def test_get(self):
        msg = get("info", "cli.general.line")
        assert msg == '=============================================================='

    def test_get_dict(self):
        msg = get("info", "cli.general.dict.test", {
            "foo": "hello",
            "bar": "world"
        })
        assert msg == "hello - world"

    def test_get_string(self):
        msg = get("info", "cli.general.str.test", "disco")
        assert msg == "disco"

    def test_get_tuple(self):
        msg = get("info", "cli.general.tuple.test", ("disco", "inferno"))
        assert msg == "disco, inferno"
