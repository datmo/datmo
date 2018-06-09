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
import glob
import time
import tempfile
import platform
from argparse import ArgumentError

from multiprocessing import Process, Manager
from io import open
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

from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.task import TaskCommand
from datmo.core.entity.task import Task as CoreTask
from datmo.core.util.exceptions import ProjectNotInitialized, MutuallyExclusiveArguments, RequiredArgumentMissing, SessionDoesNotExist
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestTaskCommand():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_method(self):
        pass

    def __set_variables(self):
        self.project_command = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        dummy(self)

        self.task_command = TaskCommand(self.temp_dir, self.cli_helper)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

    def test_task_project_not_init(self):
        failed = False
        try:
            self.task_command = TaskCommand(self.temp_dir, self.cli_helper)
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_task_command(self):
        self.__set_variables()
        self.task_command.parse(["task"])
        assert self.task_command.execute()

    def test_task_run_should_fail1(self):
        self.__set_variables()
        # Test failure case
        self.task_command.parse(["task", "run"])
        result = self.task_command.execute()
        assert not result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_run(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()
        # Test failure command execute
        test_command = ["yo", "yo"]
        self.task_command.parse(["task", "run", test_command])
        result = self.task_command.execute()
        assert result
        # Test success case
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"

        # test for single set of ports
        self.task_command.parse([
            "task", "run", "--ports", test_ports[0], "--environment-paths",
            test_dockerfile, "--mem-limit", test_mem_limit, test_command
        ])
        # test for desired side effects
        assert self.task_command.args.cmd == test_command
        assert self.task_command.args.ports == [test_ports[0]]
        assert self.task_command.args.environment_paths == [test_dockerfile]
        assert self.task_command.args.mem_limit == test_mem_limit

        self.task_command.parse([
            "task", "run", "-p", test_ports[0], "-p", test_ports[1],
            "--environment-paths", test_dockerfile, "--mem-limit",
            test_mem_limit, test_command
        ])
        # test for desired side effects
        assert self.task_command.args.cmd == test_command
        assert self.task_command.args.ports == test_ports
        assert self.task_command.args.environment_paths == [test_dockerfile]
        assert self.task_command.args.mem_limit == test_mem_limit

        # test proper execution of task run command
        result = self.task_command.execute()
        time.sleep(1)
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"

        # teardown
        self.task_command.parse(["task", "stop", "--all"])
        # test when all is passed to stop all
        task_stop_command = self.task_command.execute()

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_run_string_command(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()
        # Test success case
        test_command = "sh -c 'echo accuracy:0.45'"
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"
        self.task_command.parse([
            "task", "run", "--ports", test_ports[0], "--ports", test_ports[1],
            "--environment-paths", test_dockerfile, "--mem-limit",
            test_mem_limit, test_command
        ])
        # test for desired side effects
        assert self.task_command.args.cmd == test_command
        assert self.task_command.args.ports == test_ports
        assert self.task_command.args.environment_paths == [test_dockerfile]
        assert self.task_command.args.mem_limit == test_mem_limit

        # test proper execution of task run command
        result = self.task_command.execute()
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"

        # teardown
        self.task_command.parse(["task", "stop", "--all"])
        # test when all is passed to stop all
        task_stop_command = self.task_command.execute()

    # def test_multiple_concurrent_task_run_command(self):
    #     test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
    #     test_command = ["sh", "-c", "echo accuracy:0.45"]
    #     manager = Manager()
    #     return_dict = manager.dict()
    #
    #     def task_exec_func(procnum, return_dict):
    #         print("Creating Task object")
    #         task = TaskCommand(self.temp_dir, self.cli_helper)
    #         print("Parsing command")
    #         task.parse(
    #             ["task", "run", "--environment-paths", test_dockerfile, test_command])
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
        # Update the default Dockerfile to test with
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM nbgallery/jupyter-alpine:latest"))

        # Test success case
        test_command = ["jupyter", "notebook", "list"]
        test_ports = ["8888:8888", "9999:9999"]
        test_mem_limit = "4g"

        # test single ports option before command
        self.task_command.parse([
            "task", "run", "--ports", test_ports[0], "--mem-limit",
            test_mem_limit, test_command
        ])

        # test for desired side effects
        assert self.task_command.args.cmd == test_command
        assert self.task_command.args.ports == [test_ports[0]]
        assert self.task_command.args.mem_limit == test_mem_limit

        # test multiple ports option before command
        self.task_command.parse([
            "task", "run", "--ports", test_ports[0], "--ports", test_ports[1],
            "--mem-limit", test_mem_limit, test_command
        ])

        # test for desired side effects
        assert self.task_command.args.cmd == test_command
        assert self.task_command.args.ports == test_ports
        assert self.task_command.args.mem_limit == test_mem_limit

        # test proper execution of task run command
        result = self.task_command.execute()
        assert result
        assert isinstance(result, CoreTask)
        assert result.logs
        assert "Currently running servers" in result.logs
        assert result.status == "SUCCESS"

        # teardown
        self.task_command.parse(["task", "stop", "--all"])
        # test when all is passed to stop all
        task_stop_command = self.task_command.execute()

    def test_task_run_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task_command.parse(["task", "run" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_task_ls(self):
        self.__set_variables()

        # Test defaults
        self.task_command.parse(["task", "ls"])
        task_objs = self.task_command.execute()
        assert task_objs == []

        test_session_id = 'test_session_id'
        self.task_command.parse(
            ["task", "ls", "--session-id", test_session_id])

        # test for desired side effects
        assert self.task_command.args.session_id == test_session_id

        # Test failure no session
        failed = False
        try:
            self.task_command.execute()
        except SessionDoesNotExist:
            failed = True
        assert failed

        # Test failure (format)
        failed = False
        try:
            self.task_command.parse(["task", "ls", "--format"])
        except ArgumentError:
            failed = True
        assert failed

        # Test success format csv
        self.task_command.parse(["task", "ls", "--format", "csv"])
        task_objs = self.task_command.execute()
        assert task_objs == []

        # Test success format csv, download default
        self.task_command.parse(
            ["task", "ls", "--format", "csv", "--download"])
        task_objs = self.task_command.execute()
        assert task_objs == []
        test_wildcard = os.path.join(os.getcwd(), "task_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format csv, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.task_command.parse([
            "task", "ls", "--format", "csv", "--download", "--download-path",
            test_path
        ])
        task_objs = self.task_command.execute()
        assert task_objs == []
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

        # Test success format table
        self.task_command.parse(["task", "ls"])
        task_objs = self.task_command.execute()
        assert task_objs == []

        # Test success format table, download default
        self.task_command.parse(["task", "ls", "--download"])
        task_objs = self.task_command.execute()
        assert task_objs == []
        test_wildcard = os.path.join(os.getcwd(), "task_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format table, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.task_command.parse(
            ["task", "ls", "--download", "--download-path", test_path])
        task_objs = self.task_command.execute()
        assert task_objs == []
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

    def test_task_ls_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task_command.parse(["task", "ls" "--foobar", "foobar"])
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
        test_mem_limit = "4g"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        self.task_command.parse([
            "task", "run", "--ports", test_ports, "--environment-paths",
            test_dockerfile, "--mem-limit", test_mem_limit, test_command
        ])

        test_task_obj = self.task_command.execute()

        # 1) Test option 1
        self.task_command.parse(["task", "stop", "--id", test_task_obj.id])

        # test for desired side effects
        assert self.task_command.args.id == test_task_obj.id

        # test when task id is passed to stop it
        task_stop_command = self.task_command.execute()
        assert task_stop_command == True

        # 2) Test option 2
        self.task_command.parse(["task", "stop", "--all"])

        # test when all is passed to stop all
        task_stop_command = self.task_command.execute()
        assert task_stop_command == True

    def test_task_stop_failure_required_args(self):
        self.__set_variables()
        # Passing wrong task id
        self.task_command.parse(["task", "stop"])
        failed = False
        try:
            _ = self.task_command.execute()
        except RequiredArgumentMissing:
            failed = True
        assert failed

    def test_task_stop_failure_mutually_exclusive_vars(self):
        self.__set_variables()
        # Passing wrong task id
        self.task_command.parse(
            ["task", "stop", "--id", "invalid-task-id", "--all"])
        failed = False
        try:
            _ = self.task_command.execute()
        except MutuallyExclusiveArguments:
            failed = True
        assert failed

    def test_task_stop_failure_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.task_command.parse(["task", "stop" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_task_stop_invalid_task_id(self):
        self.__set_variables()
        # Passing wrong task id
        self.task_command.parse(["task", "stop", "--id", "invalid-task-id"])

        # test when wrong task id is passed to stop it
        result = self.task_command.execute()
        assert not result
