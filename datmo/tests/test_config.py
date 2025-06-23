#!/usr/bin/python
"""
Tests for snapshot module
"""
import os
import tempfile
import platform
try:
    to_unicode = str
except NameError:
    to_unicode = str

from datmo.config import Config

class TestConfigModule():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_method(self):
        pass

    def test_config_singleton(self):
        c1 = Config()
        c2 = Config()
        assert c1 == c2
        c1.test = 'foo'
        assert c2.test == 'foo'

    def test_config_home_default(self):
        Config().set_home(os.getcwd())
