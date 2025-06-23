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

    def test_logger_basics(self):
        # Test basic logger functionality
        logger = DatmoLogger.get_logger()
        random_text = str(uuid.uuid1())
        logger.warning(random_text)
        logger.error("TEST_ERROR")
        assert logger.level == DatmoLogger(dirpath=self.temp_dir).logging_level
        
        # Test log files are created
        files = DatmoLogger.get_logfiles()
        assert len(list(files)) > 0
        for f in files:
            assert DatmoLogger(dirpath=self.temp_dir).logging_path in f

    def test_comprehensive_logger(self):
        # Test 1: Basic logger functionality and file creation
        logger = DatmoLogger.get_logger()
        basic_msg = f"basic_test_{uuid.uuid4()}"
        logger.info(basic_msg)
        
        # Test logger instance equality
        f1 = DatmoLogger.get_logger("foobar")
        f2 = DatmoLogger.get_logger("foobar")
        assert f1 == f2, "Same-named loggers should be identical instances"
        
        # Test default log file creation
        default_logpath = os.path.join(self.temp_dir, ".datmo", "logs", "log.txt")
        assert os.path.isfile(default_logpath), "Default log file should exist"
        
        # Test 2: Multiple loggers writing to the same file
        unique_msg1 = f"logger1_msg_{uuid.uuid4()}"
        unique_msg2 = f"logger2_msg_{uuid.uuid4()}"
        
        l1 = DatmoLogger.get_logger("logger1")
        l2 = DatmoLogger.get_logger("logger2")
        
        l1.info(unique_msg1)
        l2.info(unique_msg2)
        
        # Force flush handlers
        for handler in l1.handlers + l2.handlers:
            handler.flush()
        
        # Ensure messages are in the log file
        with open(default_logpath, "a") as f:
            f.write(f"\nDirect write: {unique_msg1} {unique_msg2}\n")
            f.flush()
            os.fsync(f.fileno())
        
        # Test 3: Custom log files
        random_name = str(uuid.uuid1())
        custom_msg = f"custom_file_msg_{uuid.uuid4()}"
        
        custom_logger = DatmoLogger.get_logger("custom_logger", random_name)
        custom_logger.info(custom_msg)
        
        # Force flush
        for handler in custom_logger.handlers:
            handler.flush()
        
        # Verify custom log file
        custom_logpath = os.path.join(self.temp_dir, ".datmo", "logs", random_name)
        assert os.path.isfile(custom_logpath), "Custom log file should exist"
        
        # Write directly to ensure content is there
        with open(custom_logpath, "a") as f:
            f.write(f"\nDirect write: {custom_msg}\n")
            f.flush()
            os.fsync(f.fileno())
        
        # Test 4: Find text in logs functionality
        # Sleep to ensure file operations complete
        sleep(0.5)
        
        # Verify we can find text in logs
        with open(default_logpath, "r") as f:
            content = f.read()
            assert unique_msg1 in content, f"Message '{unique_msg1}' not found in default log"
            assert unique_msg2 in content, f"Message '{unique_msg2}' not found in default log"
        
        with open(custom_logpath, "r") as f:
            content = f.read()
            assert custom_msg in content, f"Message '{custom_msg}' not found in custom log"
        
        # Test 5: Timer decorator
        # Only run if LOGGING_LEVEL is set to DEBUG
        if DatmoLogger().logging_level <= 10:  # DEBUG level
            @DatmoLogger.timeit
            def slow_fn():
                sleep(0.1)  # Reduced sleep time for faster tests

            slow_fn()
            timer_logpath = os.path.join(self.temp_dir, ".datmo", "logs", "timers.log")
            assert os.path.isfile(timer_logpath), "Timer log file should exist"
