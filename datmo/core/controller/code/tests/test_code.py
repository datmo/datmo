"""
Tests for CodeController
"""
import os
import tempfile
import platform
import shutil
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.config import Config
from datmo.core.controller.project import ProjectController
from datmo.core.controller.code.code import CodeController
from datmo.core.util.exceptions import (EntityNotFound, GitCommitDoesNotExist)


class TestCodeController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.project = ProjectController()
        self.code = CodeController()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test3", "test description")

        # Test failing for nothing to commit, no id
        failed = False
        try:
            self.code.create()
        except GitCommitDoesNotExist:
            failed = True
        assert failed

        # Create test file
        definition_filepath = os.path.join(self.code.home, "test.txt")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("test")))

        # Test passing with something to commit
        code_obj = self.code.create()

        assert code_obj
        assert code_obj.id
        assert code_obj.driver_type

        # Test should return same code_obj if same commit_id
        code_obj_2 = self.code.create()

        assert code_obj_2 == code_obj

        # Test failing with random id given
        random_commit_id = "random"
        try:
            self.code.create(commit_id=random_commit_id)
        except GitCommitDoesNotExist:
            assert True

    def test_list(self):
        self.project.init("test4", "test description")

        # Create test file
        definition_filepath = os.path.join(self.code.home, "test.txt")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("test")))

        # Test passing with something to commit
        code_obj_1 = self.code.create()

        # Create test file
        definition_filepath = os.path.join(self.code.home, "test2.txt")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("test")))

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
        definition_filepath = os.path.join(self.code.home, "test.txt")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("test")))

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
