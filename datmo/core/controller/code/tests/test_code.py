"""
Tests for CodeController
"""
import os
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
from datmo.core.controller.code.code import CodeController
from datmo.core.util.exceptions import (EntityNotFound, CommitDoesNotExist,
                                        CodeDoesNotExist, UnstagedChanges)

class TestCodeController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.project_controller = ProjectController()
        self.code_controller = CodeController()

    def teardown_method(self):
        pass

    def test_current_code(self):
        self.project_controller.init("test4", "test description")

        # Create test file
        definition_filepath = os.path.join(self.code_controller.home,
                                           "test.txt")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Test failing with unstaged changes
        failed = False
        try:
            self.code_controller.current_code()
        except UnstagedChanges:
            failed = True
        assert failed
        # Test passing with something to commit
        code_obj = self.code_controller.create()
        current_code_obj = self.code_controller.current_code()
        assert code_obj == current_code_obj

    def test_create(self):
        self.project_controller.init("test3", "test description")

        # Test failing for nothing to commit, no id
        result = self.code_controller.create()
        assert result

        # Test failing for non-existant commit_id
        failed = False
        try:
            self.code_controller.create(commit_id="random")
        except CommitDoesNotExist:
            failed = True
        assert failed

        # Create test file
        definition_filepath = os.path.join(self.code_controller.home,
                                           "test.txt")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Test passing with something to commit
        code_obj = self.code_controller.create()

        assert code_obj
        assert code_obj.id
        assert code_obj.driver_type

        # Test should return same code_obj if same commit_id
        code_obj_2 = self.code_controller.create()

        assert code_obj_2 == code_obj

        # Test failing with random id given
        random_commit_id = "random"
        try:
            self.code_controller.create(commit_id=random_commit_id)
        except CommitDoesNotExist:
            assert True

    def test_list(self):
        self.project_controller.init("test4", "test description")

        # Create test file
        definition_filepath = os.path.join(self.code_controller.home,
                                           "test.txt")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Test passing with something to commit
        code_obj_1 = self.code_controller.create()

        # Create test file
        definition_filepath = os.path.join(self.code_controller.home,
                                           "test2.txt")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Test passing with something to commit
        code_obj_2 = self.code_controller.create()

        # List all code and ensure they exist
        result = self.code_controller.list()

        assert len(result) == 2 and \
            code_obj_1 in result and \
            code_obj_2 in result

    def test_delete(self):
        self.project_controller.init("test5", "test description")

        # Create test file
        definition_filepath = os.path.join(self.code_controller.home,
                                           "test.txt")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Test passing with something to commit
        code_obj = self.code_controller.create()

        # Delete code in the project
        result = self.code_controller.delete(code_obj.id)

        # Check if code retrieval throws error
        thrown = False
        try:
            self.code_controller.dal.code.get_by_id(code_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True

    def test_exists(self):
        # Test failure, not initialized
        failed = False
        try:
            _ = self.code_controller.create()
        except:
            failed = True
        assert failed

        # Initialize project and test file
        self.project_controller.init("test5", "test description")
        definition_filepath = os.path.join(self.code_controller.home,
                                           "test.txt")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("test")))
        code_obj = self.code_controller.create()

        # Check by code id
        result = self.code_controller.exists(code_id=code_obj.id)
        assert result

        # Check by code commit id
        result = self.code_controller.exists(code_commit_id=code_obj.commit_id)
        assert result

        # Test with wrong environment id
        result = self.code_controller.exists(code_id='test_wrong_env_id')
        assert not result

    def test_checkout(self):
        # Test code does not exist
        failed = False
        try:
            self.code_controller.checkout("does_not_exist")
        except CodeDoesNotExist:
            failed = True
        assert failed
