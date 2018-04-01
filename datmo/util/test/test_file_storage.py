"""
Tests for Datmo Local
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import tempfile
import os

from ..file_storage import JSONKeyValueStore

class TestDatmoDAL():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage_file = os.path.join(self.temp_dir, 'testing.json')

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        storage = JSONKeyValueStore(self.storage_file)
        assert storage.filepath == self.storage_file

    def test_save(self):
        storage = JSONKeyValueStore(self.storage_file)
        storage.save('foobar', 'yep')
        found_it = False
        if 'foobar' in open(self.storage_file).read():
            found_it = True
        assert found_it

    def test_get_string(self):
        storage = JSONKeyValueStore(self.storage_file)
        key = 'foobar1'
        value = 'disco'
        storage.save(key, value)
        return_value = storage.get(key)
        assert return_value == value

    def test_get_obj(self):
        storage = JSONKeyValueStore(self.storage_file)
        key = 'foobar1'
        value = {"does this work":"noway"}
        storage.save(key, value)
        return_value = storage.get(key)
        assert return_value == value

