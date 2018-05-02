"""
Tests for SessopmCommand
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import tempfile
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import os
from datmo.cli.driver.helper import Helper
from datmo.cli.command.session import SessionCommand
from datmo.cli.command.project import ProjectCommand


class TestSession():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()
        self.session_command = SessionCommand(self.temp_dir, self.cli_helper)

        init = ProjectCommand(self.temp_dir, self.cli_helper)
        init.parse(["init", "--name", "foobar", "--description", "test model"])
        init.execute()

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_session_create(self):
        self.session_command.parse(["session", "create", "--name", "pizza"])
        assert self.session_command.execute()

    def test_session_select(self):
        self.session_command.parse(["session", "select", "--name", "pizza"])
        assert self.session_command.execute()
        current = 0
        for s in self.session_command.session_controller.list():
            print("%s - %s" % (s.name, s.current))
            if s.current == True:
                current = current + 1
        assert current == 1

    def test_session_ls(self):
        self.session_command.parse(["session", "ls"])
        assert self.session_command.execute()

    def test_session_delete(self):
        self.session_command.parse(["session", "delete", "--name", "pizza"])
        assert self.session_command.execute()
        session_removed = True
        for s in self.session_command.session_controller.list():
            if s.name == 'pizza':
                session_removed = False
        assert session_removed
        self.session_command.parse(["session", "ls"])
        assert self.session_command.execute()
