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
import tempfile
import platform

from datmo import __version__
from datmo.cli.driver.helper import Helper
from datmo.cli.parser import parser
from datmo.cli.command.project import ProjectCommand


class TestProject():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()
        self.project = ProjectCommand(self.temp_dir, self.cli_helper, parser)

    def teardown_class(self):
        pass

    def test_datmo_init(self):
        self.project.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project.execute()
        # test for desired side effects
        assert os.path.exists(os.path.join(self.temp_dir, '.datmo'))

    def test_datmo_init_invalid_arg(self):
        exception_thrown = False
        try:
            self.project.parse(["init", "--foobar", "foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown

    def test_datmo_version(self):
        self.project.parse(["version"])
        result = self.project.execute()
        # test for desired side effects
        assert __version__ in result

    def test_datmo_version_invalid_arg(self):
        exception_thrown = False
        try:
            self.project.parse(["version", "--foobar"])
        except Exception:
            exception_thrown = True
        assert exception_thrown
