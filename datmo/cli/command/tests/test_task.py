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
import time
import tempfile
import platform

from multiprocessing import Process, Manager
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.config import Config
from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.task import TaskCommand
from datmo.core.entity.task import Task as CoreTask
from datmo.core.util.exceptions import ProjectNotInitializedException, MutuallyExclusiveArguments, RequiredArgumentMissing
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestTaskCommand():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        self.project = ProjectCommand(self.cli_helper)
        self.project.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project.execute()

        self.task = TaskCommand(self.cli_helper)

        # Create environment_driver definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

    def test_task_project_not_init(self):
        failed = False
        try:
            self.task = TaskCommand(self.cli_helper)
        except ProjectNotInitializedException:
            failed = True
        assert failed

    def test_task_command(self):
        self.__set_variables()
        self.task.parse(["task"])
        assert self.task.execute()

    def test_task_run_should_fail1(self):
        self.__set_variables()
        # Test failure case
        self.task.parse(["task", "run"])
        result = self.task.execute()
        assert not result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_run(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()

        # Test failure command execute
        test_command = ["yo", "yo"]
        self.task.parse(["task", "run", test_command])
        result = self.task.execute()
        assert result

        # Test success case
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        # test for single set of ports
        self.task.parse([
            "task", "run", "--ports", test_ports[0], "--environment-def",
            test_dockerfile, test_command
        ])

        # test for desired side effects
        assert self.task.args.cmd == test_command
        assert self.task.args.ports == [test_ports[0]]
        assert self.task.args.environment_definition_filepath == test_dockerfile

        self.task.parse([
            "task", "run", "-p", test_ports[0], "-p", test_ports[1],
            "--environment-def", test_dockerfile, test_command
        ])
        # test for desired side effects
        assert self.task.args.cmd == test_command
        assert self.task.args.ports == test_ports
        assert self.task.args.environment_definition_filepath == test_dockerfile

        # test proper execution of task run command
        result = self.task.execute()
        time.sleep(1)
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_run_string_command(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()
        # Test success case
        test_command = "sh -c 'echo accuracy:0.45'"
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        self.task.parse([
            "task", "run", "--ports", test_ports[0], "--ports", test_ports[1],
            "--environment-def", test_dockerfile, test_command
        ])
        # test for desired side effects
        assert self.task.args.cmd == test_command
        assert self.task.args.ports == test_ports
        assert self.task.args.environment_definition_filepath == test_dockerfile

        # test proper execution of task run command
        result = self.task.execute()
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"

    # def test_multiple_concurrent_task_run_command(self):
    #     test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
    #     test_command = ["sh", "-c", "echo accuracy:0.45"]
    #     manager = Manager()
    #     return_dict = manager.dict()
    #
    #     def task_exec_func(procnum, return_dict):
    #         print("Creating Task object")
    #         task = TaskCommand(self.cli_helper)
    #         print("Parsing command")
    #         task.parse(
    #             ["task", "run", "--environment-def", test_dockerfile, test_command])
    #         print("Executing command")
    #         result = task.execute()
    #         return_dict[procnum] = result
    #
    #     self.__set_variables()
    #     test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
    #
    #     # Run all three tasks in parallel
    #     jobs = []
    #     number_tasks = 3
    #     for i in range(number_tasks):
    #         p = Process(target=task_exec_func, args=(i, return_dict))
    #         jobs.append(p)
    #         p.start()
    #
    #     # Join
    #     for proc in jobs:
    #         proc.join()
    #
    #     results = return_dict.values()
    #     assert len(results) == number_tasks
    #     for result in results:
    #         assert result
    #         assert isinstance(result, CoreTask)
    #         assert result.logs
    #         assert "accuracy" in result.logs
    #         assert result.results
    #         assert result.results == {"accuracy": "0.45"}
    #         assert result.status == "SUCCESS"

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_run_notebook(self):
        self.__set_variables()
        # Test success case
        test_command = ["jupyter", "notebook", "list"]
        test_ports = ["8888:8888", "9999:9999"]

        # test single ports option before command
        self.task.parse(
            ["task", "run", "--ports", test_ports[0], test_command])

        # test for desired side effects
        assert self.task.args.cmd == test_command
        assert self.task.args.ports == [test_ports[0]]

        # test multiple ports option before command
        self.task.parse([
            "task", "run", "--ports", test_ports[0], "--ports", test_ports[1],
            test_command
        ])

        # test for desired side effects
        assert self.task.args.cmd == test_command
        assert self.task.args.ports == test_ports

        # test proper execution of task run command
        result = self.task.execute()
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "Currently running servers" in result.logs
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

        self.task.parse(["task", "ls"])
        task_ls_command = self.task.execute()

        assert task_ls_command == True

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

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_stop_success(self):
        # 1) Test stop with task_id
        # 2) Test stop with all
        self.__set_variables()

        test_command = ["sh", "-c", "echo yo"]
        test_ports = "8888:8888"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        self.task.parse([
            "task", "run", "--ports", test_ports, "--environment-def",
            test_dockerfile, test_command
        ])

        test_task_obj = self.task.execute()

        # 1) Test option 1
        self.task.parse(["task", "stop", "--id", test_task_obj.id])

        # test for desired side effects
        assert self.task.args.id == test_task_obj.id

        # test when task id is passed to stop it
        task_stop_command = self.task.execute()
        assert task_stop_command == True

        # 2) Test option 2
        self.task.parse(["task", "stop", "--all"])

        # test when all is passed to stop all
        task_stop_command = self.task.execute()
        assert task_stop_command == True

    def test_task_stop_failure_required_args(self):
        self.__set_variables()
        # Passing wrong task id
        self.task.parse(["task", "stop"])
        failed = False
        try:
            _ = self.task.execute()
        except RequiredArgumentMissing:
            failed = True
        assert failed

    def test_task_stop_failure_mutually_exclusive_vars(self):
        self.__set_variables()
        # Passing wrong task id
        self.task.parse(["task", "stop", "--id", "invalid-task-id", "--all"])
        failed = False
        try:
            _ = self.task.execute()
        except MutuallyExclusiveArguments:
            failed = True
        assert failed

    def test_task_stop_failure_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task.parse(["task", "stop" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_task_stop_invalid_task_id(self):
        self.__set_variables()
        # Passing wrong task id
        self.task.parse(["task", "stop", "--id", "invalid-task-id"])

        # test when wrong task id is passed to stop it
        result = self.task.execute()
        assert not result
