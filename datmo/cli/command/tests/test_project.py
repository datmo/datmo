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

import os
import tempfile
import platform

from datmo.config import Config
from datmo import __version__
from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.exceptions import UnrecognizedCLIArgument


class TestProject():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.cli_helper = Helper()
        self.project = ProjectCommand(self.cli_helper)

    def teardown_method(self):
        pass

    def test_init_create_success(self):
        test_name = "foobar"
        test_description = "test model"
        self.project.parse(
            ["init", "--name", test_name, "--description", test_description])
        result = self.project.execute()
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result.name == test_name
        assert result.description == test_description

    def test_init_create_failure(self):
        self.project.parse(["init", "--name", "", "--description", ""])
        # test if prompt opens
        @self.project.cli_helper.input("\n\n")
        def dummy(self):
            return self.project.execute()

        result = dummy(self)
        assert not result

    def test_init_update_success(self):
        test_name = "foobar"
        test_description = "test model"
        self.project.parse(
            ["init", "--name", test_name, "--description", test_description])
        result_1 = self.project.execute()
        updated_name = "foobar2"
        updated_description = "test model 2"
        self.project.parse([
            "init", "--name", updated_name, "--description",
            updated_description
        ])
        result_2 = self.project.execute()
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == updated_name
        assert result_2.description == updated_description

    def test_init_update_success_only_name(self):
        test_name = "foobar"
        test_description = "test model"
        self.project.parse(
            ["init", "--name", test_name, "--description", test_description])
        result_1 = self.project.execute()
        updated_name = "foobar2"
        self.project.parse(
            ["init", "--name", updated_name, "--description", ""])

        @self.project.cli_helper.input("\n")
        def dummy(self):
            return self.project.execute()

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == updated_name
        assert result_2.description == result_1.description

    def test_init_update_success_only_description(self):
        test_name = "foobar"
        test_description = "test model"
        self.project.parse(
            ["init", "--name", test_name, "--description", test_description])
        result_1 = self.project.execute()
        updated_description = "test model 2"
        self.project.parse(
            ["init", "--name", "", "--description", updated_description])

        @self.project.cli_helper.input("\n")
        def dummy(self):
            return self.project.execute()

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == result_1.name
        assert result_2.description == updated_description

    def test_init_invalid_arg(self):
        exception_thrown = False
        try:
            self.project.parse(["init", "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_version(self):
        self.project.parse(["version"])
        result = self.project.execute()
        # test for desired side effects
        assert __version__ in result

    def test_version_invalid_arg(self):
        exception_thrown = False
        try:
            self.project.parse(["version", "--foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_status(self):
        test_name = "foobar"
        test_description = "test model"
        self.project.parse(
            ["init", "--name", test_name, "--description", test_description])
        _ = self.project.execute()

        self.project.parse(["status"])
        result = self.project.execute()
        assert isinstance(result[0], dict)
        assert not result[1]
        assert not result[2]

    def test_status_invalid_arg(self):
        exception_thrown = False
        try:
            self.project.parse(["status", "--foobar"])
        except UnrecognizedCLIArgument:
            exception_thrown = True
        assert exception_thrown

    def test_cleanup(self):
        test_name = "foobar"
        test_description = "test model"
        self.project.parse(
            ["init", "--name", test_name, "--description", test_description])
        _ = self.project.execute()

        self.project.parse(["cleanup"])

        @self.project.cli_helper.input("y\n")
        def dummy(self):
            return self.project.execute()

        result = dummy(self)
        assert not os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert isinstance(result, bool)
        assert result

    def test_cleanup_invalid_arg(self):
        exception_thrown = False
        try:
            self.project.parse(["cleanup", "--foobar"])
        except UnrecognizedCLIArgument:
            exception_thrown = True
        assert exception_thrown
