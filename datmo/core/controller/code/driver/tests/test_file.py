"""
Tests for file.py
"""
from __future__ import division
from __future__ import unicode_literals

import os
import shutil
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.code.driver.file import FileCodeDriver
from datmo.core.util.exceptions import PathDoesNotExist


class TestFileCodeDriver():
    """
    Checks all functions of the FileCodeDriver
    """

    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.file_code_manager = FileCodeDriver(filepath=self.temp_dir)

    def teardown_method(self):
        pass

    def test_instantiation(self):
        assert self.file_code_manager != None

    def test_instantiation_fail_dne(self):
        failed = False
        try:
            _ = FileCodeDriver(filepath="nonexistant_path")
        except PathDoesNotExist:
            failed = True
        assert failed

    def test_init(self):
        result = self.file_code_manager.init()
        assert result and \
               self.file_code_manager.is_initialized == True

    def test_init_then_instantiation(self):
        self.file_code_manager.init()
        another_file_code_manager = FileCodeDriver(filepath=self.temp_dir)
        result = another_file_code_manager.is_initialized
        assert result == True

    def test_tracked_files(self):
        self.file_code_manager.init()
        with open(os.path.join(self.temp_dir, "test.txt"), "w") as f:
            f.write("hello")
        os.makedirs(os.path.join(self.temp_dir, "datmo_environment/"))
        with open(
                os.path.join(self.temp_dir, "datmo_environment", "test"),
                "w") as f:
            f.write("cool")
        os.makedirs(os.path.join(self.temp_dir, "datmo_files/"))
        with open(os.path.join(self.temp_dir, "datmo_files", "test"),
                  "w") as f:
            f.write("man")

        # Test if catches file (no .datmoignore)
        result = self.file_code_manager._tracked_files()
        assert result == ["test.txt"]

        # Test if catches multiple files (no .datmoignore)
        with open(os.path.join(self.temp_dir, "test2.txt"), "w") as f:
            f.write("hello")
        result = self.file_code_manager._tracked_files()
        for item in result:
            assert item in ["test.txt", "test2.txt"]

        # Test if ignores one file and only shows one
        with open(os.path.join(self.temp_dir, ".datmoignore"), "w") as f:
            f.write("test.txt")
        result = self.file_code_manager._tracked_files()
        assert result == ["test2.txt"]
