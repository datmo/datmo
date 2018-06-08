"""
Tests for SessionCommand
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import glob
import tempfile
import platform
from argparse import ArgumentError
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.cli.driver.helper import Helper
from datmo.cli.command.session import SessionCommand
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.exceptions import ProjectNotInitialized


class TestSession():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        self.project_command = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project_command.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project_command.execute()
        self.session_command = SessionCommand(self.temp_dir, self.cli_helper)

    def test_session_project_not_init(self):
        failed = False
        try:
            self.snapshot = SessionCommand(self.temp_dir, self.cli_helper)
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_session_no_subcommand(self):
        self.__set_variables()
        self.session_command.parse(["session"])
        assert self.session_command.execute()

    def test_session_create(self):
        self.__set_variables()
        self.session_command.parse(["session", "create", "--name", "pizza"])
        result = self.session_command.execute()
        assert result
        return result

    def test_session_select(self):
        self.test_session_create()

        self.session_command.parse(["session", "select", "--name", "pizza"])
        assert self.session_command.execute()
        current = 0
        for s in self.session_command.session_controller.list():
            print("%s - %s" % (s.name, s.current))
            if s.current == True:
                current = current + 1
        assert current == 1

    def test_session_ls(self):
        created_session_obj = self.test_session_create()

        # Test success (defaults)
        self.session_command.parse(["session", "ls"])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs

        # Test failure (format)
        failed = False
        try:
            self.session_command.parse(["session", "ls", "--format"])
        except ArgumentError:
            failed = True
        assert failed

        # Test success format csv
        self.session_command.parse(["session", "ls", "--format", "csv"])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs

        # Test success format csv, download default
        self.session_command.parse(
            ["session", "ls", "--format", "csv", "--download"])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs
        test_wildcard = os.path.join(os.getcwd(), "session_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format csv, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.session_command.parse([
            "session", "ls", "--format", "csv", "--download",
            "--download-path", test_path
        ])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

        # Test success format table
        self.session_command.parse(["session", "ls"])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs

        # Test success format table, download default
        self.session_command.parse(["session", "ls", "--download"])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs
        test_wildcard = os.path.join(os.getcwd(), "session_ls_*")
        paths = [n for n in glob.glob(test_wildcard) if os.path.isfile(n)]
        assert paths
        assert open(paths[0], "r").read()
        os.remove(paths[0])

        # Test success format table, download exact path
        test_path = os.path.join(self.temp_dir, "my_output")
        self.session_command.parse(
            ["session", "ls", "--download", "--download-path", test_path])
        session_objs = self.session_command.execute()
        assert created_session_obj in session_objs
        assert os.path.isfile(test_path)
        assert open(test_path, "r").read()
        os.remove(test_path)

    def test_session_delete(self):
        self.test_session_create()

        self.session_command.parse(["session", "delete", "--name", "pizza"])
        assert self.session_command.execute()
        session_removed = True
        for s in self.session_command.session_controller.list():
            if s.name == 'pizza':
                session_removed = False
        assert session_removed
        self.session_command.parse(["session", "ls"])
        assert self.session_command.execute()
