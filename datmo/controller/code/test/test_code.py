"""
Tests for CodeController
"""
import os
import shutil
import tempfile

from datmo.controller.project import ProjectController
from datmo.controller.code.code import \
    CodeController
from datmo.util.exceptions import EntityNotFound, \
    GitCommitDoesNotExist


class TestCodeController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        self.temp_dir = tempfile.mkdtemp('project')
        self.project = ProjectController(self.temp_dir)
        self.code = CodeController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test3", "test description")

        # Test failing for nothing to commit, no id
        try:
            self.code.create()
        except GitCommitDoesNotExist:
            assert True

        # Create test file
        definition_filepath = os.path.join(self.code.home,
                                    "test.txt")
        with open(definition_filepath, "w") as f:
            f.write(str("test"))

        # Test passing with something to commit
        code_obj = self.code.create()

        assert code_obj
        assert code_obj.id
        assert code_obj.driver_type

        # Test failing with random id given
        random_code_id = "random"
        try:
            self.code.create(id=random_code_id)
        except GitCommitDoesNotExist:
            assert True

    def test_list(self):
        self.project.init("test4", "test description")

        # Create test file
        definition_filepath = os.path.join(self.code.home,
                                           "test.txt")
        with open(definition_filepath, "w") as f:
            f.write(str("test"))

        # Test passing with something to commit
        code_obj_1 = self.code.create()

        # Create test file
        definition_filepath = os.path.join(self.code.home,
                                           "test2.txt")
        with open(definition_filepath, "w") as f:
            f.write(str("test"))

        # Test passing with something to commit
        code_obj_2 = self.code.create()

        # List all code and ensure they exist
        result = self.code.list()

        assert len(result) == 2 and \
            code_obj_1 in result and \
            code_obj_2 in result

    def test_delete(self):
        self.project.init("test5", "test description")

        # Create test file
        definition_filepath = os.path.join(self.code.home,
                                           "test.txt")
        with open(definition_filepath, "w") as f:
            f.write(str("test"))

        # Test passing with something to commit
        code_obj = self.code.create()

        # Delete code in the project
        result = self.code.delete(code_obj.id)

        # Check if code retrieval throws error
        thrown = False
        try:
            self.code.dal.code.get_by_id(code_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True