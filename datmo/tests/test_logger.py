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

from datmo.logger import Logger

class TestLoggerModule():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.logger = Logger(task_dir=self.temp_dir)

    def teardown_method(self):
        pass

    def test_log_config(self):
        config = {'a': 1}
        saved_config = self.logger.log_config(config)
        assert saved_config == config

        config = {'b': 2}
        saved_config = self.logger.log_config(config)
        assert saved_config == {'a': 1, 'b': 2}

    def test_log_results(self):
        result = {'a': 1}
        saved_result = self.logger.log_result(result)
        assert saved_result == result

        result = {'b': 2}
        saved_result = self.logger.log_result(result)
        assert saved_result == {'a': 1, 'b': 2}
