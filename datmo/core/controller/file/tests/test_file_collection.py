"""
Tests for FileCollectionController
"""
import os
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

from datmo.config import Config
from datmo.core.controller.project import ProjectController
from datmo.core.controller.file.file_collection import \
    FileCollectionController
from datmo.core.util.exceptions import EntityNotFound, UnstagedChanges

class TestFileCollectionController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.project_controller = ProjectController()
        self.file_collection_controller = FileCollectionController()

    def teardown_method(self):
        pass

    def __setup(self):
        # Create the files in the project files directory
        dirpath1 = os.path.join(
            self.file_collection_controller.file_driver.files_directory,
            "dirpath1")
        os.makedirs(dirpath1)
        filepath1 = os.path.join(
            self.file_collection_controller.file_driver.files_directory,
            "filepath1")
        with open(filepath1, "wb") as _:
            pass
        return filepath1, dirpath1

    def test_current_file_collection(self):
        self.project_controller.init("test3", "test description")
        _ = self.__setup()
        # Test failure because of unstaged changes
        failed = False
        try:
            self.file_collection_controller.current_file_collection()
        except UnstagedChanges:
            failed = True
        assert failed
        # Test success with created files
        file_collection_obj = self.file_collection_controller.create([])
        current_file_collection_obj = self.file_collection_controller.current_file_collection(
        )
        assert current_file_collection_obj == file_collection_obj

    def test_create(self):
        self.project_controller.init("test3", "test description")

        # Test failure creation of collection if no path given
        failed = False
        try:
            self.file_collection_controller.create()
        except TypeError:
            failed = True
        assert failed

        # Test create success with paths
        paths = self.__setup()
        file_collection_obj = self.file_collection_controller.create(paths)

        assert file_collection_obj
        assert file_collection_obj.id
        assert file_collection_obj.path
        assert file_collection_obj.driver_type
        assert file_collection_obj.filehash == "74be16979710d4c4e7c6647856088456"

        # Test create success without paths (should be the same as previous)
        file_collection_obj_1 = self.file_collection_controller.create([])
        assert file_collection_obj_1 == file_collection_obj
        assert file_collection_obj_1.id == file_collection_obj.id
        assert file_collection_obj_1.path == file_collection_obj.path
        assert file_collection_obj_1.driver_type == file_collection_obj.driver_type
        assert file_collection_obj_1.filehash == file_collection_obj.filehash

        # Test create success with paths again (should be same as previous)
        file_collection_obj_2 = self.file_collection_controller.create(paths)
        assert file_collection_obj_2 == file_collection_obj_1
        assert file_collection_obj_2.id == file_collection_obj_1.id
        assert file_collection_obj_2.path == file_collection_obj_1.path
        assert file_collection_obj_2.driver_type == file_collection_obj_1.driver_type
        assert file_collection_obj_2.filehash == file_collection_obj_1.filehash

        # Test file collection with empty paths (should be same as previous)
        file_collection_obj_3 = self.file_collection_controller.create([])
        assert file_collection_obj_3 == file_collection_obj_2
        assert file_collection_obj_3.id == file_collection_obj_2.id
        assert file_collection_obj_3.path == file_collection_obj_2.path
        assert file_collection_obj_3.driver_type == file_collection_obj_2.driver_type
        assert file_collection_obj_3.filehash == file_collection_obj_2.filehash

    def test_list(self):
        self.project_controller.init("test4", "test description")

        paths_1 = self.__setup()

        filepath2 = os.path.join(self.file_collection_controller.home,
                                 "filepath2")
        with open(filepath2, "wb") as f:
            f.write(to_bytes("test" + "\n"))
        paths_2 = [filepath2]

        file_collection_obj_1 = self.file_collection_controller.create(paths_1)
        file_collection_obj_2 = self.file_collection_controller.create(paths_2)

        # List all code and ensure they exist
        result = self.file_collection_controller.list()

        assert len(result) == 2 and \
            file_collection_obj_1 in result and \
            file_collection_obj_2 in result

    def test_delete(self):
        self.project_controller.init("test5", "test description")

        paths = self.__setup()

        file_collection_obj = self.file_collection_controller.create(paths)

        # Delete code in the project
        result = self.file_collection_controller.delete(file_collection_obj.id)

        # Check if code retrieval throws error
        thrown = False
        try:
            self.file_collection_controller.dal.file_collection.get_by_id(
                file_collection_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True

    def test_exists_file(self):
        self.project_controller.init("test6", "test description")

        paths = self.__setup()

        file_collection_obj = self.file_collection_controller.create(paths)

        # check for file_collection_id
        result = self.file_collection_controller.exists(
            file_collection_id=file_collection_obj.id)
        assert result

        # check for file_hash in file_collection
        result = self.file_collection_controller.exists(
            file_hash=file_collection_obj.filehash)
        assert result

        # check for not proper file_collection_id
        result = self.file_collection_controller.exists(
            file_collection_id="test_file_collection_id")
        assert not result

    def test_calculate_project_files_hash(self):
        self.project_controller.init("test7", "test description")

        filepath1, dirpath1 = self.__setup()

        # Test if hash is for 1 blank filepath and empty directory
        result = self.file_collection_controller._calculate_project_files_hash(
        )
        assert result == "74be16979710d4c4e7c6647856088456"

    def test_has_unstaged_changes(self):
        self.project_controller.init("test8", "test description")

        # Create the files in the project files directory
        paths = self.__setup()

        # Test when there are unstaged changes
        result = self.file_collection_controller._has_unstaged_changes()
        assert result

        # Save the file collection
        self.file_collection_controller.create(paths)

        # Test when there are no unstaged changes
        result = self.file_collection_controller._has_unstaged_changes()
        assert not result

        # Change the file contents
        with open(paths[0], "wb") as f:
            f.write(to_bytes("hello"))

        # Test when there are unstaged changes again
        result = self.file_collection_controller._has_unstaged_changes()
        assert result

    def test_check_unstaged_changes(self):
        self.project_controller.init("test9", "test description")

        # Create the files in the project files directory
        paths = self.__setup()

        # Test when there are unstaged changes
        failed = False
        try:
            _ = self.file_collection_controller.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # Save the file collection
        self.file_collection_controller.create(paths)

        # Test when there are no unstaged changes
        result = self.file_collection_controller.check_unstaged_changes()
        assert not result

        # Change the file contents
        with open(paths[0], "wb") as f:
            f.write(to_bytes("hello"))

        # Test when there are unstaged changes again
        failed = False
        try:
            _ = self.file_collection_controller.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # Test when there are no files (should be staged)
        os.remove(paths[0])
        shutil.rmtree(paths[1])
        result = self.file_collection_controller.check_unstaged_changes()
        assert not result

    def test_checkout(self):
        self.project_controller.init("test9", "test description")

        # Create the files in the project files directory
        paths = self.__setup()

        # Create a file collection to checkout to with paths
        file_collection_obj = self.file_collection_controller.create(paths)

        # Checkout success when there are no unstaged changes
        result = self.file_collection_controller.checkout(
            file_collection_obj.id)
        assert result
        current_hash = self.file_collection_controller._calculate_project_files_hash(
        )
        assert current_hash == "74be16979710d4c4e7c6647856088456"
        assert file_collection_obj.filehash == current_hash
        # Check the filenames as well because the hash does not take this into account
        assert os.path.isfile(paths[0])

        # Change file contents to make it unstaged
        with open(paths[0], "wb") as f:
            f.write(to_bytes("hello"))

        # Checkout failure when there are unstaged changes
        failed = False
        try:
            _ = self.file_collection_controller.checkout(
                file_collection_obj.id)
        except UnstagedChanges:
            failed = True
        assert failed

        # Create a new file collection with paths
        file_collection_obj_1 = self.file_collection_controller.create(paths)

        # Checkout success back when there are no unstaged changes
        result = self.file_collection_controller.checkout(
            file_collection_obj.id)
        assert result
        current_hash = self.file_collection_controller._calculate_project_files_hash(
        )
        assert current_hash == "74be16979710d4c4e7c6647856088456"
        assert file_collection_obj.filehash == current_hash
        assert file_collection_obj_1.filehash != current_hash
        # Check the filenames as well because the hash does not take this into account
        assert os.path.isfile(paths[0])
