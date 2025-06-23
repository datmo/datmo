#!/usr/bin/python
"""
Tests for misc_functions.py
"""
import os
import tempfile
import platform
try:
    to_unicode = str
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.util.remote_api import RemoteAPI

class TestRemoteAPI():
    # TODO: Add more cases for each test
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if platform.system() != "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # TODO: move API key to environment variable
        self.remote_api = RemoteAPI(api_key="d41d8cd98f00b204e9800998ecf8427e")

    def test_post_data(self):
        pass

    def test_get_data(self):
        pass

    def test_update_actual(self):
        pass

    def test_get_deployment_info(self):
        pass
