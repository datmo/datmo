"""
Tests for SessionCommand
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tempfile
import platform
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import os
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
        self.project = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project.execute()
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
        assert self.session_command.execute()

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
        self.test_session_create()

        self.session_command.parse(["session", "ls"])
        assert self.session_command.execute()

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
