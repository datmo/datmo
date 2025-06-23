"""
Tests for RunCommand
"""

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
from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.run import RunCommand
from datmo.core.entity.run import Run
from datmo.core.util.exceptions import DoesNotExist, \
    MutuallyExclusiveArguments, RequiredArgumentMissing
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestRunCommand():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.cli_helper = Helper()
        self.snapshot_dict = {
            "id": "test",
            "model_id": "my_model",
            "message": "my message",
            "code_id": "my_code_id",
            "environment_id": "my_environment_id",
            "file_collection_id": "my file collection",
            "config": {
                "test": 0.56
            },
            "stats": {
                "test": 0.34
            }
        }
        self.task_dict = {
            "id": "test",
            "model_id": "my_model",
            "command": "python test.py"
        }

    def teardown_method(self):
        pass

    def __set_variables(self):
        self.project_command = ProjectCommand(self.cli_helper)
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        dummy(self)

        self.run_command = RunCommand(self.cli_helper)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

    def test_run_should_fail1(self):
        self.__set_variables()
        # Test failure case
        self.run_command.parse(["run"])
        result = self.run_command.execute()
        assert not result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()
        # Test failure command execute
        test_command = ["yo", "yo"]
        self.run_command.parse(["run", test_command])
        result = self.run_command.execute()
        assert result
        # Test success case
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"

        # test for single set of ports
        self.run_command.parse([
            "run", "--ports", test_ports[0], "--environment-paths",
            test_dockerfile, "--mem-limit", test_mem_limit, test_command
        ])
        # test for desired side effects
        assert self.run_command.args.cmd == test_command
        assert self.run_command.args.ports == [test_ports[0]]
        assert self.run_command.args.environment_paths == [test_dockerfile]
        assert self.run_command.args.mem_limit == test_mem_limit

        self.run_command.parse([
            "run", "-p", test_ports[0], "-p", test_ports[1],
            "--environment-paths", test_dockerfile, "--mem-limit",
            test_mem_limit, test_command
        ])
        # test for desired side effects
        assert self.run_command.args.cmd == test_command
        assert self.run_command.args.ports == test_ports
        assert self.run_command.args.environment_paths == [test_dockerfile]
        assert self.run_command.args.mem_limit == test_mem_limit

        # test proper execution of run command
        result = self.run_command.execute()
        time.sleep(1)
        assert result
        assert isinstance(result, Run)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"
        assert result.start_time
        assert result.end_time
        assert result.duration
        assert result.core_snapshot_id
        assert result.core_snapshot_id == result.after_snapshot_id
        assert result.environment_id

        # teardown
        self.run_command.parse(["stop", "--all"])
        # test when all is passed to stop all
        self.run_command.execute()

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_data_dir(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()
        # Test success case
        test_filename = "script.py"
        test_command = ["python", test_filename]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"
        # Test success for run with directory being passed
        test_data_dir_1 = os.path.join(
            tempfile.mkdtemp(dir=test_datmo_dir), "data1")
        os.mkdir(test_data_dir_1)
        test_data_dir_2 = os.path.join(
            tempfile.mkdtemp(dir=test_datmo_dir), "data2")
        os.mkdir(test_data_dir_2)
        with open(os.path.join(test_data_dir_1, "file.txt"), "wb") as f:
            f.write(to_bytes('my initial line in 1\n'))
        with open(os.path.join(test_data_dir_2, "file.txt"), "wb") as f:
            f.write(to_bytes('my initial line in 2\n'))
        test_filename = "script.py"
        test_filepath = os.path.join(self.temp_dir, test_filename)
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("print('hello')\n"))
            f.write(to_bytes("import shutil\n"))

            f.write(
                to_bytes(
                    "with open(os.path.join('/data', 'data1', 'file.txt'), 'a') as f:\n"
                ))
            f.write(to_bytes("    f.write('my test file in 1')\n"))

            f.write(
                to_bytes(
                    "with open(os.path.join('/data', 'data2', 'file.txt'), 'a') as f:\n"
                ))
            f.write(to_bytes("    f.write('my test file in 2')\n"))

        self.run_command.parse([
            "run", "--environment-paths", test_dockerfile, "--data",
            test_data_dir_1, "--data", test_data_dir_2, "--mem-limit",
            test_mem_limit, test_command
        ])

        # test proper execution of run command
        result = self.run_command.execute()
        time.sleep(1)
        assert result
        assert isinstance(result, Run)
        assert result.logs
        assert result.status == "SUCCESS"
        assert result.start_time
        assert result.end_time
        assert result.duration
        assert result.core_snapshot_id
        assert result.core_snapshot_id == result.after_snapshot_id
        assert result.environment_id
        assert "my initial line in 1" in open(
            os.path.join(test_data_dir_1, "file.txt"), "r").read()
        assert "my test file in 1" in open(
            os.path.join(test_data_dir_1, "file.txt"), "r").read()
        assert "my initial line in 2" in open(
            os.path.join(test_data_dir_2, "file.txt"), "r").read()
        assert "my test file in 2" in open(
            os.path.join(test_data_dir_2, "file.txt"), "r").read()
        # teardown
        self.run_command.parse(["stop", "--all"])
        # test when all is passed to stop all
        self.run_command.execute()

        # test failure
        test_data_dir_dne = os.path.join(
            tempfile.mkdtemp(dir=test_datmo_dir), "data_dne")
        self.run_command.parse([
            "run", "--environment-paths", test_dockerfile, "--data",
            test_data_dir_dne
        ])
        result = self.run_command.execute()
        assert not result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_string_command(self):
        # TODO: Adding test with `--interactive` argument and terminate inside container
        self.__set_variables()
        # Test success case
        test_command = "sh -c 'echo accuracy:0.45'"
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"
        self.run_command.parse([
            "run", "--ports", test_ports[0], "--ports", test_ports[1],
            "--environment-paths", test_dockerfile, "--mem-limit",
            test_mem_limit, test_command
        ])
        # test for desired side effects
        assert self.run_command.args.cmd == test_command
        assert self.run_command.args.ports == test_ports
        assert self.run_command.args.environment_paths == [test_dockerfile]
        assert self.run_command.args.mem_limit == test_mem_limit

        # test proper execution of run command
        result = self.run_command.execute()
        assert result
        assert isinstance(result, Run)
        assert result.logs
        assert "accuracy" in result.logs
        assert result.results
        assert result.results == {"accuracy": "0.45"}
        assert result.status == "SUCCESS"
        assert result.start_time
        assert result.end_time
        assert result.duration
        assert result.core_snapshot_id
        assert result.core_snapshot_id == result.after_snapshot_id
        assert result.environment_id
        assert result

        # teardown
        self.run_command.parse(["stop", "--all"])
        # test when all is passed to stop all
        self.run_command.execute()

    # def test_multiple_concurrent_run_command(self):
    #     test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
    #     test_command = ["sh", "-c", "echo accuracy:0.45"]
    #     manager = Manager()
    #     return_dict = manager.dict()
    #
    #     def run_exec_func(procnum, return_dict):
    #         print("Creating Task object")
    #         run = RunCommand(self.temp_dir, self.cli_helper)
    #         print("Parsing command")
    #         run.parse(
    #             ["run", "--environment-paths", test_dockerfile, test_command])
    #         print("Executing command")
    #         result = run.execute()
    #         return_dict[procnum] = result
    #
    #     self.__set_variables()
    #     test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
    #
    #     # Run all three runs in parallel
    #     jobs = []
    #     number_runs = 3
    #     for i in range(number_runs):
    #         p = Process(target=run_exec_func, args=(i, return_dict))
    #         jobs.append(p)
    #         p.start()
    #
    #     # Join
    #     for proc in jobs:
    #         proc.join()
    #
    #     results = return_dict.values()
    #     assert len(results) == number_runs
    #     for result in results:
    #         assert result
    #         assert isinstance(result, CoreTask)
    #         assert result.logs
    #         assert "accuracy" in result.logs
    #         assert result.results
    #         assert result.results == {"accuracy": "0.45"}
    #         assert result.status == "SUCCESS"

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_notebook(self):
        self.__set_variables()
        # Update the default Dockerfile to test with
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM nbgallery/jupyter-alpine:latest"))

        # Test success case
        test_command = ["jupyter", "notebook", "list"]
        test_ports = ["8888:8888", "9999:9999"]
        test_mem_limit = "4g"

        # test single ports option before command
        self.run_command.parse([
            "run", "--ports", test_ports[0], "--mem-limit", test_mem_limit,
            test_command
        ])

        # test for desired side effects
        assert self.run_command.args.cmd == test_command
        assert self.run_command.args.ports == [test_ports[0]]
        assert self.run_command.args.mem_limit == test_mem_limit

        # test multiple ports option before command
        self.run_command.parse([
            "run", "--ports", test_ports[0], "--ports", test_ports[1],
            "--mem-limit", test_mem_limit, "--environment-paths",
            self.env_def_path, test_command
        ])

        # test for desired side effects
        assert self.run_command.args.cmd == test_command
        assert self.run_command.args.ports == test_ports
        assert self.run_command.args.mem_limit == test_mem_limit

        # test proper execution of run command
        result = self.run_command.execute()
        assert result
        assert isinstance(result, Run)
        assert result.logs
        assert "Currently running servers" in result.logs
        assert result.status == "SUCCESS"

        # teardown
        self.run_command.parse(["stop", "--all"])
        # test when all is passed to stop all
        self.run_command.execute()

    def test_run_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.run_command.parse(["run" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_ls(self):
        self.__set_variables()

        # Running a task
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"

        # test for single set of ports
        self.run_command.parse([
            "run", "--ports", test_ports[0], "--environment-paths",
            test_dockerfile, "--mem-limit", test_mem_limit, test_command
        ])

        # test proper execution of run command
        self.run_command.execute()
        # Test defaults
        self.run_command.parse(["ls"])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"

        # Test failure (format)
        failed = False
        try:
            self.run_command.parse(["ls", "--format"])
        except ArgumentError:
            failed = True
        assert failed

        # Test success format csv
        self.run_command.parse(["ls", "--format", "csv"])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"

        # Test success format csv, download default
        self.run_command.parse(["ls", "--format", "csv", "--download"])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"
        test_wildcard = os.path.join(os.getcwd(), "run_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format csv, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.run_command.parse([
            "ls", "--format", "csv", "--download", "--download-path", test_path
        ])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

        # Test success format table
        self.run_command.parse(["ls"])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"

        # Test success format table, download default
        self.run_command.parse(["ls", "--download"])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"
        test_wildcard = os.path.join(os.getcwd(), "run_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format table, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.run_command.parse(
            ["ls", "--download", "--download-path", test_path])
        run_objs = self.run_command.execute()
        assert run_objs
        assert run_objs[0].status == "SUCCESS"
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

    def test_run_ls_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.run_command.parse(["ls" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_stop_success(self):
        # 1) Test stop with task_id
        # 2) Test stop with all
        self.__set_variables()

        test_command = ["sh", "-c", "echo yo"]
        test_ports = "8888:8888"
        test_mem_limit = "4g"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        self.run_command.parse([
            "run", "--ports", test_ports, "--environment-paths",
            test_dockerfile, "--mem-limit", test_mem_limit, test_command
        ])

        test_run_obj = self.run_command.execute()

        # 1) Test option 1
        self.run_command.parse(["stop", "--id", test_run_obj.id])

        # test for desired side effects
        assert self.run_command.args.id == test_run_obj.id

        # test when task id is passed to stop it
        run_stop_command = self.run_command.execute()
        assert run_stop_command == True

        # 2) Test option 2
        self.run_command.parse(["stop", "--all"])

        # test when all is passed to stop all
        run_stop_command = self.run_command.execute()
        assert run_stop_command == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_stop_failure_required_args(self):
        self.__set_variables()
        # Passing wrong task id
        self.run_command.parse(["stop"])
        failed = False
        try:
            _ = self.run_command.execute()
        except RequiredArgumentMissing:
            failed = True
        assert failed

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_stop_failure_mutually_exclusive_vars(self):
        self.__set_variables()
        # Passing wrong task id
        self.run_command.parse(["stop", "--id", "invalid-task-id", "--all"])
        failed = False
        try:
            _ = self.run_command.execute()
        except MutuallyExclusiveArguments:
            failed = True
        assert failed

    def test_run_stop_failure_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.run_command.parse(["stop" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_run_stop_invalid_task_id(self):
        self.__set_variables()
        # Passing wrong task id
        self.run_command.parse(["stop", "--id", "invalid-task-id"])

        # test when wrong task id is passed to stop it
        result = self.run_command.execute()
        assert not result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_delete_success(self):
        # 1) Test delete with run_id
        self.__set_variables()

        test_command = ["sh", "-c", "echo yo"]
        test_ports = "8888:8888"
        test_mem_limit = "4g"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")

        self.run_command.parse([
            "run", "--ports", test_ports, "--environment-paths",
            test_dockerfile, "--mem-limit", test_mem_limit, test_command
        ])

        test_run_obj = self.run_command.execute()

        # 1) Test option 1
        self.run_command.parse(["delete", test_run_obj.id])

        # test for desired side effects
        assert self.run_command.args.id == test_run_obj.id

        # test when task id is passed to delete it
        run_delete_command = self.run_command.execute()
        assert run_delete_command == True

    def test_run_delete_invalid_task_id(self):
        self.__set_variables()
        # Passing wrong task id
        self.run_command.parse(["delete", "invalid-task-id"])

        # test when wrong task id is passed to stop it
        result = self.run_command.execute()
        assert not result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_rerun(self):
        self.__set_variables()
        # Test success case
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888", "9999:9999"]
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        test_mem_limit = "4g"

        # test for single set of ports
        self.run_command.parse([
            "run", "-p", test_ports[0], "--environment-paths", test_dockerfile,
            "--mem-limit", test_mem_limit, test_command
        ])

        # test proper execution of run command
        run_obj = self.run_command.execute()
        run_id = run_obj.id
        # 1. Test success rerun
        self.run_command.parse(["rerun", run_id])
        result_run_obj = self.run_command.execute()
        assert result_run_obj
        assert isinstance(result_run_obj, Run)
        assert result_run_obj.command == run_obj.command
        assert result_run_obj.status == "SUCCESS"
        assert result_run_obj.logs
        assert result_run_obj.before_snapshot_id == run_obj.before_snapshot_id

        # teardown
        self.run_command.parse(["stop", "--all"])
        # test when all is passed to stop all
        self.run_command.execute()

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_rerun_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.run_command.parse(["rerun", "foobar"])
            self.run_command.execute()
        except DoesNotExist:
            exception_thrown = True
        assert exception_thrown
