"""
Tests for Project Commands
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# TODO: include builtin libraries for the appropriate Python
# try:
#     import __builtin__
# except ImportError:
#     # Python 3
#     import builtins as __builtin__
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

import os
import tempfile
import platform

from datmo import __version__
from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.exceptions import UnrecognizedCLIArgument
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                tempfile.gettempdir())

class TestProject():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()
        self.project_command = ProjectCommand(self.temp_dir, self.cli_helper)

    def teardown_method(self):
        pass

    def test_init_create_success_no_environment(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        # Test when environment is not created
        @self.project_command.cli_helper.input("\n")
        def dummy_no_environment(self):
            return self.project_command.execute()

        result = dummy_no_environment(self)

        definition_filepath = os.path.join(self.temp_dir, "datmo_environment", "Dockerfile")

        assert result
        assert not os.path.isfile(definition_filepath)
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result.name == test_name
        assert result.description == test_description

    def test_init_create_success_environment(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        # Test when environment is created
        @self.project_command.cli_helper.input("y\n1\n")
        def dummy_environment(self):
            return self.project_command.execute()

        result = dummy_environment(self)

        definition_filepath = os.path.join(self.temp_dir, "datmo_environment", "Dockerfile")

        assert result
        assert os.path.isfile(definition_filepath)
        assert "FROM datmo/xgboost:cpu" in open(definition_filepath,
                                                "r").read()

        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result.name == test_name
        assert result.description == test_description


    def test_init_create_failure(self):
        self.project_command.parse(["init", "--name", "", "--description", ""])
        # test if prompt opens
        @self.project_command.cli_helper.input("\n\n\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)
        assert not result

    def test_init_update_success(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)
        updated_name = "foobar2"
        updated_description = "test model 2"
        self.project_command.parse([
            "init", "--name", updated_name, "--description",
            updated_description
        ])

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == updated_name
        assert result_2.description == updated_description

    def test_init_update_success_only_name(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)
        updated_name = "foobar2"
        self.project_command.parse(
            ["init", "--name", updated_name, "--description", ""])

        @self.project_command.cli_helper.input("\n\n")
        def dummy(self):
            return self.project_command.execute()

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == updated_name
        assert result_2.description == result_1.description

    def test_init_update_success_only_description(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)
        updated_description = "test model 2"
        self.project_command.parse(
            ["init", "--name", "", "--description", updated_description])

        @self.project_command.cli_helper.input("\n\n")
        def dummy(self):
            return self.project_command.execute()

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == result_1.name
        assert result_2.description == updated_description

    def test_init_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["init", "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_version(self):
        self.project_command.parse(["version"])
        result = self.project_command.execute()
        # test for desired side effects
        assert __version__ in result

    def test_version_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["version", "--foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_status(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        assert isinstance(result[0], dict)
        assert not result[1]
        assert not result[2]

    def test_status_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["status", "--foobar"])
        except UnrecognizedCLIArgument:
            exception_thrown = True
        assert exception_thrown

    def test_cleanup(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        self.project_command.parse(["cleanup"])

        @self.project_command.cli_helper.input("y\n\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)
        assert not os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert isinstance(result, bool)
        assert result

    def test_cleanup_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["cleanup", "--foobar"])
        except UnrecognizedCLIArgument:
            exception_thrown = True
        assert exception_thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_notebook(self):
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            self.project_command.execute()

        dummy(self)

        # Create environment_driver definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu\n")))

        # test single ports option before command
        self.project_command.parse(["notebook", "--gpu", "--environment-paths", env_def_path,
                                    "--mem-limit", test_mem_limit,])

        # test for desired side effects
        assert self.project_command.args.gpu == True
        assert self.project_command.args.environment_paths == [env_def_path]
        assert self.project_command.args.mem_limit == test_mem_limit

        # test multiple ports option before command
        self.project_command.parse(["notebook"])

        assert self.project_command.args.gpu == False