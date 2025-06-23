"""
Tests for LocalDAL
"""

import os
import tempfile
import platform

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.storage.local.dal import LocalDAL
from datmo.core.util.exceptions import EntityNotFound, EntityCollectionNotFound

class TestLocalDAL():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.driver_type = "blitzdb"
        self.driver_options = {
            "driver_type": "file",
            "connection_string": self.temp_dir
        }

    def teardown_class(self):
        pass

    def test_init(self):
        dal = LocalDAL(self.driver_type, self.driver_options)
        assert dal != None

    def test_get_by_id_unknown_entity(self):
        exp_thrown = False
        dal = LocalDAL(self.driver_type, self.driver_options)
        try:
            dal.model.get_by_id("not_found")
        except EntityNotFound:
            exp_thrown = True
        except EntityCollectionNotFound:
            exp_thrown = True
        assert exp_thrown
