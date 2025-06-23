#!/usr/bin/python
"""
Tests for logger.py
"""
import os
import uuid
import tempfile
import platform
from time import sleep
from datmo.core.util.logger import DatmoLogger

class TestLogger():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # Delete previous singletons for logger if present
        if hasattr(DatmoLogger, "instance"):
            del DatmoLogger.instance
        DatmoLogger(dirpath=self.temp_dir)

    def test_logger(self):
        logger = DatmoLogger.get_logger()
        random_text = str(uuid.uuid1())
        logger.warning(random_text)
        logger.error("WHAT?")
        assert logger.level == DatmoLogger(dirpath=self.temp_dir).logging_level

    def test_datmo_logger_get_logfiles(self):
        files = DatmoLogger.get_logfiles()
        assert len(list(files)) > 0
        for f in files:
            assert DatmoLogger(dirpath=self.temp_dir).logging_path in f

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
        logpath = os.path.join(self.temp_dir, ".datmo", "logs", "log.txt")
        assert os.path.isfile(logpath)

    def test_multiple_loggers(self):
        l1 = DatmoLogger.get_logger("logger1")
        l2 = DatmoLogger.get_logger("logger2")
        l1.info("pizza")
        l2.info("party")
        assert len(DatmoLogger.find_text_in_logs("pizza")) == 1
        assert len(DatmoLogger.find_text_in_logs("logger2")) == 1
        logpath = os.path.join(self.temp_dir, ".datmo", "logs", "log.txt")
        assert os.path.isfile(logpath)

    def test_multiple_log_files(self):
        random_name_1 = str(uuid.uuid1())
        random_name_2 = str(uuid.uuid1())
        l1 = DatmoLogger.get_logger("logger3", random_name_1)
        l2 = DatmoLogger.get_logger("logger3", random_name_2)
        l1.info("green")
        l2.info("purple")
        r = DatmoLogger.find_text_in_logs("green")
        assert len(r) == 1
        assert r[0]["file"].find(random_name_1)
        r = DatmoLogger.find_text_in_logs("purple")
        assert len(r) == 1
        assert r[0]["file"].find(random_name_2)
        logpath = os.path.join(self.temp_dir, ".datmo", "logs", random_name_1)
        assert os.path.isfile(logpath)
        logpath = os.path.join(self.temp_dir, ".datmo", "logs", random_name_2)
        assert os.path.isfile(logpath)

    def test_new_logger_and_default(self):
        random_name = str(uuid.uuid1())
        logger = DatmoLogger.get_logger("logger3", random_name)
        logger.info("testing")
        assert len(DatmoLogger.find_text_in_logs("testing")) == 1
        default_logger = DatmoLogger.get_logger()
        default_logger.info("default-logger")
        assert len(DatmoLogger.find_text_in_logs("default-logger")) == 1
        logpath = os.path.join(self.temp_dir, ".datmo", "logs", random_name)
        assert os.path.isfile(logpath)

    def test_timeit_decorator(self):
        # NOTE:  If this test is failing be sure to add
        # LOGGING_LEVEL=DEBUG before pytest
        # or add as an environment variable
        @DatmoLogger.timeit
        def slow_fn():
            sleep(1)

        slow_fn()
        assert len(DatmoLogger.find_text_in_logs("slow_fn")) >= 1
        logpath = os.path.join(self.temp_dir, ".datmo", "logs", "timers.log")
        assert os.path.isfile(logpath)
