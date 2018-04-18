"""
Tests for FileCollectionController
"""
import os
import shutil
import tempfile

from datmo.core.controller.project import ProjectController
from datmo.core.controller.file.file_collection import \
    FileCollectionController
from datmo.core.util.exceptions import EntityNotFound


class TestFileCollectionController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.file_collection = FileCollectionController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test3", "test description")

        # Test failure creation of collection
        try:
            self.file_collection.create()
        except:
            assert True

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", dir=True)
        self.file_collection.file_driver.create("filepath1")

        dirpath1 = os.path.join(self.file_collection.home,
                                "dirpath1")
        filepath1 = os.path.join(self.file_collection.home,
                                 "filepath1")
        filepaths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(filepaths)

        assert file_collection_obj
        assert file_collection_obj.id
        assert file_collection_obj.path
        assert file_collection_obj.driver_type

        # Test file collection with same filepaths/filehash returns same object
        file_collection_obj_2 = self.file_collection.create(filepaths)

        assert file_collection_obj_2 == file_collection_obj

    def test_list(self):
        self.project.init("test4", "test description")

        self.file_collection.file_driver.create("dirpath1", dir=True)
        self.file_collection.file_driver.create("filepath1")
        dirpath1 = os.path.join(self.file_collection.home,
                                "dirpath1")
        filepath1 = os.path.join(self.file_collection.home,
                                 "filepath1")
        filepaths_1 = [filepath1, dirpath1]


        filepath2 = os.path.join(self.file_collection.home,
                                 "filepath2")
        with open(filepath2, "w") as f:
            f.write("test" + "\n")
        filepaths_2 = [filepath2]

        file_collection_obj_1 = self.file_collection.create(filepaths_1)
        file_collection_obj_2 = self.file_collection.create(filepaths_2)

        # List all code and ensure they exist
        result = self.file_collection.list()

        assert len(result) == 2 and \
            file_collection_obj_1 in result and \
            file_collection_obj_2 in result

    def test_delete(self):
        self.project.init("test5", "test description")

        # Test successful creation of collection
        self.file_collection.file_driver.create("dirpath1", dir=True)
        self.file_collection.file_driver.create("filepath1")

        dirpath1 = os.path.join(self.file_collection.home,
                                "dirpath1")
        filepath1 = os.path.join(self.file_collection.home,
                                 "filepath1")
        filepaths = [filepath1, dirpath1]

        file_collection_obj = self.file_collection.create(filepaths)

        # Delete code in the project
        result = self.file_collection.delete(file_collection_obj.id)

        # Check if code retrieval throws error
        thrown = False
        try:
            self.file_collection.dal.file_collection.get_by_id(file_collection_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True