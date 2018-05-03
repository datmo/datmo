
"""
Tests for logger.py
"""
import logging
import tempfile
import shutil
import os
from datmo.core.util.logger import DatmoLogger
from datmo.core.controller.project import ProjectController

class TestLogger():
    def test_global_logger_configure(self):
        self.temp_dir = tempfile.mkdtemp()
        global_logger = DatmoLogger.configure(self.temp_dir, 10)
        assert global_logger.logging_level == 10
        assert global_logger.logging_path == self.temp_dir

    def test_logger(self):
        logger = DatmoLogger.get_logger()
        logger.info("testing")
        logger.error("WHAT?")
        assert logger.level == DatmoLogger().logging_level

    def test_datmo_logger_get_logfiles(self):
        files = DatmoLogger.get_logfiles()
        assert len(files) > 0
        for f in files:
            assert DatmoLogger().logging_path in f

    def test_find_text_in_logs(self):
        logger = DatmoLogger.get_logger()
        logger.info("can you find this")
        results = DatmoLogger.find_text_in_logs("can you find this")
        assert len(results) == 1
        for r in results:
            assert r["file"]
            assert r["line_number"]
            assert r["line"]

    def test_get_logger_should_return_same_logger(self):
        f = DatmoLogger.get_logger("foobar")
        f2 = DatmoLogger.get_logger("foobar")
        assert f == f2

    def test_multiple_loggers(self):
        l1 = DatmoLogger.get_logger("logger1")
        l2 = DatmoLogger.get_logger("logger2")
        l1.info("pizza")
        l2.info("party")
        assert len(DatmoLogger.find_text_in_logs("pizza")) == 1
        assert len(DatmoLogger.find_text_in_logs("logger2")) == 1

    def test_multiple_log_files(self):
        l1 = DatmoLogger.get_logger("logger3","debug.txt")
        l2 = DatmoLogger.get_logger("logger3","info.txt")
        l1.info("green")
        l2.info("purple")
        r = DatmoLogger.find_text_in_logs("green")
        assert len(r) == 1
        assert r[0]["file"].find("debug.txt")
        r = DatmoLogger.find_text_in_logs("purple")
        assert len(r) == 1
        assert r[0]["file"].find("info.txt")





