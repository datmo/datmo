"""
Tests for misc_functions.py
"""
import tempfile

from datmo.util.misc_functions import *


class TestMiscFunctions():
    # TODO: Add more cases for each test
    def setup_method(self):
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def test_get_filehash(self):
        filepath =  os.path.join(self.temp_dir, "test.txt")
        with open(filepath, "w") as f:
            f.write("hello\n")
        result = get_filehash(filepath)
        assert result == "b1946ac92492d2347c6235b4d2611184"