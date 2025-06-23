
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

from datmo.config import Config
from datmo.cli.driver.helper import Helper
from datmo.cli.command.environment import EnvironmentCommand
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.snapshot import SnapshotCommand
from datmo.cli.command.run import RunCommand

from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestFlow():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.cli_helper = Helper()

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
        self.environment_command = EnvironmentCommand(self.cli_helper)
        self.run_command = RunCommand(self.cli_helper)
        self.snapshot_command = SnapshotCommand(self.cli_helper)

        # Create test file
        self.filepath = os.path.join(self.snapshot_command.home, "file.txt")
        with open(self.filepath, "wb") as f:
            f.write(to_bytes(str("test")))

    def __environment_setup(self):
        self.environment_command.parse(["environment", "setup"])

        @self.environment_command.cli_helper.input("\n\n\n")
        def dummy(self):
            return self.environment_command.execute()

        environment_setup_result = dummy(self)
        return environment_setup_result

    def __run(self):
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        test_ports = ["8888:8888"]
        self.run_command.parse(["run", "-p", test_ports[0], test_command])
        run_result = self.run_command.execute()
        return run_result

    def __run_ls(self):
        self.run_command.parse(["ls"])
        run_ls_result = self.run_command.execute()
        return run_ls_result

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
        # Step 2: run
        # Step 3: ls
        # Step 4: snapshot create
        # Step 5: snapshot ls
        self.__set_variables()

        # Step 1: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 2: run command
        run_result = self.__run()
        assert run_result

        # Step 3: ls
        run_ls_result = self.__run_ls()
        assert run_ls_result

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
        # Step 3: run
        # Step 4: ls
        # Step 5: snapshot create
        # Step 6: snapshot ls
        self.__set_variables()

        # TODO: TEST more fundamental functions first
        # Step 1: interrupted environment setup
        # @timeout_decorator.timeout(0.0001, use_signals=False)
        # def timed_command_with_interuption():
        #     result = self.__environment_setup()
        #     return result
        #
        # failed = False
        # try:
        #     timed_command_with_interuption()
        # except timeout_decorator.timeout_decorator.TimeoutError:
        #     failed = True
        # assert failed

        # Step 2: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 3: run
        run_result = self.__run()
        assert run_result

        # Step 4: ls
        run_ls_result = self.__run_ls()
        assert run_ls_result

        # Step 5: snapshot create
        snapshot_create_result = self.__snapshot_create()
        assert snapshot_create_result

        # Step 6: snapshot ls
        snapshot_ls_result = self.__snapshot_ls()
        assert snapshot_ls_result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_flow_3(self):
        # Flow interruption in run
        # Step 1: environment setup
        # Step 2: interrupted run
        # Step 3: run
        # Step 4: ls
        # Step 5: snapshot create
        # Step 6: snapshot ls
        self.__set_variables()
        # Step 1: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # TODO: Test more fundamental functions first
        # Step 2: interrupted run
        # @timeout_decorator.timeout(0.0001, use_signals=False)
        # def timed_command_with_interuption():
        #     result = self.__run()
        #     return result
        #
        # failed = False
        # try:
        #     timed_command_with_interuption()
        # except timeout_decorator.timeout_decorator.TimeoutError:
        #     failed = True
        # assert failed

        # Step 3: run
        run_result = self.__run()
        assert run_result

        # Step 4: task ls
        run_ls_result = self.__run_ls()
        assert run_ls_result

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
        # Step 2: run
        # Step 3: ls
        # Step 4: interrupted snapshot create
        # Step 5: snapshot create
        # Step 6: snapshot ls
        self.__set_variables()

        # Step 1: environment setup
        environment_setup_result = self.__environment_setup()
        assert environment_setup_result

        # Step 2: run
        run_result = self.__run()
        assert run_result

        # Step 3: ls
        run_ls_result = self.__run_ls()
        assert run_ls_result

        # TODO: Test more fundamental functions first
        # Step 4: interrupted snapshot create
        # @timeout_decorator.timeout(0.0001, use_signals=False)
        # def timed_command_with_interuption():
        #     result = self.__snapshot_create()
        #     return result
        #
        # failed = False
        # try:
        #     timed_command_with_interuption()
        # except timeout_decorator.timeout_decorator.TimeoutError:
        #     failed = True
        # assert failed
        # snapshot_ls_result = self.__snapshot_ls()
        # assert not snapshot_ls_result

        # Step 5: snapshot create
        snapshot_create_result = self.__snapshot_create()
        assert snapshot_create_result

        # Step 6: snapshot ls
        snapshot_ls_result = self.__snapshot_ls()
        assert snapshot_ls_result
