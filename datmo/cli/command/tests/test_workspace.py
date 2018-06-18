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

from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.workspace import WorkspaceCommand
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestWorkspace():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()
        self.project_command = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            self.project_command.execute()

        dummy(self)
        self.workspace_command = WorkspaceCommand(self.temp_dir, self.cli_helper)

    def teardown_method(self):
        pass

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_notebook(self):
        # Create environment_driver definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu\n")))

        # test single ports option before command
        self.workspace_command.parse([
            "notebook",
            "--gpu",
            "--environment-paths",
            env_def_path,
            "--mem-limit",
            test_mem_limit,
        ])

        # test for desired side effects
        assert self.workspace_command.args.gpu == True
        assert self.workspace_command.args.environment_paths == [env_def_path]
        assert self.workspace_command.args.mem_limit == test_mem_limit

        # test multiple ports option before command
        self.workspace_command.parse(["notebook"])

        assert self.workspace_command.args.gpu == False
