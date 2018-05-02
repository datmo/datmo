"""
Tests for Project Commands
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

from datmo.cli.driver.helper import Helper
from datmo.cli.command.project import ProjectCommand


class TestProject():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli = Helper()
        self.init = ProjectCommand(self.temp_dir, self.cli)

    def teardown_class(self):
        pass

    def test_datmo_init(self):
        self.init.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.init.execute()
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))

    def test_datmo_init_invalid_arg(self):
        exception_thrown = False
        try:
            self.init.parse(["init", "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown
