"""
Tests for LocalDAL
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.storage.local.dal import LocalDAL
from datmo.core.util.exceptions import EntityNotFound, EntityCollectionNotFound


class TestLocalDAL():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.datadriver = BlitzDBDALDriver("file", self.temp_dir)

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        dal = LocalDAL(self.datadriver)
        assert dal != None

    def test_get_by_id_unknown_entity(self):
        exp_thrown = False
        dal = LocalDAL(self.datadriver)
        try:
            dal.model.get_by_id("not_found")
        except EntityNotFound:
            exp_thrown = True
        except EntityCollectionNotFound:
            exp_thrown = True
        assert exp_thrown