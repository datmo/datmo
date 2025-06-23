"""
Tests for SnapshotCommand
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
import json
import tempfile
import platform
from io import open
from argparse import ArgumentError
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
from datmo.cli.command.snapshot import SnapshotCommand

from datmo.cli.command.run import RunCommand
from datmo.core.util.exceptions import (ProjectNotInitialized,
                                        MutuallyExclusiveArguments,
                                        SnapshotCreateFromTaskArgs)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestSnapshotCommand():
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
        self.snapshot_command = SnapshotCommand(self.cli_helper)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create config file
        self.config_filepath = os.path.join(self.snapshot_command.home,
                                            "config.json")
        with open(self.config_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create stats file
        self.stats_filepath = os.path.join(self.snapshot_command.home,
                                           "stats.json")
        with open(self.stats_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create test file
        self.filepath = os.path.join(self.snapshot_command.home, "file.txt")
        with open(self.filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Create another test file
        self.filepath_2 = os.path.join(self.snapshot_command.home, "file2.txt")
        with open(self.filepath_2, "wb") as f:
            f.write(to_bytes(str("test")))

        # Create config
        self.config = 'foo:bar'
        self.config1 = "{'foo1':'bar1'}"
        self.config2 = "this is test config blob"

        # Create stats
        self.stats = 'foo:bar'
        self.stats1 = "{'foo1':'bar1'}"
        self.stats2 = "this is test stats blob"

    def test_snapshot_help(self):
        self.__set_variables()
        print(
            "\n====================================== datmo snapshot ==========================\n"
        )

        self.snapshot_command.parse(["snapshot"])
        assert self.snapshot_command.execute()

        print(
            "\n====================================== datmo snapshot --help ==========================\n"
        )

        self.snapshot_command.parse(["snapshot", "--help"])
        assert self.snapshot_command.execute()

        print(
            "\n====================================== datmo snapshot create --help ==========================\n"
        )

        self.snapshot_command.parse(["snapshot", "create", "--help"])
        assert self.snapshot_command.execute()

    def test_snapshot_create(self):
        self.__set_variables()
        test_message = "this is a test message"
        test_label = "test label"
        test_run_id = "test_run_id"
        test_environment_definition_filepath = self.env_def_path
        test_config_filepath = self.config_filepath
        test_stats_filepath = self.config_filepath
        test_paths = [self.filepath, self.filepath_2]

        # try single filepath
        self.snapshot_command.parse([
            "snapshot", "create", "--message", test_message, "--run-id",
            test_run_id
        ])

        # testing for proper parsing
        assert self.snapshot_command.args.message == test_message
        assert self.snapshot_command.args.run_id == test_run_id

        # try single filepath
        self.snapshot_command.parse([
            "snapshot",
            "create",
            "--message",
            test_message,
            "--label",
            test_label,
            "--environment-paths",
            test_environment_definition_filepath,
            "--config-filepath",
            test_config_filepath,
            "--stats-filepath",
            test_stats_filepath,
            "--paths",
            test_paths[0],
        ])

        # test for desired side effects
        assert self.snapshot_command.args.message == test_message
        assert self.snapshot_command.args.label == test_label
        assert self.snapshot_command.args.environment_paths == [
            test_environment_definition_filepath
        ]
        assert self.snapshot_command.args.config_filepath == test_config_filepath
        assert self.snapshot_command.args.stats_filepath == test_stats_filepath
        assert self.snapshot_command.args.paths == [test_paths[0]]

        # test multiple paths
        self.snapshot_command.parse([
            "snapshot", "create", "--message", test_message, "--label",
            test_label, "--environment-paths",
            test_environment_definition_filepath, "--config-filepath",
            test_config_filepath, "--stats-filepath", test_stats_filepath,
            "--paths", test_paths[0], "--paths", test_paths[1]
        ])

        # test for desired side effects
        assert self.snapshot_command.args.message == test_message
        assert self.snapshot_command.args.label == test_label
        assert self.snapshot_command.args.environment_paths == [
            test_environment_definition_filepath
        ]
        assert self.snapshot_command.args.config_filepath == test_config_filepath
        assert self.snapshot_command.args.stats_filepath == test_stats_filepath
        assert self.snapshot_command.args.paths == test_paths

        snapshot_obj_1 = self.snapshot_command.execute()
        assert snapshot_obj_1

    def test_snapshot_create_config_stats(self):
        self.__set_variables()
        test_message = "this is a test message"
        test_label = "test label"
        test_config = self.config
        test_stats = self.stats

        # try config
        self.snapshot_command.parse([
            "snapshot", "create", "--message", test_message, "--label",
            test_label, "--config", test_config, "--stats", test_stats
        ])

        # test for desired side effects
        snapshot_obj = self.snapshot_command.execute()
        assert snapshot_obj

        test_config = self.config1
        test_stats = self.stats1

        # try config
        self.snapshot_command.parse([
            "snapshot", "create", "--message", test_message, "--label",
            test_label, "--config", test_config, "--stats", test_stats
        ])

        # test for desired side effects
        snapshot_obj = self.snapshot_command.execute()
        assert snapshot_obj

        test_config = self.config2
        test_stats = self.stats2

        # try config
        self.snapshot_command.parse([
            "snapshot", "create", "--message", test_message, "--label",
            test_label, "--config", test_config, "--stats", test_stats
        ])

        # test for desired side effects
        snapshot_obj = self.snapshot_command.execute()
        assert snapshot_obj

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_snapshot_create_from_run(self):
        self.__set_variables()
        test_message = "this is a test message"

        # create task
        test_command = "sh -c 'echo accuracy:0.45'"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        self.run = RunCommand(self.cli_helper)
        self.run.parse(
            ["run", "--environment-paths", test_dockerfile, test_command])

        # test proper execution of task run command
        run_obj = self.run.execute()

        run_id = run_obj.id

        # test run id
        self.snapshot_command.parse([
            "snapshot", "create", "--message", test_message, "--run-id", run_id
        ])

        # test for desired side effects
        assert self.snapshot_command.args.message == test_message

        snapshot_obj = self.snapshot_command.execute()
        assert snapshot_obj

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_snapshot_create_from_run_fail_user_inputs(self):
        self.__set_variables()
        test_message = "this is a test message"

        # create run
        test_command = "sh -c 'echo accuracy:0.45'"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        self.run = RunCommand(self.cli_helper)
        self.run.parse(
            ["run", "--environment-paths", test_dockerfile, test_command])

        # test proper execution of task run command
        run_obj = self.run.execute()

        run_id = run_obj.id

        failed = False
        try:
            # test run id with environment-id
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--environment-id", "test_environment_id"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test run id with environment-def
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--environment-paths", "test_environment_path"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test run id with filepaths
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--paths", "mypath"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test run id with config-filepath
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--config-filepath", "mypath"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test run id with config-filename
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--config-filename", "myname"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test run id with stats-filepath
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--stats-filepath", "mypath"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            # test run id with stats-filename
            self.snapshot_command.parse([
                "snapshot", "create", "--message", test_message, "--run-id",
                run_id, "--stats-filename", "myname"
            ])
            _ = self.snapshot_command.execute()
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

    def test_snapshot_create_fail_mutually_exclusive_args(self):
        self.__set_variables()
        test_message = "this is a test message"
        test_label = "test label"
        test_environment_id = "test_environment_id"
        test_environment_definition_filepath = self.env_def_path
        test_config_filename = "config.json"
        test_config_filepath = self.config_filepath
        test_stats_filename = "stats.json"
        test_stats_filepath = self.config_filepath

        # Environment exception
        exception_thrown = False
        try:
            self.snapshot_command.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--environment-id",
                test_environment_id,
                "--environment-paths",
                test_environment_definition_filepath,
            ])
            _ = self.snapshot_command.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # Config exception
        exception_thrown = False
        try:
            self.snapshot_command.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--config-filename",
                test_config_filename,
                "--config-filepath",
                test_config_filepath,
            ])
            _ = self.snapshot_command.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # Stats exception
        exception_thrown = False
        try:
            self.snapshot_command.parse([
                "snapshot",
                "create",
                "--message",
                test_message,
                "--label",
                test_label,
                "--stats-filename",
                test_stats_filename,
                "--stats-filepath",
                test_stats_filepath,
            ])
            _ = self.snapshot_command.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

    def test_snapshot_create_default(self):
        self.__set_variables()
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])

        snapshot_obj_2 = self.snapshot_command.execute()
        assert snapshot_obj_2

    def test_snapshot_create_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.snapshot_command.parse(
                ["snapshot", "create"
                 "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_snapshot_update(self):
        self.__set_variables()

        test_config = ["depth: 10", "learning_rate:0.91"]
        test_stats = ["acc: 91.34", "f1_score:0.91"]
        test_config1 = "{'foo_config': 'bar_config'}"
        test_stats1 = "{'foo_stats': 'bar_stats'}"
        test_config2 = "this is a config blob"
        test_stats2 = "this is a stats blob"
        test_message = "test_message"
        test_label = "test_label"

        # 1. Updating both message and label
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse([
            "snapshot", "update", snapshot_obj.id, "--message", test_message,
            "--label", test_label
        ])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.message == test_message
        assert result.label == test_label

        # 2. Updating only message
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse(
            ["snapshot", "update", snapshot_obj.id, "--message", test_message])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.message == test_message

        # Updating label
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse(
            ["snapshot", "update", snapshot_obj.id, "--label", test_label])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.label == test_label

        # 3. Updating config, message and label
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse([
            "snapshot", "update", snapshot_obj.id, "--config", test_config[0],
            "--config", test_config[1], "--message", test_message, "--label",
            test_label
        ])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.config == {"depth": "10", "learning_rate": "0.91"}
        assert result.message == test_message
        assert result.label == test_label

        # 4. Updating stats, message and label
        # Test when optional parameters are not given
        self.snapshot_command.parse([
            "snapshot", "update", snapshot_obj.id, "--stats", test_stats[0],
            "--stats", test_stats[1], "--message", test_message, "--label",
            test_label
        ])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.stats == {"acc": "91.34", "f1_score": "0.91"}
        assert result.message == test_message
        assert result.label == test_label

        # Adding sleep due to issue with consistency in blitzdb database
        time.sleep(2)

        # 5. Updating config, stats
        # Test when optional parameters are not given
        self.snapshot_command.parse([
            "snapshot", "update", snapshot_obj.id, "--config", test_config1,
            "--stats", test_stats1
        ])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.config == {
            "depth": "10",
            "learning_rate": "0.91",
            'foo_config': 'bar_config'
        }
        assert result.stats == {
            "acc": "91.34",
            "f1_score": "0.91",
            'foo_stats': 'bar_stats'
        }
        assert result.message == test_message
        assert result.label == test_label

        # Test when optional parameters are not given
        self.snapshot_command.parse([
            "snapshot", "update", snapshot_obj.id, "--config", test_config2,
            "--stats", test_stats2
        ])

        result = self.snapshot_command.execute()
        assert result.id == snapshot_obj.id
        assert result.config == {
            "depth": "10",
            "learning_rate": "0.91",
            'foo_config': 'bar_config',
            'config': test_config2
        }
        assert result.stats == {
            "acc": "91.34",
            "f1_score": "0.91",
            'foo_stats': 'bar_stats',
            'stats': test_stats2
        }
        assert result.message == test_message
        assert result.label == test_label

    def test_snapshot_delete(self):
        self.__set_variables()

        # Test when optional parameters are not given
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])

        snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse(["snapshot", "delete", snapshot_obj.id])

        result = self.snapshot_command.execute()
        assert result

    def test_snapshot_delete_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.snapshot_command.parse(
                ["snapshot", "delete"
                 "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_snapshot_ls_invisible(self):
        self.__set_variables()

        # Test invisible snapshot from task
        # create task
        test_command = "sh -c 'echo accuracy:0.45'"
        test_dockerfile = os.path.join(self.temp_dir, "Dockerfile")
        self.run = RunCommand(self.cli_helper)
        self.run.parse(
            ["run", "--environment-paths", test_dockerfile, test_command])

        # test proper execution of task run command
        task_obj = self.run.execute()

        # test no visible snapshots
        self.snapshot_command.parse(["snapshot", "ls"])

        result = self.snapshot_command.execute()

        assert not result

        # test invisible snapshot from task_id was created
        self.snapshot_command.parse(["snapshot", "ls", "--all"])

        result = self.snapshot_command.execute()

        assert result
        assert task_obj.after_snapshot_id in [obj.id for obj in result]

    def test_snapshot_ls(self):
        self.__set_variables()

        # create a visible snapshot
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])

        created_snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse(["snapshot", "ls"])

        result = self.snapshot_command.execute()

        assert result
        assert created_snapshot_obj in result
        # Check if current snapshot id is the same as the latest created id
        current_snapshot_obj = self.snapshot_command.snapshot_controller.current_snapshot(
        )
        current_snapshot_id = current_snapshot_obj.id if current_snapshot_obj else None
        assert current_snapshot_id == created_snapshot_obj.id

        # Test when optional parameters are not given
        self.snapshot_command.parse(["snapshot", "ls", "--details"])

        result = self.snapshot_command.execute()

        assert result
        assert created_snapshot_obj in result

        # Test failure (format)
        failed = False
        try:
            self.snapshot_command.parse(["snapshot", "ls", "--format"])
        except ArgumentError:
            failed = True
        assert failed

        # Test success format csv
        self.snapshot_command.parse(["snapshot", "ls", "--format", "csv"])
        snapshot_objs = self.snapshot_command.execute()
        assert created_snapshot_obj in snapshot_objs

        # Test success format csv, download default
        self.snapshot_command.parse(
            ["snapshot", "ls", "--format", "csv", "--download"])
        snapshot_objs = self.snapshot_command.execute()
        assert created_snapshot_obj in snapshot_objs
        test_wildcard = os.path.join(
            self.snapshot_command.snapshot_controller.home, "snapshot_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format csv, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.snapshot_command.parse([
            "snapshot", "ls", "--format", "csv", "--download",
            "--download-path", test_path
        ])
        snapshot_objs = self.snapshot_command.execute()
        assert created_snapshot_obj in snapshot_objs
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

        # Test success format table
        self.snapshot_command.parse(["snapshot", "ls"])
        environment_objs = self.snapshot_command.execute()
        assert created_snapshot_obj in snapshot_objs

        # Test success format table, download default
        self.snapshot_command.parse(["snapshot", "ls", "--download"])
        snapshot_objs = self.snapshot_command.execute()
        assert created_snapshot_obj in snapshot_objs
        test_wildcard = os.path.join(
            self.snapshot_command.snapshot_controller.home, "snapshot_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format table, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.snapshot_command.parse(
            ["snapshot", "ls", "--download", "--download-path", test_path])
        snapshot_objs = self.snapshot_command.execute()
        assert created_snapshot_obj in snapshot_objs
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

    def test_snapshot_checkout_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
            self.snapshot_command.parse(
                ["snapshot", "checkout"
                 "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_snapshot_checkout(self):
        self.__set_variables()
        # Test when optional parameters are not given
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj = self.snapshot_command.execute()

        # Test when optional parameters are not given
        self.snapshot_command.parse(["snapshot", "checkout", snapshot_obj.id])

        result = self.snapshot_command.execute()
        assert result

    def test_snapshot_diff(self):
        self.__set_variables()

        # Create config file
        with open(self.config_filepath, "wb") as f:
            f.write(to_bytes(str('{"depth":6}')))

        # Create stats file
        with open(self.stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"acc":0.97}')))

        # Create snapshots to test
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj_1 = self.snapshot_command.execute()

        # Create another test file
        self.filepath_3 = os.path.join(self.snapshot_command.home, "file3.txt")
        with open(self.filepath_3, "wb") as f:
            f.write(to_bytes(str("test")))

        # Create config file
        with open(self.config_filepath, "wb") as f:
            f.write(to_bytes(str('{"depth":5}')))

        # Create stats file
        with open(self.stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"acc":0.91}')))

        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my second snapshot"])
        snapshot_obj_2 = self.snapshot_command.execute()

        # Test diff with the above two snapshots
        self.snapshot_command.parse(
            ["snapshot", "diff", snapshot_obj_1.id, snapshot_obj_2.id])

        result = self.snapshot_command.execute()
        assert result
        assert "message" in result
        assert "label" in result
        assert "code_id" in result
        assert "environment_id" in result
        assert "file_collection_id" in result
        assert "config" in result
        assert "stats" in result

    def test_snapshot_inspect(self):
        self.__set_variables()
        # Create snapshot to test
        self.snapshot_command.parse(
            ["snapshot", "create", "-m", "my test snapshot"])
        snapshot_obj = self.snapshot_command.execute()
        # Test inspect for this snapshot
        self.snapshot_command.parse(["snapshot", "inspect", snapshot_obj.id])

        result = self.snapshot_command.execute()
        assert result
        assert "Code" in result
        assert "Environment" in result
        assert "Files" in result
        assert "Config" in result
        assert "Stats" in result
