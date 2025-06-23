"""
Tests for LocalDAL
"""

import os
import tempfile
import platform
from datetime import datetime

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.storage.local.dal import LocalDAL
from datmo.core.entity.model import Model
from datmo.core.entity.code import Code
from datmo.core.util.exceptions import EntityNotFound

class TestLocalDAL():
    def setup_method(self):
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

        self.dal = LocalDAL(self.driver_type, self.driver_options)
        model_name = "model_1"
        model = self.dal.model.create(Model({"name": model_name}))

        self.code_input_dict = {
            "model_id": model.id,
            "driver_type": "git",
            "commit_id": "commit_id"
        }

    def teardown_method(self):
        pass

    def test_create_code_by_dictionary(self):

        code = self.dal.code.create(Code(self.code_input_dict))

        assert code.id
        assert code.model_id == self.code_input_dict['model_id']
        assert code.driver_type == self.code_input_dict['driver_type']
        assert code.commit_id == self.code_input_dict['commit_id']
        assert code.created_at
        assert code.updated_at

        code_2 = self.dal.code.create(Code(self.code_input_dict))

        assert code_2.id != code.id

        test_code_input_dict = self.code_input_dict.copy()
        test_code_input_dict['id'] = "id_1"
        code_3 = self.dal.code.create(Code(test_code_input_dict))

        assert code_3.id == test_code_input_dict['id']

    def test_get_by_id_code(self):
        code = self.dal.code.create(Code(self.code_input_dict))
        result = self.dal.code.get_by_id(code.id)
        assert code.id == result.id

    def test_get_by_shotened_id_code(self):
        code = self.dal.code.create(Code(self.code_input_dict))
        result = self.dal.code.get_by_shortened_id(code.id[:10])
        assert code.id == result.id

    def test_get_by_id_code_new_driver_instance(self):
        code = self.dal.code.create(Code(self.code_input_dict))

        # create new dal with new driver instance (success)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(
            self.driver_type, self.driver_options, driver=new_driver_instance)
        new_code_1 = new_dal_instance.code.get_by_id(code.id)
        assert new_code_1.id == code.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.driver_type, self.driver_options)
        new_code_2 = new_dal_instance.code.get_by_id(code.id)
        assert new_code_2.id == code.id

    def test_update_code(self):
        code = self.dal.code.create(Code(self.code_input_dict))

        # Update required and optional parameters
        updated_code_input_dict = self.code_input_dict.copy()
        updated_code_input_dict['id'] = code.id
        updated_code_input_dict['driver_type'] = "new_driver"
        updated_code_input_dict['created_at'] = datetime.utcnow()
        updated_code = self.dal.code.update(updated_code_input_dict)
        assert code.id == updated_code.id
        assert code.updated_at < updated_code.updated_at
        assert updated_code.driver_type == updated_code_input_dict[
            'driver_type']
        assert updated_code.created_at == updated_code_input_dict['created_at']

    def test_delete_code(self):
        code = self.dal.code.create(Code(self.code_input_dict))

        self.dal.code.delete(code.id)
        deleted = False
        try:
            self.dal.code.get_by_id(code.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_codes(self):
        code = self.dal.code.create(Code(self.code_input_dict))

        assert len(self.dal.code.query({"id": code.id})) == 1

    def test_query_codes_range_query(self):
        _ = self.dal.code.create(Code(self.code_input_dict))
        _ = self.dal.code.create(Code(self.code_input_dict))
        _ = self.dal.code.create(Code(self.code_input_dict))
        codes = self.dal.code.query(
            {}, sort_key="created_at", sort_order="descending")
        result = self.dal.code.query({
            "created_at": {
                "$lt": codes[1].created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        })
        assert len(codes) == 3
        assert len(result) == 1
