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
import timeout_decorator

from datmo.config import Config
from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.workspace import WorkspaceCommand
from datmo.cli.command.task import TaskCommand
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestWorkspace():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.cli_helper = Helper()

    def __set_variables(self):
        self.project_command = ProjectCommand(self.cli_helper)
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        dummy(self)

        self.workspace_command = WorkspaceCommand(self.cli_helper)
        self.task_command = TaskCommand(self.cli_helper)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/data-analytics:cpu-py27\n")))

    def teardown_method(self):
        pass

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_notebook(self):
        self.__set_variables()

        test_mem_limit = "4g"
        # test single ports option before command
        self.workspace_command.parse([
            "notebook",
            "--gpu",
            "--environment-paths",
            self.env_def_path,
            "--mem-limit",
            test_mem_limit,
        ])

        # test for desired side effects
        assert self.workspace_command.args.gpu == True
        assert self.workspace_command.args.environment_paths == [
            self.env_def_path
        ]
        assert self.workspace_command.args.mem_limit == test_mem_limit

        # test multiple ports option before command
        self.workspace_command.parse(["notebook"])

        assert self.workspace_command.args.gpu == False

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(timed_run_result):
            if self.workspace_command.execute():
                return timed_run_result

        timed_run_result = False
        try:
            timed_run_result = timed_run(timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

        # Stop all running datmo task
        self.task_command.parse(["task", "stop", "--all"])
        self.task_command.execute()

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_rstudio(self):
        self.__set_variables()

        # Update environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/rstudio:latest\n")))

        test_mem_limit = "4g"
        # test single ports option before command
        self.workspace_command.parse([
            "rstudio",
            "--environment-paths",
            self.env_def_path,
            "--mem-limit",
            test_mem_limit,
        ])

        # test for desired side effects
        assert self.workspace_command.args.environment_paths == [
            self.env_def_path
        ]
        assert self.workspace_command.args.mem_limit == test_mem_limit

        # test multiple ports option before command
        self.workspace_command.parse(["rstudio"])

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(timed_run_result):
            if self.workspace_command.execute():
                return timed_run_result

        timed_run_result = False
        try:
            timed_run_result = timed_run(timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

        # Stop all running datmo task
        self.task_command.parse(["task", "stop", "--all"])
        self.task_command.execute()
