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

import shutil
import tempfile

from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.task import TaskCommand

class TestSnapshot():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cli_helper = Helper()
        self.init = ProjectCommand(self.temp_dir, self.cli_helper)
        self.init.parse([
            "init",
            "--name", "foobar",
            "--description", "test model"])
        self.init.execute()
        self.task = TaskCommand(self.temp_dir, self.cli_helper)

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_datmo_task_run(self):

        test_command = "python test.py"
        test_gpu = True
        test_ports = "8888:8888"
        test_data = "data"
        test_dockerfile = "Dockerfile"
        test_interactive = True

        self.task.parse([
            "task",
            "run",
            "--command", test_command,
            "--gpu", test_gpu,
            "--ports", test_ports,
            "--data", test_data,
            "--dockerfile", test_dockerfile,
            "--interactive", test_interactive
        ])

        # test for desired side effects
        assert self.task.args.command == test_command
        assert self.task.args.gpu == test_gpu
        assert self.task.args.ports == test_ports
        assert self.task.args.data == test_data
        assert self.task.args.dockerfile == test_dockerfile
        assert self.task.args.interactive == test_interactive

    def test_datmo_task_run_invalid_arg(self):
        exception_thrown = False
        try:
          self.task.parse([
            "task",
            "run"
            "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_task_ls(self):

        test_running = True
        test_all = True

        self.task.parse([
            "task",
            "ls",
            "--running", test_running,
            "--all", test_all
        ])

        # test for desired side effects
        assert self.task.args.running == test_running
        assert self.task.args.all == test_all

    def test_datmo_task_ls_invalid_arg(self):
        exception_thrown = False
        try:
          self.task.parse([
            "task",
            "ls"
            "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_task_stop(self):

        test_running = True
        test_id = 'test_id'

        self.task.parse([
            "task",
            "stop",
            "--running", test_running,
            "--id", test_id
        ])

        # test for desired side effects
        assert self.task.args.running == test_running
        assert self.task.args.id == test_id

    def test_datmo_task_stop_invalid_arg(self):
        exception_thrown = False
        try:
          self.task.parse([
            "task",
            "stop"
            "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown