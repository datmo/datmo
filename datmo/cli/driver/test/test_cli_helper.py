"""
Tests for Datmo Cli Helper
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


from datmo.cli.driver.cli_helper import CLIHelper

class TestCLIHelper():
    def test_init(self):
        cli = CLIHelper()
        assert cli != None

    def test_prompt(self):
        cli = CLIHelper()
        test_message = 'foobar'
        # TODO: figure out how to replace "print" with a testable function
        # https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
        # assert cli.echo(test_message) == test_message