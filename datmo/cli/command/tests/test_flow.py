from __future__ import print_function

import os
import tempfile
import platform
import timeout_decorator
from io import open

try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.cli.driver.helper import Helper
from datmo.cli.command.environment import EnvironmentCommand
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.snapshot import SnapshotCommand
from datmo.cli.command.task import TaskCommand

from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestFlow():
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
        self.environment_command = EnvironmentCommand(self.temp_dir,
                                                      self.cli_helper)
        self.task_command = TaskCommand(self.temp_dir, self.cli_helper)
        self.snapshot_command = SnapshotCommand(self.temp_dir, self.cli_helper)

        # Create test file
        self.filepath = os.path.join(self.snapshot_command.home, "file.txt")
        with open(self.filepath, "wb") as f:
            f.write(to_bytes(str("test")))

    def __environment_setup(self):
        self.environment_command.parse(["environment", "setup"])

        @self.environment_command.cli_helper.input("1\n")
        def dummy(self):
            return self.environment_command.execute()

        environment_setup_result = dummy(self)
        return environment_setup_result

    def __task_run(self):
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888"]
        self.task_command.parse(
            ["task", "run", "-p", test_ports[0], test_command])
        task_run_result = self.task_command.execute()
        return task_run_result

    def __task_ls(self):
        self.task_command.parse(["task", "ls"])
        task_ls_result = self.task_command.execute()
        return task_ls_result

    def __snapshot_create(self):
        test_message = "creating a snapshot"
        self.snapshot_command.parse(["snapshot", "create", "-m", test_message])

        snapshot_create_result = self.snapshot_command.execute()
        return snapshot_create_result

    def __snapshot_ls(self):
        self.snapshot_command.parse(["snapshot", "ls"])
        snapshot_ls_result = self.snapshot_command.execute()
        return snapshot_ls_result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_flow_1(self):
        # Flow
        # Step 1: environment setup
        # Step 2: task run
        # Step 3: task ls
        # Step 4: snapshot create
        # Step 5: snapshot ls
        self.__set_variables()

        # Step 1: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 2: task run
        task_run_result = self.__task_run()
        assert task_run_result

        # Step 3: task ls
        task_ls_result = self.__task_ls()
        assert task_ls_result

        # Step 4: snapshot create
        snapshot_create_result = self.__snapshot_create()
        assert snapshot_create_result

        # Step 5: snapshot ls
        snapshot_ls_result = self.__snapshot_ls()
        assert snapshot_ls_result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_flow_2(self):
        # Flow interruption in environment
        # Step 1: interrupted environment setup
        # Step 2: environment setup
        # Step 3: task run
        # Step 4: task ls
        # Step 5: snapshot create
        # Step 6: snapshot ls
        self.__set_variables()

        # Step 1: interrupted environment setup
        @timeout_decorator.timeout(0.0001, use_signals=False)
        def timed_command_with_interuption():
            result = self.__environment_setup()
            return result

        failed = False
        try:
            timed_command_with_interuption()
        except timeout_decorator.timeout_decorator.TimeoutError:
            failed = True
        assert failed

        # Step 2: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 3: task run
        task_run_result = self.__task_run()
        assert task_run_result

        # Step 4: task ls
        task_ls_result = self.__task_ls()
        assert task_ls_result

        # Step 5: snapshot create
        snapshot_create_result = self.__snapshot_create()
        assert snapshot_create_result

        # Step 6: snapshot ls
        snapshot_ls_result = self.__snapshot_ls()
        assert snapshot_ls_result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_flow_3(self):
        # Flow interruption in task run
        # Step 1: environment setup
        # Step 2: interrupted task run
        # Step 3: task run
        # Step 4: task ls
        # Step 5: snapshot create
        # Step 6: snapshot ls
        self.__set_variables()
        # Step 1: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 2: interrupted task run
        @timeout_decorator.timeout(0.0001, use_signals=False)
        def timed_command_with_interuption():
            result = self.__task_run()
            return result

        failed = False
        try:
            timed_command_with_interuption()
        except timeout_decorator.timeout_decorator.TimeoutError:
            failed = True
        assert failed

        # Step 3: task run
        task_run_result = self.__task_run()
        assert task_run_result

        # Step 4: task ls
        task_ls_result = self.__task_ls()
        assert task_ls_result

        # Step 5: snapshot create
        snapshot_create_result = self.__snapshot_create()
        assert snapshot_create_result

        # Step 6: snapshot ls
        snapshot_ls_result = self.__snapshot_ls()
        assert snapshot_ls_result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_flow_4(self):
        # Flow interruption in snapshot create
        # Step 1: environment setup
        # Step 2: task run
        # Step 3: task ls
        # Step 4: interrupted snapshot create
        # Step 5: snapshot create
        # Step 6: snapshot ls
        self.__set_variables()

        # Step 1: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 2: task run
        task_run_result = self.__task_run()
        assert task_run_result

        # Step 3: task ls
        task_ls_result = self.__task_ls()
        assert task_ls_result

        # Step 4: interrupted snapshot create
        @timeout_decorator.timeout(0.0001, use_signals=False)
        def timed_command_with_interuption():
            result = self.__snapshot_create()
            return result

        failed = False
        try:
            timed_command_with_interuption()
        except timeout_decorator.timeout_decorator.TimeoutError:
            failed = True
        assert failed
        snapshot_ls_result = self.__snapshot_ls()
        assert not snapshot_ls_result

        # Step 5: snapshot create
        snapshot_create_result = self.__snapshot_create()
        assert snapshot_create_result

        # Step 6: snapshot ls
        snapshot_ls_result = self.__snapshot_ls()
        assert snapshot_ls_result
