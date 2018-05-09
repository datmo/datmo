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
from datmo.cli.command.datmo_command import DatmoCommand


class TestDatmo():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli = Helper()

    def teardown_class(self):
        pass

    def test_datmo_base(self):
        base = DatmoCommand(self.temp_dir, self.cli)
        base.parse([])
        assert base.execute()

    def test_datmo_help(self):
        base = DatmoCommand(self.temp_dir, self.cli)
        base.parse(["--help"])
        assert base.execute()
