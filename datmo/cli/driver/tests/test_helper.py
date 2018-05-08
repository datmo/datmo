"""
Tests for Datmo CLI Helper
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# TODO: include builtin libraries for the appropriate Python
# try:
#     import __builtin__
# except ImportError:
#     # Python 3
#     import builtins as __builtin__

from datmo.cli.driver.helper import Helper


class TestHelper():
    # https://stackoverflow.com/questions/35851323/pytest-how-to-test-a-function-with-input-call/36377194

    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.orig_stdin = sys.stdin

    def teardown_method(self):
        sys.stdin = self.orig_stdin

    def test_init(self):
        cli = Helper()
        assert cli != None

    def test_input(self):
        cli = Helper()
        test_msg = "test"
        @cli.input(test_msg)
        def dummy():
            return input("test")
        result = dummy()
        assert test_msg in result

    def test_prompt(self):
        cli = Helper()
        test_message = 'foobar'
        @cli.input(test_message)
        def dummy():
            return cli.prompt("what is this test?")
        i = dummy()
        assert i == test_message

        # TODO: figure out how to replace "print" with a testable function
        # https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
        # assert cli.prompt(test_message)