"""
Tests for Datmo CLI Helper
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import input

import os
import sys
import tempfile
import platform
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
from datmo.core.util.exceptions import ArgumentError
from datmo.cli.command.project import ProjectCommand
from datmo.cli.command.snapshot import SnapshotCommand
from datmo.cli.command.task import TaskCommand
from datmo.cli.command.session import SessionCommand
from datmo.cli.command.environment import EnvironmentCommand


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
        self.cli = Helper()

    def teardown_method(self):
        sys.stdin = self.orig_stdin

    def test_init(self):
        assert self.cli != None

    def test_input(self):
        test_input = "test"

        @self.cli.input(test_input)
        def dummy():
            return input("test prompt")

        result = dummy()
        assert test_input in result

    def test_prompt(self):
        test_input = 'foobar'

        @self.cli.input(test_input)
        def dummy():
            return self.cli.prompt("what is this test?")

        i = dummy()
        assert i == test_input

        # TODO: figure out how to replace "print" with a testable function
        # https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
        # assert cli.prompt(test_message)

    def test_print_items(self):
        # Test without download in print_format="table"
        header_list = ["foo", "bar"]
        item_dict_list = [{
            "foo": "yo",
            "bar": "hello"
        }, {
            "foo": "cool",
            "bat": "there"
        }]
        result = self.cli.print_items(
            header_list=header_list, item_dict_list=item_dict_list)
        assert "foo" in result
        assert "bar" in result
        assert "yo" in result
        assert "hello" in result
        assert "cool" in result
        assert "there" not in result
        assert "N/A" in result
        # Test without download in print_format="csv"
        result = self.cli.print_items(
            header_list=header_list,
            item_dict_list=item_dict_list,
            print_format="csv")
        assert result == "foo,bar\nyo,hello\ncool,N/A\n"
        assert "there" not in result
        # Test without download in random print_format
        result = self.cli.print_items(
            header_list=header_list,
            item_dict_list=item_dict_list,
            print_format="not_valid")
        assert not result
        # Test with output_path given (not absolute)
        test_path = "testprint"
        test_full_path = os.path.join(os.getcwd(), test_path)
        result = self.cli.print_items(
            header_list=header_list,
            item_dict_list=item_dict_list,
            output_path=test_path)
        assert result
        assert os.path.isfile(test_full_path)
        assert result in open(test_full_path, "r").read()
        os.remove(test_full_path)
        # Test with output_path given (absolute)
        test_full_path = os.path.join(self.temp_dir, "testprint")
        result = self.cli.print_items(
            header_list=header_list,
            item_dict_list=item_dict_list,
            output_path=test_full_path)
        assert result
        assert os.path.isfile(test_full_path)
        assert result in open(test_full_path, "r").read()

    def test_prompt_bool(self):
        # Test if true for truthy inputs
        test_message_list = [
            'true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'
        ]
        for test_message in test_message_list:

            @self.cli.input(test_message)
            def dummy():
                return self.cli.prompt_bool("are you sure about this test?")

            i = dummy()
            assert i == True

        # Test if false for non-truthy inputs
        test_message = 'n'

        @self.cli.input(test_message)
        def dummy():
            return self.cli.prompt_bool("are you sure about this test?")

        i = dummy()
        assert i == False

    def test_prompt_validator(self):
        def validate_y(val):
            return True if val == "y" else False

        # Test success
        test_input = "y"

        @self.cli.input(test_input)
        def dummy():
            return self.cli.prompt_validator("is this a y?", validate_y)

        i = dummy()
        assert i == test_input
        # Test success invalid (2 tries) - TODO: fix
        # test_input = "n"
        # @self.cli.input(test_input + "\n")
        # @self.cli.input(test_input + "\n")
        # def dummy():
        #     return self.cli.prompt_validator("is this a y?", validate_y, tries=2)
        # i = dummy()
        # assert i == test_input
        # Test failure (not valid function)
        validate_func = 2
        failed = False
        try:
            self.cli.prompt_validator("y", validate_func)
        except ArgumentError:
            failed = True
        assert failed

    def test_get_command_class(self):
        # Test success
        for command in [
                "project", "snapshot", "task", "session", "environment"
        ]:
            result = self.cli.get_command_class(command)
            if command == "project":
                assert result == ProjectCommand
            elif command == "snapshot":
                assert result == SnapshotCommand
            elif command == "task":
                assert result == TaskCommand
            elif command == "session":
                assert result == SessionCommand
            elif command == "environment":
                assert result == EnvironmentCommand
            else:
                assert False

    def test_get_command_choices(self):
        # assert same as output
        assert self.cli.get_command_choices() == [
            "init", "version", "--version", "-v", "status", "cleanup",
            "snapshot", "task", "notebook", "environment", "run"
        ]
