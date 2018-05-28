#!/usr/bin/python
"""
Tests for misc_functions.py
"""
import os
import tempfile
import platform
import datetime
from pytz import timezone
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.util.misc_functions import (
    get_filehash, create_unique_hash, mutually_exclusive, is_project_dir,
    find_project_dir, grep, prettify_datetime, format_table, parse_cli_key_value, get_datmo_temp_path)

from datmo.core.util.exceptions import MutuallyExclusiveArguments, RequiredArgumentMissing


class TestMiscFunctions():
    # TODO: Add more cases for each test
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if platform.system() != "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def test_get_filehash(self):
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, "w") as f:
            f.write(to_unicode("hello\n"))
        result = get_filehash(filepath)
        assert len(result) == 32

    def test_create_unique_hash(self):
        result_hash_1 = create_unique_hash()
        result_hash_2 = create_unique_hash()

        assert result_hash_1 != result_hash_2

    def test_mutually_exclusive(self):
        mutually_exclusive_args = ["code_id", "commit_id"]
        arguments_dictionary = {
            "code_id": "test_code_id",
            "environment_id": "test_environment_id"
        }
        dictionary = {}
        mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                           dictionary)
        assert dictionary
        assert dictionary['code_id'] == arguments_dictionary['code_id']

        failed = False
        try:
            mutually_exclusive_args = ["code_id", "commit_id"]
            arguments_dictionary = {"code_id": None, "environment_id": None}
            dictionary = {}
            mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                               dictionary)
        except RequiredArgumentMissing:
            failed = True
        assert failed

        failed = False
        try:
            mutually_exclusive_args = ["code_id", "commit_id"]
            arguments_dictionary = {"code_id": None, "commit_id": None}
            dictionary = {}
            mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                               dictionary)
        except RequiredArgumentMissing:
            failed = True
        assert failed

        update_dictionary_failed = False
        try:
            mutually_exclusive_args = ["code_id", "commit_id"]
            arguments_dictionary = {
                'code_id': "test_code_id",
                'commit_id': "test_environment_id"
            }
            dictionary = {}
            mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                               dictionary)
        except MutuallyExclusiveArguments:
            update_dictionary_failed = True
        assert update_dictionary_failed

    def test_find_project_dir(self):
        exec_path = os.path.join(self.temp_dir, "1", "1", "1")
        os.makedirs(exec_path)
        os.makedirs(os.path.join(self.temp_dir, ".datmo"))
        project_path = find_project_dir(exec_path)
        assert project_path == self.temp_dir

    def test_is_project_dir(self):
        os.makedirs(os.path.join(self.temp_dir, ".datmo"))
        assert is_project_dir(self.temp_dir)

    def test_grep(self):
        # open current file and try to find this method in it
        assert len(grep("test_grep", open(__file__, "r"))) == 2

    def test_parse_cli_key_value(self):
        # passing in parsable json blob
        cli_string = "{'foo1':'bar1', 'foo2':'bar2'}"
        default_key = 'config'

        dictionary = parse_cli_key_value(cli_string, default_key)

        assert dictionary == {'foo1': 'bar1', 'foo2': 'bar2'}

        # passing in unparsable json blob
        cli_string = "this is a test blob"
        default_key = 'config'

        dictionary = parse_cli_key_value(cli_string, default_key)

        assert dictionary == {'config': 'this is a test blob'}

        # passing in key, value in dictionary
        cli_string = 'foo:bar'
        default_key = 'config'

        dictionary = parse_cli_key_value(cli_string, default_key)

        assert dictionary == {'foo': 'bar'}

    def test_prettify_datetime(self):
        my_test_datetime = datetime.datetime(2018, 1, 1)
        result = prettify_datetime(my_test_datetime)
        # Ensure there is a result in the local timezone
        assert result
        tz = timezone('US/Eastern')
        result = prettify_datetime(my_test_datetime, tz=tz)
        assert result == "Sun Dec 31 19:00:00 2017 -0500"

    def test_format_table(self):
        test_data = [["row1", "row1"], ["row2", "row2"]]
        result = format_table(test_data, padding=2)
        assert result == "row1  row1  \nrow2  row2  \n"

    def test_get_datmo_temp_path(self):
        datmo_temp_path = get_datmo_temp_path(self.temp_dir)
        exists = False
        if os.path.isdir(datmo_temp_path):
            exists = True

        assert exists
