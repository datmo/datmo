#!/usr/bin/python
"""
Tests for misc_functions.py
"""
import os
import time
import tempfile
import platform
import datetime
from pytz import timezone
from io import open
try:
    to_unicode = str
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.util.misc_functions import (
    bytes2human, create_unique_hash, mutually_exclusive, is_project_dir,
    find_project_dir, grep, prettify_datetime, format_table,
    parse_cli_key_value, convert_keys_to_string, get_datmo_temp_path,
    parse_path, parse_paths, list_all_filepaths)

from datmo.core.util.exceptions import MutuallyExclusiveArguments, RequiredArgumentMissing, InvalidDestinationName, PathDoesNotExist, TooManyArgumentsFound

class TestMiscFunctions():
    # TODO: Add more cases for each test
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if platform.system() != "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

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

    def test_bytes2human(self):
        # test the bytes2human method
        result = bytes2human(10000)
        assert result == '9.8K'

        result = bytes2human(100001221)
        assert result == '95.4M'

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

    def test_list_all_filepaths(self):
        # Create a file and a directory to test on
        filepath = os.path.join(self.temp_dir, "test.txt")
        dirpath = os.path.join(self.temp_dir, "test_dir")
        dirfilepath = os.path.join(dirpath, "test.txt")
        with open(filepath, "wb") as f:
            f.write(to_bytes("test" + "\n"))
        os.makedirs(dirpath)
        with open(dirfilepath, "wb") as f:
            f.write(to_bytes("test" + "\n"))
        # List all paths
        result = list_all_filepaths(self.temp_dir)
        assert len(result) == 2
        assert "test.txt" in result
        assert os.path.join("test_dir", "test.txt") in result

    def test_get_datmo_temp_path(self):
        datmo_temp_path = get_datmo_temp_path(self.temp_dir)
        exists = False
        if os.path.isdir(datmo_temp_path):
            exists = True
        assert exists
        # Test if subsequent temp dirs are different
        datmo_temp_path_1 = get_datmo_temp_path(self.temp_dir)
        assert datmo_temp_path != datmo_temp_path_1
        datmo_temp_path_2 = get_datmo_temp_path(self.temp_dir)
        assert datmo_temp_path != datmo_temp_path_2
        assert datmo_temp_path_1 != datmo_temp_path_2

    def test_parse_path(self):
        test_simple = os.path.join(self.temp_dir, "test.txt")
        test_path = os.path.join(self.temp_dir, "test.txt") + ">hello"
        test_windows_like = os.path.join("pre:pre", "test")
        test_windows_like_with_dest = os.path.join("pre:pre", "test>new")
        test_invalid_path = os.path.join(self.temp_dir,
                                         "test.txt") + ">" + os.path.join(
                                             self.temp_dir, "hello")
        test_invalid_path_2 = "test.txt>" + os.path.join(
            self.temp_dir, "hello")
        test_invalid_path_3 = "test.txt>new>third"

        src_path, dest_name = parse_path(test_simple)
        assert "test.txt" in src_path
        assert dest_name == "test.txt"

        src_path, dest_name = parse_path(test_path)
        assert "test.txt" in src_path
        assert dest_name == "hello"

        src_path, dest_name = parse_path(test_windows_like)
        assert src_path == os.path.join("pre:pre", "test")
        assert dest_name == "test"

        src_path, dest_name = parse_path(test_windows_like_with_dest)
        assert src_path == os.path.join("pre:pre", "test")
        assert dest_name == "new"

        failed = False
        try:
            _ = parse_path(test_invalid_path)
        except InvalidDestinationName:
            failed = True
        assert failed

        failed = False
        try:
            _ = parse_path(test_invalid_path_2)
        except InvalidDestinationName:
            failed = True
        assert failed

        failed = False
        try:
            _ = parse_path(test_invalid_path_3)
        except TooManyArgumentsFound:
            failed = True
        assert failed

    def test_parse_paths(self):
        # Create a file and a directory to test on
        filepath = os.path.join(self.temp_dir, "test.txt")
        dirpath = os.path.join(self.temp_dir, "test_dir")
        dirfilepath = os.path.join(dirpath, "test.txt")
        with open(filepath, "wb") as f:
            f.write(to_bytes("test" + "\n"))
        os.makedirs(dirpath)
        with open(dirfilepath, "wb") as f:
            f.write(to_bytes("test" + "\n"))
        # Define user paths
        default_source_prefix = self.temp_dir
        dest_prefix = os.path.join(self.temp_dir, "some_dest_dir")
        # Test default source path and default dest path
        paths = ["test.txt", "test_dir"]
        result = parse_paths(default_source_prefix, paths, dest_prefix)
        assert result[0] == [(os.path.join(default_source_prefix, "test.txt"),
                              os.path.join(dest_prefix, "test.txt"))]
        assert result[1] == [(os.path.join(default_source_prefix, "test_dir"),
                              os.path.join(dest_prefix, "test_dir"))]
        assert result[2] == [(os.path.join(default_source_prefix, "test.txt"),
                              "test.txt")]
        assert result[3] == [(os.path.join(default_source_prefix, "test_dir"),
                              "test_dir")]
        # Test absolute source path and no dest path
        paths = [filepath, dirpath]
        result = parse_paths(default_source_prefix, paths, dest_prefix)
        assert result[0] == [(filepath, os.path.join(dest_prefix, "test.txt"))]
        assert result[1] == [(dirpath, os.path.join(dest_prefix, "test_dir"))]
        assert result[2] == [(os.path.join(default_source_prefix, "test.txt"),
                              "test.txt")]
        assert result[3] == [(os.path.join(default_source_prefix, "test_dir"),
                              "test_dir")]
        # Test default source path and given dest path
        paths = ["test.txt>new_name.txt", "test_dir>new_dirname"]
        result = parse_paths(default_source_prefix, paths, dest_prefix)
        assert result[0] == [(os.path.join(default_source_prefix, "test.txt"),
                              os.path.join(dest_prefix, "new_name.txt"))]
        assert result[1] == [(os.path.join(default_source_prefix, "test_dir"),
                              os.path.join(dest_prefix, "new_dirname"))]
        assert result[2] == [(os.path.join(default_source_prefix, "test.txt"),
                              "new_name.txt")]
        assert result[3] == [(os.path.join(default_source_prefix, "test_dir"),
                              "new_dirname")]
        # Test failure if path does not exist
        paths = ["sldfkj.txt>new_name.txt", "sldkfj>new_dirname"]
        failed = False
        try:
            parse_paths(default_source_prefix, paths, dest_prefix)
        except PathDoesNotExist:
            failed = True
        assert failed
        # Test success absolute path and destination
        paths = [filepath + ">new_name.txt", dirpath + ">new_dirname"]
        result = parse_paths(default_source_prefix, paths, dest_prefix)
        assert result[0] == [(filepath,
                              os.path.join(dest_prefix, "new_name.txt"))]
        assert result[1] == [(dirpath, os.path.join(dest_prefix,
                                                    "new_dirname"))]
        assert result[2] == [(os.path.join(default_source_prefix, "test.txt"),
                              "new_name.txt")]
        assert result[3] == [(os.path.join(default_source_prefix, "test_dir"),
                              "new_dirname")]

    def test_convert_keys_to_string(self):
        test_data = {
            u'spam':
                u'eggs',
            u'foo':
                frozenset([u'Gah!']),
            u'bar': {
                u'baz': 97
            },
            u'list': [
                u'list', (True, u'Maybe'),
                set([u'and', u'a', u'set', 1])
            ]
        }

        converted_data = convert_keys_to_string(test_data)

        assert converted_data == {
            'bar': {
                'baz': 97
            },
            'foo': frozenset(['Gah!']),
            'list': ['list', (True, 'Maybe'),
                     set(['and', 'a', 'set', 1])],
            'spam': 'eggs'
        }
