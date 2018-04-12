"""
Tests for file_storage.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import tempfile
import os

from datmo.util.json_store import JSONStore


class TestFileStorage():
    def setup_class(self):
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.storage_file = os.path.join(self.temp_dir, 'testing.json')

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        storage = JSONStore(self.storage_file)
        assert storage.filepath == self.storage_file

    def test_save(self):
        storage = JSONStore(self.storage_file)
        storage.save('foobar', 'yep')
        found_it = False
        if 'foobar' in open(self.storage_file).read():
            found_it = True
        assert found_it

    def test_get_string(self):
        storage = JSONStore(self.storage_file)
        key = 'foobar1'
        value = 'disco'
        storage.save(key, value)
        return_value = storage.get(key)
        assert return_value == value

    def test_get_obj(self):
        storage = JSONStore(self.storage_file)
        key = 'foobar1'
        value = {"does this work":"noway"}
        storage.save(key, value)
        return_value = storage.get(key)
        assert return_value == value

