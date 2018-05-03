"""
Tests for misc_functions.py
"""
import os
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.util.misc_functions import get_filehash, \
    create_unique_hash, mutually_exclusive
from datmo.core.util.exceptions import MutuallyExclusiveArguments

class TestMiscFunctions():
    # TODO: Add more cases for each test
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def test_get_filehash(self):
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, "w") as f:
            f.write(to_unicode("hello\n"))
        result = get_filehash(filepath)
        assert result == "b1946ac92492d2347c6235b4d2611184"

    def test_create_unique_hash(self):
        result_hash_1 = create_unique_hash()
        result_hash_2 = create_unique_hash()

        assert result_hash_1 != result_hash_2

    def test_mutually_exclusive(self):
        mutually_exclusive_args = ["code_id", "commit_id"]
        arguments_dictionary = {
            'code_id': 'test_code_id',
            'environment_id': 'test_environment_id'
        }
        dictionary = {}
        mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                           dictionary)
        assert dictionary
        assert dictionary['code_id'] == arguments_dictionary['code_id']

        update_dictionary_failed = False
        try:
            mutually_exclusive_args = ["code_id", "commit_id"]
            arguments_dictionary = {
                'code_id': 'test_code_id',
                'commit_id': 'test_environment_id'
            }
            dictionary = {}
            mutually_exclusive(mutually_exclusive_args, arguments_dictionary,
                               dictionary)
        except MutuallyExclusiveArguments:
            update_dictionary_failed = True
        assert update_dictionary_failed

    def test_find_project_dir(self):
        # TODO:
        pass

    def test_is_project_dir(self):
        # TODO:
        pass