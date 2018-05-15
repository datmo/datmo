#!/usr/bin/python
"""
Tests for logger.py
"""
import os
import uuid
from time import sleep
from datmo.core.util.logger import DatmoLogger


class TestLogger():
    def test_logger(self):
        logger = DatmoLogger.get_logger()
        logger.warning("some_other_test")
        logger.error("WHAT?")
        assert logger.level == DatmoLogger().logging_level

    def test_datmo_logger_get_logfiles(self):
        files = DatmoLogger.get_logfiles()
        assert len(list(files)) > 0
        for f in files:
            assert DatmoLogger().logging_path in f
        # teardown logger created in previous test_logger function
        os.remove(
            os.path.join(os.path.expanduser("~"), ".datmo", "logs", "log.txt"))

    def test_find_text_in_logs(self):
        logger = DatmoLogger.get_logger()
        logger.info("can you find this")
        results = DatmoLogger.find_text_in_logs("can you find this")
        assert len(results) == 1
        for r in results:
            assert r["file"]
            assert r["line_number"]
            assert r["line"]
        # teardown
        os.remove(
            os.path.join(os.path.expanduser("~"), ".datmo", "logs", "log.txt"))

    def test_get_logger_should_return_same_logger(self):
        f = DatmoLogger.get_logger("foobar")
        f2 = DatmoLogger.get_logger("foobar")
        assert f == f2
        # teardown
        os.remove(
            os.path.join(os.path.expanduser("~"), ".datmo", "logs", "log.txt"))

    def test_multiple_loggers(self):
        l1 = DatmoLogger.get_logger("logger1")
        l2 = DatmoLogger.get_logger("logger2")
        l1.info("pizza")
        l2.info("party")
        assert len(DatmoLogger.find_text_in_logs("pizza")) == 1
        assert len(DatmoLogger.find_text_in_logs("logger2")) == 1
        # teardown
        os.remove(
            os.path.join(os.path.expanduser("~"), ".datmo", "logs", "log.txt"))

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
        # teardown
        os.remove(
            os.path.join(
                os.path.expanduser("~"), ".datmo", "logs", random_name_1))
        os.remove(
            os.path.join(
                os.path.expanduser("~"), ".datmo", "logs", random_name_2))

    def test_new_logger_and_default(self):
        random_name = str(uuid.uuid1())
        logger = DatmoLogger.get_logger("logger3", random_name)
        logger.info("testing")
        assert len(DatmoLogger.find_text_in_logs("testing")) == 1
        default_logger = DatmoLogger.get_logger()
        default_logger.info("default-logger")
        assert len(DatmoLogger.find_text_in_logs("default-logger")) == 1
        # teardown
        os.remove(
            os.path.join(
                os.path.expanduser("~"), ".datmo", "logs", random_name))

    def test_timeit_decorator(self):
        # NOTE:  If this test is failing be sure to add
        # LOGGING_LEVEL=DEBUG before pytest
        # or add as an environment variable
        @DatmoLogger.timeit
        def slow_fn():
            sleep(1)

        slow_fn()
        assert len(DatmoLogger.find_text_in_logs("slow_fn")) >= 1
        # teardown
        os.remove(
            os.path.join(
                os.path.expanduser("~"), ".datmo", "logs", "timers.log"))
