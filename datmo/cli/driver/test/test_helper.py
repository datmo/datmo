"""
Tests for Datmo CLI Helper
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

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
        self.orig_stdin = sys.stdin

    def teardown_method(self):
        sys.stdin = self.orig_stdin

    def test_init(self):
        cli = Helper()
        assert cli != None

    def test_prompt(self):
        cli = Helper()
        test_message = 'foobar'
        with open("test.txt", "w") as f:
            f.write(test_message)

        with open("test.txt", "r") as f:
            sys.stdin = f
            i = cli.prompt("what is this test?")
            assert i == test_message
        os.remove("test.txt")

        # TODO: figure out how to replace "print" with a testable function
        # https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
        # assert cli.prompt(test_message)