"""
Tests for file.py
"""

import os
import time
import shutil
import tempfile
import platform
from io import open
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

from datmo.core.controller.code.driver.file import FileCodeDriver
from datmo.core.util.exceptions import PathDoesNotExist, FileIOError, CodeNotInitialized, UnstagedChanges, CommitDoesNotExist

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
        self.file_code_driver = FileCodeDriver(
            root=self.temp_dir, datmo_directory_name=".datmo")

    def teardown_method(self):
        pass

    def test_instantiation(self):
        assert self.file_code_driver != None

    def test_instantiation_fail_dne(self):
        failed = False
        try:
            _ = FileCodeDriver(
                root="nonexistant_path", datmo_directory_name=".datmo")
        except PathDoesNotExist:
            failed = True
        assert failed

    def test_is_initalized(self):
        # test if code manager is initialized
        self.file_code_driver.init()
        assert self.file_code_driver.is_initialized == True
        # test if code folder is removed from .datmo folder
        self._code_filepath = os.path.join(
            self.file_code_driver._datmo_directory_path, "code")
        shutil.rmtree(self._code_filepath)
        assert self.file_code_driver.is_initialized == False

    def test_init(self):
        result = self.file_code_driver.init()
        assert result and \
               self.file_code_driver.is_initialized == True

    def test_init_then_instantiation(self):
        self.file_code_driver.init()
        another_file_code_manager = FileCodeDriver(
            root=self.temp_dir, datmo_directory_name=".datmo")
        result = another_file_code_manager.is_initialized
        assert result == True

    def __setup(self):
        self.file_code_driver.init()
        with open(os.path.join(self.temp_dir, "test.txt"), "wb") as f:
            f.write(to_bytes("hello"))

    def test_tracked_files(self):
        self.__setup()
        # Test if catches file (no .datmoignore)
        result = self.file_code_driver._get_tracked_files()
        assert result == ["test.txt"]

        # Test if catches multiple files (no .datmoignore)
        with open(os.path.join(self.temp_dir, "test2.txt"), "wb") as f:
            f.write(to_bytes("hello"))
        result = self.file_code_driver._get_tracked_files()
        for item in result:
            assert item in ["test.txt", "test2.txt"]

        # Test if it ignores any .datmo directory or files within
        with open(
                os.path.join(self.file_code_driver._datmo_directory_path,
                             "test"), "wb") as f:
            f.write(to_bytes("cool"))
        result = self.file_code_driver._get_tracked_files()
        for item in result:
            assert os.path.join(self.file_code_driver._datmo_directory_name,
                                "test") not in item
            assert item in ["test.txt", "test2.txt"]

        # Test if it ignores any .git directory or files within
        os.makedirs(os.path.join(self.temp_dir, ".git"))
        with open(os.path.join(self.temp_dir, ".git", "test"), "wb") as f:
            f.write(to_bytes("cool"))
        result = self.file_code_driver._get_tracked_files()
        for item in result:
            assert os.path.join(".git", "test") not in item
            assert item in ["test.txt", "test2.txt"]

        # Test if ignores one file and only shows one
        with open(os.path.join(self.temp_dir, ".datmoignore"), "wb") as f:
            f.write(to_bytes("test.txt"))
        result = self.file_code_driver._get_tracked_files()
        assert result == ["test2.txt"]

    def test_calculate_commit_hash(self):
        self.__setup()
        # Test if the hash matches the test file
        tracked_filepaths = self.file_code_driver._get_tracked_files()
        result = self.file_code_driver._calculate_commit_hash(
            tracked_filepaths)
        # Assert the correct commit hash was returned
        assert result == "69a329523ce1ec88bf63061863d9cb14"

    def test_current_hash(self):
        self.__setup()
        # Test failure with UnstagedChanges
        failed = False
        try:
            self.file_code_driver.current_hash()
        except UnstagedChanges:
            failed = True
        assert failed
        # Test successful creation of ref
        current_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.current_hash()
        assert result == current_hash

    def test_create_ref(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        # Test failure, commit given does not exist
        self.file_code_driver.init()
        failed = False
        try:
            self.file_code_driver.create_ref(commit_id="random")
        except CommitDoesNotExist:
            failed = True
        assert failed
        # Test successful creation of ref
        self.__setup()
        result = self.file_code_driver.create_ref()
        assert result == "69a329523ce1ec88bf63061863d9cb14"
        # Assert the commit file was added in the correct place
        commit_filepath = os.path.join(self.file_code_driver._code_filepath,
                                       result)
        assert os.path.isfile(commit_filepath)
        # Assert only the tracked files were added in the correct locations
        tracked_filepaths = self.file_code_driver._get_tracked_files()
        for tracked_filepath in tracked_filepaths:
            absolute_dirpath = os.path.join(
                self.file_code_driver._code_filepath, tracked_filepath)
            assert os.path.isdir(absolute_dirpath)
            assert len(os.listdir(absolute_dirpath)) == 1
            file_line_str = tracked_filepath + "," + os.listdir(
                absolute_dirpath)[0]
            assert file_line_str in open(commit_filepath).read()

    def test_current_ref(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        # Test success (single commit)
        self.__setup()
        commit_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.current_ref()
        assert result == commit_hash
        # Test success (multiple commits)
        with open(os.path.join(self.temp_dir, "test2.txt"), "wb") as f:
            f.write(to_bytes("hello"))
        commit_hash_2 = self.file_code_driver.create_ref()
        result = self.file_code_driver.current_ref()
        assert commit_hash != commit_hash_2
        assert result == commit_hash_2
        # Test success after checkout
        self.file_code_driver.checkout_ref(commit_id=commit_hash)
        result = self.file_code_driver.current_ref()
        assert result == commit_hash

    def test_latest_ref(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        # Test success (single commit)
        self.__setup()
        commit_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.latest_ref()
        assert result == commit_hash
        # Test success (multiple commits)
        with open(os.path.join(self.temp_dir, "test2.txt"), "wb") as f:
            f.write(to_bytes("hello"))
        time.sleep(1)
        commit_hash_2 = self.file_code_driver.create_ref()
        result = self.file_code_driver.latest_ref()
        assert commit_hash != commit_hash_2
        assert result == commit_hash_2
        # Test success after checkout
        self.file_code_driver.checkout_ref(commit_id=commit_hash)
        result = self.file_code_driver.latest_ref()
        assert result == commit_hash_2

    def test_exists_ref(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        self.__setup()
        commit_hash = "69a329523ce1ec88bf63061863d9cb14"
        # Test does not exist case
        result = self.file_code_driver.exists_ref(commit_id=commit_hash)
        assert result == False
        # Test exists case
        commit_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.exists_ref(commit_id=commit_hash)
        assert result == True

    def test_delete_ref(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        self.__setup()
        commit_hash = "69a329523ce1ec88bf63061863d9cb14"
        # Test trying to delete failure
        failed = False
        try:
            self.file_code_driver.delete_ref(commit_id=commit_hash)
        except FileIOError:
            failed = True
        assert failed
        # Test successful deletion
        commit_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.delete_ref(commit_id=commit_hash)
        assert result
        commit_filepath = os.path.join(self.file_code_driver._code_filepath,
                                       commit_hash)
        assert not os.path.isfile(commit_filepath)

    def test_list_refs(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        self.__setup()
        # Test no commits
        result = self.file_code_driver.list_refs()
        assert result == []
        # Test 1 commit
        commit_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.list_refs()
        assert result == [commit_hash]

    def test_check_unstaged_changes(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        self.__setup()

        # Test for unstaged changes
        unstaged = False
        try:
            self.file_code_driver.check_unstaged_changes()
        except UnstagedChanges:
            unstaged = True
        assert unstaged

        # Test if the changes are commited
        self.file_code_driver.create_ref()
        unstaged = self.file_code_driver.check_unstaged_changes()

        assert not unstaged

    def test_checkout_ref(self):
        # Test failure, not initialized
        failed = False
        try:
            self.file_code_driver.create_ref()
        except CodeNotInitialized:
            failed = True
        assert failed
        self.__setup()
        commit_hash = "69a329523ce1ec88bf63061863d9cb14"
        # Test trying to checkout failure (commit does not exist)
        failed = False
        try:
            self.file_code_driver.checkout_ref(commit_id=commit_hash)
        except FileIOError:
            failed = True
        assert failed
        # Test successful checkout (same commit as current, no changes)
        commit_hash = self.file_code_driver.create_ref()
        result = self.file_code_driver.checkout_ref(commit_id=commit_hash)
        assert result
        # Test trying to checkout failure (unstaged changes)
        with open(os.path.join(self.temp_dir, "test2.txt"), "wb") as f:
            f.write(to_bytes("hello"))
        failed = False
        try:
            self.file_code_driver.checkout_ref(commit_id=commit_hash)
        except UnstagedChanges:
            failed = True
        assert failed
        # Test successful checkout with new commit (files back to old commit)
        _ = self.file_code_driver.create_ref()
        result = self.file_code_driver.checkout_ref(commit_id=commit_hash)
        assert result
        commit_filepath = os.path.join(self.file_code_driver._code_filepath,
                                       commit_hash)
        # Check all files in commit file exist and are at the correct point
        with open(commit_filepath, "r") as f:
            for line in f:
                tracked_filepath, filehash = line.rstrip().split(",")
                destination_absolute_filepath = os.path.join(
                    self.file_code_driver.root, tracked_filepath)
                assert os.path.isfile(destination_absolute_filepath)
                assert filehash == self.file_code_driver._get_filehash(
                    destination_absolute_filepath)
        # Check that files in the latest commit are not present
        assert not os.path.isfile(os.path.join(self.temp_dir, "test2.txt"))
