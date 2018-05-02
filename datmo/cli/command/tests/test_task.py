"""
Tests for TaskCommand
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
import shutil
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.task import TaskCommand
from datmo.core.entity.task import Task as CoreTask
from datmo.core.util.exceptions import ProjectNotInitializedException


class TestTaskCommand():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        init = ProjectCommand(self.temp_dir, self.cli_helper)
        init.parse(["init", "--name", "foobar", "--description", "test model"])
        init.execute()

        self.task = TaskCommand(self.temp_dir, self.cli_helper)

        # Create environment_driver definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

    def test_task_project_not_init(self):
        failed = False
        try:
            self.task = TaskCommand(self.temp_dir, self.cli_helper)
        except ProjectNotInitializedException:
            failed = True
        assert failed

    def test_datmo_task_run_should_fail1(self):
        self.__set_variables()
        # Test failure case
        self.task.parse(["task", "run"])
        failed = False
        try:
            _ = self.task.execute()
        except:
            failed = True
        assert failed

    def test_datmo_task_run_should_fail2(self):
        self.__set_variables()
        # Test failure case execute
        test_command = ["yo", "yo"]
        self.task.parse(["task", "run", test_command])
        result = self.task.execute()
        assert not result

    def test_datmo_task_run(self):
        self.__set_variables()
        # Test success case
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_gpu = True  # TODO: implement in controller
        test_ports = "8888:8888"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_interactive = True

        self.task.parse([
            "task", "run", "--gpu", "--ports", test_ports, "--env-def",
            test_dockerfile, "--interactive", test_command
        ])

        # test for desired side effects
        assert self.task.args.cmd == test_command
        assert self.task.args.gpu == test_gpu
        assert self.task.args.ports == [test_ports]
        assert self.task.args.environment_definition_filepath == test_dockerfile
        assert self.task.args.interactive == test_interactive

        # test proper execution of task run command
        result = self.task.execute()
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"

    def test_task_run_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task.parse(["task", "run" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_task_ls(self):
        self.__set_variables()
        test_session_id = 'test_session_id'

        self.task.parse(["task", "ls", "--session-id", test_session_id])

        # test for desired side effects
        assert self.task.args.session_id == test_session_id

        task_ls_command = self.task.execute()
        assert task_ls_command == True

    def test_task_ls_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task.parse(["task", "ls" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_task_stop(self):
        self.__set_variables()

        test_command = ["sh", "-c", "echo yo"]
        test_ports = "8888:8888"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        self.task.parse([
            "task", "run", "--gpu", "--ports", test_ports, "--env-def",
            test_dockerfile, "--interactive", test_command
        ])

        test_task_obj = self.task.execute()

        self.task.parse(["task", "stop", "--id", test_task_obj.id])

        # test for desired side effects
        assert self.task.args.id == test_task_obj.id

        # test when task id is passed to stop it
        task_stop_command = self.task.execute()
        assert task_stop_command == True

    def test_task_stop_invalid_task_id(self):
        self.__set_variables()
        # Passing wrong task id
        self.task.parse(["task", "stop", "--id", "invalid-task-id"])

        # test when wrong task id is passed to stop it
        result = self.task.execute()
        assert not result

    def test_task_stop_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task.parse(["task", "stop" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown
