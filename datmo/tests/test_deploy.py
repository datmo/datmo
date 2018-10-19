#!/usr/bin/python
"""
Tests for deploy module
"""
import os
import tempfile
import platform
from celery import Celery
try:
    basestring
except NameError:
    basestring = str

from datmo.deploy import Deploy


class TestDeployModule():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.deploy = Deploy()

    def teardown_class(self):
        pass

    def test_method(self):
        result = self.deploy.method()
        assert type(result) == type(Celery().task(
            bind=True, soft_time_limit=1000))
