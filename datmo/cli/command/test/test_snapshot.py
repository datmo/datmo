"""
Tests for Snapshot
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
from datmo.cli.driver.cli_helper import CLIHelper
from datmo.cli.command.init import Init
from datmo.cli.command.snapshot import Snapshot

class TestSnapshot():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cli = CLIHelper()
        self.init = Init(self.cli)
        self.snapshot = Snapshot(self.cli)

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_datmo_snapshot_create(self):
        self.init.parse([
          "init",
          "--name","foobar",
          "--path",self.temp_dir,
          "--description","test model"])
        self.init.execute()

        test_message = "this is a test message"
        test_label = "test label"
        test_session_id = "test_session_id"
        test_task_id = "test_task_id"
        test_code_id = "test_code_id"
        test_environment_def_path = "/path/to/Dockerfile"
        test_config_filename = "config.json"
        test_config_filepath = "/path/to/config.json"
        test_stats_filename = "stats.json"
        test_stats_filepath = "/path/to/stats.json"
        test_filepaths = ["file.txt", "files/"]

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
            "--filepaths", test_filepaths
        ])

        # test for desired side effects
        assert self.snapshot.args.message == test_message
        assert self.snapshot.args.label == test_label
        assert self.snapshot.args.session_id == test_session_id
        assert self.snapshot.args.task_id == test_task_id
        assert self.snapshot.args.code_id == test_code_id
        assert self.snapshot.args.environment_def_path == test_environment_def_path
        assert self.snapshot.args.config_filename == test_config_filename
        assert self.snapshot.args.config_filepath == test_config_filepath
        assert self.snapshot.args.stats_filename == test_stats_filename
        assert self.snapshot.args.stats_filepath == test_stats_filepath
        assert self.snapshot.args.filepaths == test_filepaths


    def test_datmo_snapshot_create_invalid_arg(self):
        datmo_init = Init(self.cli)
        exception_thrown = False
        try:
          datmo_init.parse([
            "init",
            "--foobar","foobar"])
        except Exception as ex:
            exception_thrown = True
        assert exception_thrown