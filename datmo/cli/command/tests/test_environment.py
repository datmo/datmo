"""
Tests for EnvironmentCommand
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import uuid
import tempfile
import shutil
import platform
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

import os
from datmo.cli.driver.helper import Helper
from datmo.cli.command.environment import EnvironmentCommand
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestEnvironment():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        self.project = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project.execute()
        self.environment_command = EnvironmentCommand(self.temp_dir,
                                                      self.cli_helper)

    def test_environment_setup_parameter(self):
        # Setup the environement by passing name
        self.__set_variables()
        definition_filepath = os.path.join(
            self.environment_command.environment_controller.
            environment_directory, "Dockerfile")

        # Test pass with correct input
        test_name = "xgboost:cpu"
        self.environment_command.parse(
            ["environment", "setup", "--name", test_name])
        result = self.environment_command.execute()

        assert result
        assert os.path.isfile(definition_filepath)
        assert "FROM datmo/xgboost:cpu" in open(definition_filepath,
                                                "r").read()

        # Test fail with wrong input
        test_name = "random"
        self.environment_command.parse(
            ["environment", "setup", "--name", test_name])
        result = self.environment_command.execute()
        assert not result

    def test_environment_setup_prompt(self):
        # Setup the environement by passing name
        self.__set_variables()
        definition_filepath = os.path.join(
            self.environment_command.environment_controller.
            environment_directory, "Dockerfile")

        # Test success with correct prompt input using numbers
        self.environment_command.parse(["environment", "setup"])

        @self.environment_command.cli_helper.input("1\n")
        def dummy(self):
            return self.environment_command.execute()

        result = dummy(self)

        assert result
        assert os.path.isfile(definition_filepath)
        assert "FROM datmo/xgboost:cpu" in open(definition_filepath,
                                                "r").read()

        # Test success with correct prompt input using string
        test_name = "xgboost:cpu"
        self.environment_command.parse(["environment", "setup"])

        @self.environment_command.cli_helper.input(test_name + "\n")
        def dummy(self):
            return self.environment_command.execute()

        result = dummy(self)

        assert result
        assert os.path.isfile(definition_filepath)
        assert "FROM datmo/xgboost:cpu" in open(definition_filepath,
                                                "r").read()

        # Test failure with prompt input number out of range
        self.environment_command.parse(["environment", "setup"])

        @self.environment_command.cli_helper.input("-1\n")
        def dummy(self):
            return self.environment_command.execute()

        result = dummy(self)

        assert not result

        # Test failure with prompt input string incorrect
        self.environment_command.parse(["environment", "setup"])

        @self.environment_command.cli_helper.input("random\n")
        def dummy(self):
            return self.environment_command.execute()

        result = dummy(self)

        assert not result

    def test_environment_create(self):
        # 1) Environment definition file in project environment directory (with name / description)
        # 2) Environment definition file passed as an option
        # 3) Environment definition file in root project folder
        # 4) Environment definition file in root project folder (should return the same environment)
        # 5) No environment definition file present
        # 6) No environment definition file present (should return the same environment)
        self.__set_variables()
        # Test option 1
        # Create environment definition in project environment directory
        definition_filepath = os.path.join(
            self.environment_command.environment_controller.
            environment_directory, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        self.environment_command.parse([
            "environment", "create", "--name", "test", "--description",
            "test description"
        ])
        result = self.environment_command.execute()

        assert result
        assert result.name == "test"
        assert result.description == "test description"

        # remove datmo_environment directory
        shutil.rmtree(self.environment_command.environment_controller.
                      environment_directory)

        # Test option 2
        random_dir = os.path.join(self.temp_dir, "random_datmo_dir")
        os.makedirs(random_dir)

        definition_filepath = os.path.join(random_dir, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        self.environment_command.parse(
            ["environment", "create", "--paths", definition_filepath])
        result = self.environment_command.execute()
        assert result

        # remove directory with Dockerfile
        shutil.rmtree(random_dir)

        # Test option 3
        definition_filepath = os.path.join(self.temp_dir, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        self.environment_command.parse(["environment", "create"])
        result = self.environment_command.execute()
        assert result

        # Test option 4
        self.environment_command.parse(["environment", "create"])
        result_2 = self.environment_command.execute()
        assert result == result_2

        os.remove(definition_filepath)

        # Test option 5
        self.environment_command.parse(["environment", "create"])
        result = self.environment_command.execute()
        assert result

        # Test option 6
        self.environment_command.parse(["environment", "create"])
        result_2 = self.environment_command.execute()
        assert result == result_2

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_environment_delete(self):
        self.__set_variables()
        self.environment_command.parse(["environment", "create"])
        environment_obj = self.environment_command.execute()

        self.environment_command.parse(
            ["environment", "delete", "--id", environment_obj.id])
        result = self.environment_command.execute()

        assert result

    def test_environment_ls(self):
        self.__set_variables()
        self.environment_command.parse(["environment", "create"])
        created_environment_obj = self.environment_command.execute()

        self.environment_command.parse(["environment", "ls"])
        environment_objs = self.environment_command.execute()

        assert created_environment_obj in environment_objs
