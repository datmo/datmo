"""
Tests for FileCollectionController
"""
import os
import shutil
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
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
        self.project = ProjectController(self.temp_dir)
        self.file_collection = FileCollectionController(self.temp_dir)

    def teardown_method(self):
        pass

    def test_create(self):
        self.project.init("test3", "test description")

        # Test failure creation of collection
        failed = False
        try:
            self.file_collection.create()
        except Exception:
            failed = True
        assert failed

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", directory=True)
        self.file_collection.file_driver.create("filepath1")

        dirpath1 = os.path.join(self.file_collection.home, "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "filepath1")
        paths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(paths)

        assert file_collection_obj
        assert file_collection_obj.id
        assert file_collection_obj.path
        assert file_collection_obj.driver_type

        # Test file collection with same paths/filehash returns same object
        file_collection_obj_2 = self.file_collection.create(paths)

        assert file_collection_obj_2 == file_collection_obj

    def test_list(self):
        self.project.init("test4", "test description")

        self.file_collection.file_driver.create("dirpath1", directory=True)
        self.file_collection.file_driver.create("filepath1")
        dirpath1 = os.path.join(self.file_collection.home, "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "filepath1")
        paths_1 = [filepath1, dirpath1]

        filepath2 = os.path.join(self.file_collection.home, "filepath2")
        with open(filepath2, "wb") as f:
            f.write(to_bytes("test" + "\n"))
        paths_2 = [filepath2]

        file_collection_obj_1 = self.file_collection.create(paths_1)
        file_collection_obj_2 = self.file_collection.create(paths_2)

        # List all code and ensure they exist
        result = self.file_collection.list()

        assert len(result) == 2 and \
            file_collection_obj_1 in result and \
            file_collection_obj_2 in result

    def test_delete(self):
        self.project.init("test5", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", directory=True)
        self.file_collection.file_driver.create("filepath1")

        dirpath1 = os.path.join(self.file_collection.home, "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "filepath1")
        paths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(paths)

        # Delete code in the project
        result = self.file_collection.delete(file_collection_obj.id)

        # Check if code retrieval throws error
        thrown = False
        try:
            self.file_collection.dal.file_collection.get_by_id(
                file_collection_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True

    def test_exists_file(self):
        self.project.init("test6", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", directory=True)
        self.file_collection.file_driver.create("filepath1")

        dirpath1 = os.path.join(self.file_collection.home, "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "filepath1")
        filepaths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(filepaths)

        # check for file_collection_id
        result = self.file_collection.exists(
            file_collection_id=file_collection_obj.id)
        assert result

        # check for file_hash in file_collection
        result = self.file_collection.exists(
            file_hash=file_collection_obj.filehash)
        assert result

        # check for not proper file_collection_id
        result = self.file_collection.exists(
            file_collection_id="test_file_collection_id")
        assert not result

    def test_calculate_file_collection_hash(self):
        self.project.init("test7", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", directory=True)
        self.file_collection.file_driver.create("filepath1")

        # Test successful creation of collection
        dirpath1 = os.path.join(self.file_collection.home, "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "filepath1")
        filepaths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(filepaths)
        datmo_files_path = os.path.join(self.file_collection.home,
                                        "datmo_files")
        file_collection_path = os.path.join(self.file_collection.home,
                                            file_collection_obj.path)
        self.file_collection.file_driver.copytree(file_collection_path,
                                                  datmo_files_path)

        assert file_collection_obj.filehash == self.file_collection._calculate_datmo_files_hash(
        )

        shutil.rmtree(datmo_files_path)

        self.file_collection.file_driver.create(
            "datmo_files/dirpath1", directory=True)
        self.file_collection.file_driver.create("datmo_files/filepath1")

        dirpath1 = os.path.join(self.file_collection.home, "datmo_files",
                                "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "datmo_files",
                                 "filepath1")
        filepaths = [filepath1, dirpath1]

        file_collection_obj_1 = self.file_collection.create(filepaths)

        assert file_collection_obj.filehash == file_collection_obj_1.filehash

    def test_has_unstaged_changes(self):
        self.project.init("test8", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create(
            "datmo_files/dirpath1", directory=True)
        self.file_collection.file_driver.create("datmo_files/filepath1")
        dirpath1 = os.path.join(self.file_collection.home, "datmo_files",
                                "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "datmo_files",
                                 "filepath1")
        filepaths = [filepath1, dirpath1]

        self.file_collection.create(filepaths)

        # Test when there are no unstaged changes
        result = self.file_collection._has_unstaged_changes()
        assert not result

        with open(filepath1, "wb") as f:
            f.write(to_bytes("hello"))

        # Test when there are unstaged changes
        result = self.file_collection._has_unstaged_changes()
        assert result

    def test_check_unstaged_changes(self):
        self.project.init("test9", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create(
            "datmo_files/dirpath1", directory=True)
        self.file_collection.file_driver.create("datmo_files/filepath1")

        dirpath1 = os.path.join(self.file_collection.home, "datmo_files",
                                "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "datmo_files",
                                 "filepath1")
        filepaths = [filepath1, dirpath1]
        self.file_collection.create(filepaths)

        # Test when there are no unstaged changes
        result = self.file_collection.check_unstaged_changes()
        assert not result

        # Change a file
        with open(filepath1, "wb") as f:
            f.write(to_bytes("hello"))

        # Test when there are unstaged changes
        failed = False
        try:
            _ = self.file_collection.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # Test when there are no files (should be staged)
        os.remove(filepath1)
        shutil.rmtree(dirpath1)
        result = self.file_collection.check_unstaged_changes()
        assert not result

    def test_checkout_file(self):
        self.project.init("test9", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", directory=True)
        self.file_collection.file_driver.create("filepath1")

        dirpath1 = os.path.join(self.file_collection.home, "dirpath1")
        filepath1 = os.path.join(self.file_collection.home, "filepath1")
        filepaths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(filepaths)

        # Test when there are no unstaged changes
        result = self.file_collection.checkout(file_collection_obj.id)
        assert result

        # changing filepath in `datmo_files`
        datmo_file_path = os.path.join(self.file_collection.home,
                                       "datmo_files")
        with open(os.path.join(datmo_file_path, "filepath1"), "wb") as f:
            f.write(to_bytes("hello"))

        # Test when there are unstaged changes
        failed = False
        try:
            _ = self.file_collection.checkout(file_collection_obj.id)
        except:
            failed = True
        assert failed
