"""
Tests for Project Commands
"""

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
from datmo import __version__
from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.snapshot import SnapshotCommand
from datmo.core.entity.snapshot import Snapshot
from datmo.cli.command.run import RunCommand
from datmo.core.controller.task import TaskController
from datmo.core.util.exceptions import UnrecognizedCLIArgument
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestProjectCommand():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.cli_helper = Helper()
        self.project_command = ProjectCommand(self.cli_helper)

    def teardown_method(self):
        pass

    def test_init_create_success_default_name_no_description_no_environment(
            self):
        self.project_command.parse(["init"])

        # Test when environment is created
        @self.project_command.cli_helper.input("\n\ny\n\n\n\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)

        # Ensure that the name and description are current
        _, default_name = os.path.split(
            self.project_command.project_controller.home)
        assert result
        assert result.name == default_name
        assert result.description == None
        # Ensure environment is correct
        definition_filepath = os.path.join(
            self.project_command.project_controller.environment_driver.
            environment_directory_path, "Dockerfile")
        assert os.path.isfile(definition_filepath)
        assert "FROM datmo/python-base:cpu-py27" in open(
            definition_filepath, "r").read()

    def test_init_create_success_force(self):
        self.project_command.parse(["init", "--force"])

        result = self.project_command.execute()
        assert result
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))

    def test_init_create_success_no_environment(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        # Test when environment is not created
        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)

        definition_filepath = os.path.join(
            self.project_command.project_controller.environment_driver.
            environment_directory_path, "Dockerfile")

        assert result
        assert not os.path.isfile(definition_filepath)
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result.name == test_name
        assert result.description == test_description

    def test_init_create_success_environment(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])
        # Test when environment is created
        @self.project_command.cli_helper.input("y\n\n\n\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)

        definition_filepath = os.path.join(
            self.project_command.project_controller.environment_driver.
            environment_directory_path, "Dockerfile")

        assert result
        assert os.path.isfile(definition_filepath)
        assert "FROM datmo/python-base:cpu-py27" in open(
            definition_filepath, "r").read()

        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result.name == test_name
        assert result.description == test_description

    def test_init_create_success_blank(self):
        self.project_command.parse(["init", "--name", "", "--description", ""])
        # test if prompt opens
        @self.project_command.cli_helper.input("\n\n\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)
        assert result
        assert result.name
        assert not result.description

    def test_init_update_force_success(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)

        self.project_command.parse(["init", "--force"])

        result_2 = self.project_command.execute()
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id

    def test_init_update_success(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)
        updated_name = "foobar2"
        updated_description = "test model 2"
        self.project_command.parse([
            "init", "--name", updated_name, "--description",
            updated_description
        ])

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == updated_name
        assert result_2.description == updated_description

    def test_init_update_success_only_name(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)
        updated_name = "foobar2"
        self.project_command.parse(
            ["init", "--name", updated_name, "--description", ""])

        @self.project_command.cli_helper.input("\n\n")
        def dummy(self):
            return self.project_command.execute()

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == updated_name
        assert result_2.description == result_1.description

    def test_init_update_success_only_description(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        result_1 = dummy(self)
        updated_description = "test model 2"
        self.project_command.parse(
            ["init", "--name", "", "--description", updated_description])

        @self.project_command.cli_helper.input("\n\n")
        def dummy(self):
            return self.project_command.execute()

        result_2 = dummy(self)
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert result_2.id == result_1.id
        assert result_2.name == result_1.name
        assert result_2.description == updated_description

    def test_init_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["init", "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_version(self):
        self.project_command.parse(["version"])
        result = self.project_command.execute()
        # test for desired side effects
        assert __version__ in result

    def test_version_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["version", "--foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_status_basic(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = result
        assert isinstance(status_dict, dict)
        assert not current_snapshot
        assert not latest_snapshot_user_generated
        assert not latest_snapshot_auto_generated
        assert unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

    def test_status_user_generated_snapshot(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        # Create a snapshot
        self.snapshot_command = SnapshotCommand(self.cli_helper)
        with open(os.path.join(self.project_command.home, "test.py"),
                  "wb") as f:
            f.write(to_bytes(str("import xgboost")))
        self.snapshot_command.parse(
            ["snapshot", "create", "--message", "test"])
        snapshot_obj = self.snapshot_command.execute()

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = result
        assert isinstance(status_dict, dict)
        assert isinstance(current_snapshot, Snapshot)
        assert isinstance(latest_snapshot_user_generated, Snapshot)
        assert snapshot_obj == latest_snapshot_user_generated
        assert current_snapshot == latest_snapshot_user_generated
        assert not latest_snapshot_auto_generated
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_status_autogenerated_snapshot(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        self.run_command = RunCommand(self.cli_helper)
        self.task_controller = TaskController()

        # Create and run a task and test if task is shown
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        self.run_command.parse(["run", test_command])

        updated_first_task = self.run_command.execute()
        before_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_first_task.before_snapshot_id)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_first_task.after_snapshot_id)
        before_environment_obj = self.task_controller.dal.environment.get_by_id(
            before_snapshot_obj.environment_id)
        after_environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        assert before_environment_obj == after_environment_obj

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            result

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == test_name
        assert status_dict['description'] == test_description
        assert isinstance(status_dict['config'], dict)
        assert isinstance(current_snapshot, Snapshot)
        assert not latest_snapshot_user_generated
        assert isinstance(latest_snapshot_auto_generated, Snapshot)
        # current snapshot is the before snapshot for the run
        assert current_snapshot == before_snapshot_obj
        assert current_snapshot != latest_snapshot_auto_generated
        # latest autogenerated snapshot is the after snapshot id
        assert latest_snapshot_auto_generated == after_snapshot_obj
        # autogenerated snapshot is after the user generated snapshot
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

        # Create a snapshot
        self.snapshot_command = SnapshotCommand(self.cli_helper)
        with open(os.path.join(self.project_command.home, "test.py"),
                  "wb") as f:
            f.write(to_bytes(str("import xgboost")))
        self.snapshot_command.parse(
            ["snapshot", "create", "--message", "test"])
        first_snapshot = self.snapshot_command.execute()

        # Create and run a task and test if task is shown
        test_command = ["sh", "-c", "echo accuracy:0.45"]
        self.run_command.parse(["run", test_command])

        updated_second_task = self.run_command.execute()
        before_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_second_task.before_snapshot_id)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_second_task.after_snapshot_id)
        before_environment_obj = self.task_controller.dal.environment.get_by_id(
            before_snapshot_obj.environment_id)
        after_environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        assert before_environment_obj == after_environment_obj

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            result

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == test_name
        assert status_dict['description'] == test_description
        assert isinstance(status_dict['config'], dict)
        assert isinstance(current_snapshot, Snapshot)
        assert isinstance(latest_snapshot_user_generated, Snapshot)
        assert latest_snapshot_user_generated == first_snapshot
        assert isinstance(latest_snapshot_auto_generated, Snapshot)
        # current snapshot is the before snapshot for the run
        assert current_snapshot == before_snapshot_obj
        assert current_snapshot == latest_snapshot_user_generated
        assert current_snapshot != latest_snapshot_auto_generated
        # latest autogenerated snapshot is the after snapshot id
        assert latest_snapshot_auto_generated == after_snapshot_obj
        assert latest_snapshot_auto_generated != latest_snapshot_user_generated
        # user generated snapshot is not associated with any before or after snapshot
        assert latest_snapshot_user_generated == before_snapshot_obj
        assert latest_snapshot_user_generated != after_snapshot_obj
        # autogenerated snapshot is after the user generated snapshot
        assert latest_snapshot_auto_generated.created_at > latest_snapshot_user_generated.created_at
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

        # Check if the same snapshot is given back when created
        self.snapshot_command.parse(
            ["snapshot", "create", "--message", "test"])
        new_snapshot = self.snapshot_command.execute()
        assert current_snapshot == new_snapshot

        # Create a user generated snapshot after some changes
        with open(os.path.join(self.project_command.home, "new.py"),
                  "wb") as f:
            f.write(to_bytes(str("import xgboost")))
        self.snapshot_command.parse(
            ["snapshot", "create", "--message", "test"])
        new_snapshot = self.snapshot_command.execute()
        # ensure we created a new snapshot
        assert current_snapshot != new_snapshot

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            result

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == test_name
        assert status_dict['description'] == test_description
        assert isinstance(status_dict['config'], dict)
        assert isinstance(current_snapshot, Snapshot)
        assert isinstance(latest_snapshot_user_generated, Snapshot)
        # current snapshot is the latest user generated one
        assert current_snapshot == latest_snapshot_user_generated
        # latest autogenerated snapshot is not the user generated one
        assert latest_snapshot_auto_generated != latest_snapshot_user_generated
        # autogenerated snapshot is after the user generated snapshot
        assert latest_snapshot_user_generated.created_at > latest_snapshot_auto_generated.created_at
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

        # Create a snapshot from the auto generated one and ensure they are the same
        self.run_command = RunCommand(self.cli_helper)
        self.task_controller = TaskController()

        test_command = ["sh", "-c", "echo accuracy:0.45"]
        self.run_command.parse(["run", test_command])
        updated_third_task = self.run_command.execute()
        before_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_third_task.before_snapshot_id)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_third_task.after_snapshot_id)
        self.snapshot_command.parse([
            "snapshot", "create", "--run-id", updated_third_task.id,
            "--message", "test"
        ])
        converted_snapshot = self.snapshot_command.execute()

        self.project_command.parse(["status"])
        result = self.project_command.execute()
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            result

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == test_name
        assert status_dict['description'] == test_description
        assert isinstance(status_dict['config'], dict)
        assert isinstance(current_snapshot, Snapshot)
        assert isinstance(latest_snapshot_user_generated, Snapshot)
        assert isinstance(latest_snapshot_auto_generated, Snapshot)
        # current snapshot is the before snapshot for the run
        assert current_snapshot == before_snapshot_obj
        assert current_snapshot != latest_snapshot_user_generated
        # latest user generated snapshot is the same as that created by the run
        assert converted_snapshot == latest_snapshot_user_generated
        assert latest_snapshot_user_generated == after_snapshot_obj
        # latest user generated converted the latest task so latest generate is from the last task
        assert latest_snapshot_user_generated.created_at > latest_snapshot_auto_generated.created_at
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

    def test_status_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["status", "--foobar"])
        except UnrecognizedCLIArgument:
            exception_thrown = True
        assert exception_thrown

    def test_cleanup(self):
        test_name = "foobar"
        test_description = "test model"
        self.project_command.parse(
            ["init", "--name", test_name, "--description", test_description])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        self.project_command.parse(["cleanup"])

        @self.project_command.cli_helper.input("y\n\n")
        def dummy(self):
            return self.project_command.execute()

        result = dummy(self)
        assert not os.path.exists(os.path.join(self.temp_dir, '.datmo'))
        assert isinstance(result, bool)
        assert result

    def test_cleanup_invalid_arg(self):
        exception_thrown = False
        try:
            self.project_command.parse(["cleanup", "--foobar"])
        except UnrecognizedCLIArgument:
            exception_thrown = True
        assert exception_thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_dashboard(self):
        # test dashboard command
        self.project_command.parse(["dashboard"])

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(timed_run_result):
            if self.project_command.execute():
                return timed_run_result

        # Failure case not initialized
        timed_run_result = False
        try:
            timed_run_result = timed_run(timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert not timed_run_result

        # Success case after initialization
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])

        @self.project_command.cli_helper.input("\n")
        def dummy(self):
            return self.project_command.execute()

        _ = dummy(self)

        self.project_command.parse(["dashboard"])
        timed_run_result = False
        try:
            timed_run_result = timed_run(timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result
