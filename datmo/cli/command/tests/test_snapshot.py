"""
Tests for SnapshotCommand
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
from datmo.cli.command.snapshot import SnapshotCommand
from datmo.cli.command.task import TaskCommand
from datmo.core.util.exceptions import (ProjectNotInitializedException,
                                        MutuallyExclusiveArguments,
                                        SnapshotCreateFromTaskArgs)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestSnapshot():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        self.project = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project.execute()
        self.snapshot = SnapshotCommand(self.temp_dir, self.cli_helper)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        self.config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(self.config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        self.stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(self.stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create test file
        self.filepath = os.path.join(self.snapshot.home, "file.txt")
        with open(self.filepath, "w") as f:
            f.write(to_unicode(str("test")))

        # Create another test file
        self.filepath_2 = os.path.join(self.snapshot.home, "file2.txt")
        with open(self.filepath_2, "w") as f:
            f.write(to_unicode(str("test")))

    def test_snapshot_project_not_init(self):
        failed = False
        try:
            self.snapshot = SnapshotCommand(self.temp_dir, self.cli_helper)
        except ProjectNotInitializedException:
            failed = True
        assert failed

    def test_snapshot_help(self):
        self.__set_variables()
        print(
            "\n====================================== datmo snapshot ==========================\n"
        )

        self.snapshot.parse(["snapshot"])
        assert self.snapshot.execute()

        print(
            "\n====================================== datmo snapshot --help ==========================\n"
        )

        self.snapshot.parse(["snapshot", "--help"])
        assert self.snapshot.execute()

        print(
            "\n====================================== datmo snapshot create --help ==========================\n"
        )

        self.snapshot.parse(["snapshot", "create", "--help"])
        assert self.snapshot.execute()

    def test_snapshot_create(self):
        self.__set_variables()
        test_message = "this is a test message"
        test_label = "test label"
        test_session_id = "test_session_id"
        test_task_id = "test_task_id"
        test_code_id = "test_code_id"
        test_environment_definition_filepath = self.env_def_path
        test_config_filepath = self.config_filepath
        test_stats_filepath = self.config_filepath
        test_filepaths = [self.filepath, self.filepath_2]

        # try single filepath
        self.snapshot.parse([
            "snapshot", "create", "--message", test_message, "--task-id",
            test_task_id
        ])

        # testing for proper parsing
        assert self.snapshot.args.message == test_message
        assert self.snapshot.args.task_id == test_task_id

        # try single filepath
        self.snapshot.parse([
            "snapshot",
            "create",
            "--message",
            test_message,
            "--label",
            test_label,
            "--session-id",
            test_session_id,
            "--code-id",
            test_code_id,
            "--environment-def",
            test_environment_definition_filepath,
            "--config-filepath",
            test_config_filepath,
            "--stats-filepath",
            test_stats_filepath,
            "--filepaths",
            test_filepaths[0],
        ])

        # test for desired side effects
        assert self.snapshot.args.message == test_message
        assert self.snapshot.args.label == test_label
        assert self.snapshot.args.session_id == test_session_id
        assert self.snapshot.args.code_id == test_code_id
        assert self.snapshot.args.environment_definition_filepath == test_environment_definition_filepath
        assert self.snapshot.args.config_filepath == test_config_filepath
        assert self.snapshot.args.stats_filepath == test_stats_filepath
        assert self.snapshot.args.filepaths == [test_filepaths[0]]

        # test multiple filepaths
        self.snapshot.parse([
            "snapshot", "create", "--message", test_message, "--label",
            test_label, "--session-id", test_session_id, "--code-id",
            test_code_id, "--environment-def",
            test_environment_definition_filepath, "--config-filepath",
            test_config_filepath, "--stats-filepath", test_stats_filepath,
            "--filepaths", test_filepaths[0], "--filepaths", test_filepaths[1]
        ])

        # test for desired side effects
        assert self.snapshot.args.message == test_message
        assert self.snapshot.args.label == test_label
        assert self.snapshot.args.session_id == test_session_id
        assert self.snapshot.args.code_id == test_code_id
        assert self.snapshot.args.environment_definition_filepath == test_environment_definition_filepath
        assert self.snapshot.args.config_filepath == test_config_filepath
        assert self.snapshot.args.stats_filepath == test_stats_filepath
        assert self.snapshot.args.filepaths == test_filepaths

        snapshot_id_1 = self.snapshot.execute()
        assert snapshot_id_1

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_snapshot_create_from_task(self):
        self.__set_variables()
        test_message = "this is a test message"

        # create task
        test_command = "sh -c 'echo accuracy:0.45'"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        self.task = TaskCommand(self.temp_dir, self.cli_helper)
        self.task.parse([
            "task", "run", "--environment-def", test_dockerfile, test_command
        ])

        # test proper execution of task run command
        task_obj = self.task.execute()

        task_id = task_obj.id

        # test task id
        self.snapshot.parse([
            "snapshot", "create", "--message", test_message, "--task-id",
            task_id
        ])

        # test for desired side effects
        assert self.snapshot.args.message == test_message

        snapshot_id = self.snapshot.execute()
        assert snapshot_id

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_snapshot_create_from_task_fail_user_inputs(self):
        self.__set_variables()
        test_message = "this is a test message"

        # create task
        test_command = "sh -c 'echo accuracy:0.45'"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        self.task = TaskCommand(self.temp_dir, self.cli_helper)
        self.task.parse([
            "task", "run", "--environment-def", test_dockerfile, test_command
        ])

        # test proper execution of task run command
        task_obj = self.task.execute()

        task_id = task_obj.id

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--code-id", "test_code_id"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--commit-id", "test_commit_id"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--environment-id", "test_environment_id"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--environment-def", "test_environment_def"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--file-collection-id", "test_file_collection_id"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--filepaths", "mypath"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--config-filepath", "mypath"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--config-filename", "myname"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--stats-filepath", "mypath"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test task id with code id
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--task-id",
                task_id, "--stats-filename", "myname"
            ])
            _ = self.snapshot.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

    def test_datmo_snapshot_create_fail_mutually_exclusive_args(self):
        self.__set_variables()
        test_message = "this is a test message"
        test_label = "test label"
        test_session_id = "test_session_id"
        test_code_id = "test_code_id"
        test_commit_id = "test_commit_id"
        test_environment_id = "test_environment_id"
        test_environment_definition_filepath = self.env_def_path
        test_file_collection_id = "test_file_collection_id"
        test_filepaths = [self.filepath]
        test_config_filename = "config.json"
        test_config_filepath = self.config_filepath
        test_stats_filename = "stats.json"
        test_stats_filepath = self.config_filepath

        # Code exception
        exception_thrown = False
        try:
            self.snapshot.parse([
                "snapshot", "create", "--message", test_message, "--label",
                test_label, "--session-id", test_session_id, "--code-id",
                test_code_id, "--commit-id", test_commit_id
            ])
            _ = self.snapshot.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # Environment exception
        exception_thrown = False
        try:
            self.snapshot.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--session-id",
                test_session_id,
                "--environment-id",
                test_environment_id,
                "--environment-def",
                test_environment_definition_filepath,
            ])
            _ = self.snapshot.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # File exception
        exception_thrown = False
        try:
            self.snapshot.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--session-id",
                test_session_id,
                "--file-collection-id",
                test_file_collection_id,
                "--filepaths",
                test_filepaths[0],
            ])
            _ = self.snapshot.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # Config exception
        exception_thrown = False
        try:
            self.snapshot.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--session-id",
                test_session_id,
                "--config-filename",
                test_config_filename,
                "--config-filepath",
                test_config_filepath,
            ])
            _ = self.snapshot.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # Stats exception
        exception_thrown = False
        try:
            self.snapshot.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--session-id",
                test_session_id,
                "--stats-filename",
                test_stats_filename,
                "--stats-filepath",
                test_stats_filepath,
            ])
            _ = self.snapshot.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_create_default(self):
        self.__set_variables()
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])

        snapshot_id_2 = self.snapshot.execute()
        assert snapshot_id_2

    def test_datmo_snapshot_create_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.snapshot.parse(["snapshot", "create" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_update(self):
        self.__set_variables()

        test_message = "test_message"
        test_label = "test_label"

        # 1. Updating both message and label
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])
        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot", "update", "--id", snapshot_id, "--message",
            test_message, "--label", test_label
        ])

        result = self.snapshot.execute()
        assert result.id == snapshot_id
        assert result.message == test_message
        assert result.label == test_label

        # 2. Updating only message
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])
        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot", "update", "--id", snapshot_id, "--message",
            test_message
        ])

        result = self.snapshot.execute()
        assert result.id == snapshot_id
        assert result.message == test_message

        # Updating label
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])
        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse(
            ["snapshot", "update", "--id", snapshot_id, "--label", test_label])

        result = self.snapshot.execute()
        assert result.id == snapshot_id
        assert result.label == test_label

    def test_datmo_snapshot_delete(self):
        self.__set_variables()

        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])

        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "delete", "--id", snapshot_id])

        result = self.snapshot.execute()
        assert result

    def test_datmo_snapshot_delete_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.snapshot.parse(["snapshot", "delete" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_ls(self):
        self.__set_variables()
        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])

        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "ls"])

        result = self.snapshot.execute()

        assert result
        assert snapshot_id in result

        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "ls", "-a"])

        result = self.snapshot.execute()

        assert result
        assert snapshot_id in result

    def test_datmo_snapshot_checkout_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.snapshot.parse(["snapshot", "checkout" "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_checkout(self):
        self.__set_variables()
        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "create", "-m", "my test snapshot"])
        snapshot_id = self.snapshot.execute()

        # remove datmo_task folder to have no changes before checkout
        datmo_tasks_dirpath = os.path.join(self.snapshot.home, "datmo_tasks")
        if os.path.exists(datmo_tasks_dirpath):
            shutil.rmtree(datmo_tasks_dirpath)

        # Test when optional parameters are not given
        self.snapshot.parse(["snapshot", "checkout", "--id", snapshot_id])

        result = self.snapshot.execute()
        assert result
