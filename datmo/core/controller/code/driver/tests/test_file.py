"""
Tests for file.py
"""
from __future__ import division
from __future__ import unicode_literals

import os
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.code.driver.file import FileCodeDriver
from datmo.core.util.misc_functions import list_all_filepaths, get_filehash
from datmo.core.util.exceptions import PathDoesNotExist, FileIOError, UnstagedChanges


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

    def __setup(self):
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

    def test_tracked_files(self):
        self.__setup()
        # Test if catches file (no .datmoignore)
        result = self.file_code_manager._get_tracked_files()
        assert result == ["test.txt"]

        # Test if catches multiple files (no .datmoignore)
        with open(os.path.join(self.temp_dir, "test2.txt"), "w") as f:
            f.write("hello")
        result = self.file_code_manager._get_tracked_files()
        for item in result:
            assert item in ["test.txt", "test2.txt"]

        # Test if it ignores any .datmo directory or files within
        with open(os.path.join(self.temp_dir, ".datmo", "test"), "w") as f:
            f.write("cool")
        result = self.file_code_manager._get_tracked_files()
        for item in result:
            assert ".datmo" not in item
            assert item in ["test.txt", "test2.txt"]

        # Test if ignores one file and only shows one
        with open(os.path.join(self.temp_dir, ".datmoignore"), "w") as f:
            f.write("test.txt")
        result = self.file_code_manager._get_tracked_files()
        assert result == ["test2.txt"]

    def test_calculate_commit_hash(self):
        self.__setup()
        # Test if the hash matches the test file
        tracked_filepaths = self.file_code_manager._get_tracked_files()
        result = self.file_code_manager._calculate_commit_hash(
            tracked_filepaths)
        temp_dir_path = os.path.join(
            self.file_code_manager._code_filepath,
            os.listdir(self.file_code_manager._code_filepath)[0])
        # Assert temp directory was created and populated correctly
        for item in list_all_filepaths(temp_dir_path):
            assert item in tracked_filepaths
        # Assert the correct commit hash was returned
        assert result == "69a329523ce1ec88bf63061863d9cb14"

    def test_create_ref(self):
        self.__setup()
        # Test successful creation of ref
        result = self.file_code_manager.create_ref()
        assert result == "69a329523ce1ec88bf63061863d9cb14"
        # Assert the commit file was added in the correct place
        commit_filepath = os.path.join(self.file_code_manager._code_filepath,
                                       result)
        assert os.path.isfile(commit_filepath)
        # Assert only the tracked files were added in the correct locations
        tracked_filepaths = self.file_code_manager._get_tracked_files()
        for tracked_filepath in tracked_filepaths:
            absolute_dirpath = os.path.join(
                self.file_code_manager._code_filepath, tracked_filepath)
            assert os.path.isdir(absolute_dirpath)
            assert len(os.listdir(absolute_dirpath)) == 1
            file_line_str = tracked_filepath + "," + os.listdir(
                absolute_dirpath)[0]
            assert file_line_str in open(commit_filepath).read()

    def test_exists_ref(self):
        self.__setup()
        commit_hash = "69a329523ce1ec88bf63061863d9cb14"
        # Test does not exist case
        result = self.file_code_manager.exists_ref(commit_id=commit_hash)
        assert result == False
        # Test exists case
        commit_hash = self.file_code_manager.create_ref()
        result = self.file_code_manager.exists_ref(commit_id=commit_hash)
        assert result == True

    def test_delete_ref(self):
        self.__setup()
        commit_hash = "69a329523ce1ec88bf63061863d9cb14"
        # Test trying to delete failure
        failed = False
        try:
            self.file_code_manager.delete_ref(commit_id=commit_hash)
        except FileIOError:
            failed = True
        assert failed
        # Test successful deletion
        commit_hash = self.file_code_manager.create_ref()
        result = self.file_code_manager.delete_ref(commit_id=commit_hash)
        assert result
        commit_filepath = os.path.join(self.file_code_manager._code_filepath,
                                       commit_hash)
        assert not os.path.isfile(commit_filepath)

    def test_list_refs(self):
        self.__setup()
        # Test no commits
        result = self.file_code_manager.list_refs()
        assert result == []
        # Test 1 commit
        commit_hash = self.file_code_manager.create_ref()
        result = self.file_code_manager.list_refs()
        assert result == [commit_hash]

    def test_checkout_ref(self):
        self.__setup()
        commit_hash = "69a329523ce1ec88bf63061863d9cb14"
        # Test trying to checkout failure (commit does not exist)
        failed = False
        try:
            self.file_code_manager.checkout_ref(commit_id=commit_hash)
        except FileIOError:
            failed = True
        assert failed
        # Test successful checkout (same commit as current, no changes)
        commit_hash = self.file_code_manager.create_ref()
        result = self.file_code_manager.checkout_ref(commit_id=commit_hash)
        assert result
        # Test trying to checkout failure (unstaged changes)
        with open(os.path.join(self.temp_dir, "test2.txt"), "w") as f:
            f.write("hello")
        failed = False
        try:
            self.file_code_manager.checkout_ref(commit_id=commit_hash)
        except UnstagedChanges:
            failed = True
        assert failed
        # Test successful checkout with new commit (files back to old commit)
        _ = self.file_code_manager.create_ref()
        result = self.file_code_manager.checkout_ref(commit_id=commit_hash)
        assert result
        commit_filepath = os.path.join(self.file_code_manager._code_filepath,
                                       commit_hash)
        # Check all files in commit file exist and are at the correct point
        with open(commit_filepath, "r") as f:
            for line in f:
                tracked_filepath, filehash = line.rstrip().split(",")
                destination_absolute_filepath = os.path.join(
                    self.file_code_manager.filepath, tracked_filepath)
                assert os.path.isfile(destination_absolute_filepath)
                assert filehash == get_filehash(destination_absolute_filepath)
        # Check that files in the latest commit are not present
        assert not os.path.isfile(os.path.join(self.temp_dir, "test2.txt"))
