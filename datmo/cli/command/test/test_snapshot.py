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
from datmo.core.util.exceptions import ProjectNotInitializedException, MutuallyExclusiveArguments


class TestSnapshot():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        self.init = ProjectCommand(self.temp_dir, self.cli_helper)
        self.init.parse([
            "init",
            "--name", "foobar",
            "--description", "test model"])
        self.init.execute()
        self.snapshot = SnapshotCommand(self.temp_dir, self.cli_helper)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir,
                                         "Dockerfile")
        with open(self.env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        self.config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(self.config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        self.stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(self.stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create test file
        self.filepath = os.path.join(self.snapshot.home,
                                           "file.txt")
        with open(self.filepath, "w") as f:
            f.write(to_unicode(str("test")))

    def test_snapshot_project_not_init(self):
        failed = False
        try:
            self.snapshot = SnapshotCommand(self.temp_dir, self.cli_helper)
        except ProjectNotInitializedException:
            failed = True
        assert failed

    def test_datmo_snapshot_create(self):
        self.__set_variables()
        test_message = "this is a test message"
        test_label = "test label"
        test_session_id = "test_session_id"
        test_task_id = "test_task_id"
        test_code_id = "test_code_id"
        test_environment_def_path = self.env_def_path
        test_config_filename = "config.json"
        test_config_filepath = self.config_filepath
        test_stats_filename = "stats.json"
        test_stats_filepath = self.config_filepath
        test_filepaths = [self.filepath]
        test_visible = False

        self.snapshot.parse([
            "snapshot",
            "create",
            "--message", test_message,
            "--label", test_label,
            "--session-id", test_session_id,
            "--task-id", test_task_id,
            "--code-id", test_code_id,
            "--environment-def-path", test_environment_def_path,
            "--config-filepath", test_config_filepath,
            "--stats-filepath", test_stats_filepath,
            "--filepaths", test_filepaths[0],
            "--not-visible"
        ])

        # test for desired side effects
        assert self.snapshot.args.message == test_message
        assert self.snapshot.args.label == test_label
        assert self.snapshot.args.session_id == test_session_id
        assert self.snapshot.args.task_id == test_task_id
        assert self.snapshot.args.code_id == test_code_id
        assert self.snapshot.args.environment_def_path == test_environment_def_path
        assert self.snapshot.args.config_filepath == test_config_filepath
        assert self.snapshot.args.stats_filepath == test_stats_filepath
        assert self.snapshot.args.filepaths == test_filepaths
        assert self.snapshot.args.visible == test_visible

        snapshot_id_1 = self.snapshot.execute()
        assert snapshot_id_1

        exception_thrown = False
        try:
            self.snapshot.parse([
                "snapshot",
                "create",
                "--message", test_message,
                "--label", test_label,
                "--session-id", test_session_id,
                "--task-id", test_task_id,
                "--code-id", test_code_id,
                "--environment-def-path", test_environment_def_path,
                "--config-filename", test_config_filename,
                "--config-filepath", test_config_filepath,
                "--stats-filename", test_stats_filename,
                "--stats-filepath", test_stats_filepath,
                "--filepaths", test_filepaths[0],
                "--not-visible"
            ])

            _ = self.snapshot.execute()
        except MutuallyExclusiveArguments:
            exception_thrown = True
        assert exception_thrown

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "create",
            "-m", "my test snapshot"
        ])

        snapshot_id_2 = self.snapshot.execute()
        assert snapshot_id_2

    def test_datmo_snapshot_create_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
          self.snapshot.parse([
            "snapshot",
            "create"
            "--foobar","foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_delete(self):
        self.__set_variables()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "create",
            "-m", "my test snapshot"
        ])

        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "delete",
            "--id", snapshot_id
        ])

        result = self.snapshot.execute()
        assert result

    def test_datmo_snapshot_delete_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
          self.snapshot.parse([
            "snapshot",
            "delete"
            "--foobar","foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_ls(self):
        self.__set_variables()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "create",
            "-m", "my test snapshot"
        ])

        self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "ls"
        ])

        result = self.snapshot.execute()

        assert result

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "ls", "-a"
        ])

        result = self.snapshot.execute()

        assert result

    def test_datmo_snapshot_checkout_invalid_arg(self):
        self.__set_variables()
        exception_thrown = False
        try:
          self.snapshot.parse([
            "snapshot",
            "checkout"
            "--foobar","foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_snapshot_checkout(self):
        self.__set_variables()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "create",
            "-m", "my test snapshot"
        ])

        snapshot_id = self.snapshot.execute()

        # Test when optional parameters are not given
        self.snapshot.parse([
            "snapshot",
            "checkout",
            "--id", snapshot_id
        ])

        result = self.snapshot.execute()
        assert result