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

from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.task import TaskCommand
from datmo.util.exceptions import ProjectNotInitializedException, EntityNotFound


class TestTaskCommand():
    def setup_class(self):
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def __set_variables(self):
        self.init = ProjectCommand(self.temp_dir, self.cli_helper)
        self.init.parse([
            "init",
            "--name", "foobar",
            "--description", "test model"])
        self.init.execute()
        self.task = TaskCommand(self.temp_dir, self.cli_helper)

    def test_task_project_not_init(self):
        try:
            self.task = TaskCommand(self.temp_dir, self.cli_helper)
        except ProjectNotInitializedException:
            assert True

    def test_datmo_task_run(self):
        self.__set_variables()
        test_command = ["sh", "-c", "echo yo"]
        test_gpu = True
        test_ports = "8888:8888"
        test_data = "data"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_interactive = True

        self.task.parse([
            "task",
            "run",
            "--gpu",
            "--ports", test_ports,
            "--data", test_data,
            "--dockerfile", test_dockerfile,
            "--interactive",
            test_command
        ])

        # test for desired side effects
        assert self.task.args.command == test_command
        assert self.task.args.gpu == test_gpu
        assert self.task.args.ports == [test_ports]
        assert self.task.args.data == [test_data]
        assert self.task.args.dockerfile == test_dockerfile
        assert self.task.args.interactive == test_interactive

        if self.task.run():
            assert True


    def test_datmo_task_run_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
          self.task.parse([
            "task",
            "run"
            "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_task_ls(self):
        self.__set_variables()
        test_session_id = 'test_session_id'

        self.task.parse([
            "task",
            "ls",
            "--session-id", test_session_id
        ])

        # test for desired side effects
        assert self.task.args.session_id == test_session_id

        task_ls_command = self.task.ls()
        assert task_ls_command == True

    def test_datmo_task_ls_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
          self.task.parse([
            "task",
            "ls"
            "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_task_stop(self):
        self.__set_variables()

        test_command = ["sh", "-c", "echo yo"]
        test_ports = "8888:8888"
        test_data = "data"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        self.task.parse([
            "task",
            "run",
            "--gpu",
            "--ports", test_ports,
            "--data", test_data,
            "--dockerfile", test_dockerfile,
            "--interactive",
            test_command
        ])

        test_task_id = self.task.run()

        self.task.parse([
            "task",
            "stop",
            "--id", test_task_id
        ])

        # test for desired side effects
        assert self.task.args.id == test_task_id

        # test when task id is passed to stop it
        task_stop_command = self.task.stop()
        assert task_stop_command == True

        # Passing wrong task id
        test_task_id = "task_id"
        self.task.parse([
            "task",
            "stop",
            "--id", test_task_id
        ])

        # test when wrong task id is passed to stop it
        try:
            self.task.stop()
        except EntityNotFound:
            assert True


    def test_datmo_task_stop_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
          self.task.parse([
            "task",
            "stop"
            "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown