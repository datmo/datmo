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
from datmo.core.entity.file_collection import FileCollection
from datmo.core.util.exceptions import EntityNotFound, InvalidArgumentType

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

        self.file_collection_input_dict = {
            "model_id": model.id,
            "driver_type": "local",
            "filehash": "myhash",
            "path": "test_path",
        }

    def teardown_method(self):
        pass

    def test_create_file_collection_by_dictionary(self):

        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        assert file_collection.id
        assert file_collection.model_id == self.file_collection_input_dict[
            'model_id']
        assert file_collection.driver_type == self.file_collection_input_dict[
            'driver_type']
        assert file_collection.filehash == self.file_collection_input_dict[
            'filehash']
        assert file_collection.path == self.file_collection_input_dict['path']
        assert file_collection.created_at
        assert file_collection.updated_at

        file_collection_2 = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        assert file_collection_2.id != file_collection.id

        test_file_collection_input_dict = self.file_collection_input_dict.copy(
        )
        test_file_collection_input_dict['id'] = "file_collection_id"
        file_collection_3 = self.dal.file_collection.create(
            FileCollection(test_file_collection_input_dict))

        assert file_collection_3.id == test_file_collection_input_dict['id']

    def test_get_by_id_file_collection(self):
        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        result = self.dal.file_collection.get_by_id(file_collection.id)
        assert file_collection.id == result.id

    def test_get_by_shortened_id_file_collection(self):
        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        result = self.dal.file_collection.get_by_shortened_id(
            file_collection.id[:10])
        assert file_collection.id == result.id

    def test_get_by_id_file_collection_new_driver_instance(self):
        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        # create new dal with new driver instance (success)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(
            self.driver_type, self.driver_options, driver=new_driver_instance)
        new_file_collection_1 = new_dal_instance.file_collection.get_by_id(
            file_collection.id)
        assert new_file_collection_1.id == file_collection.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.driver_type, self.driver_options)
        new_file_collection_2 = new_dal_instance.file_collection.get_by_id(
            file_collection.id)
        assert new_file_collection_2.id == file_collection.id

    def test_update_file_collection(self):
        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        # Update required and optional parameters
        updated_file_collection_input_dict = self.file_collection_input_dict.copy(
        )
        updated_file_collection_input_dict['id'] = file_collection.id
        updated_file_collection_input_dict['driver_type'] = "new_driver"
        updated_file_collection_input_dict['created_at'] = datetime.utcnow()
        updated_file_collection = self.dal.file_collection.update(
            updated_file_collection_input_dict)
        assert file_collection.id == updated_file_collection.id
        assert file_collection.updated_at < updated_file_collection.updated_at
        assert updated_file_collection.driver_type == updated_file_collection_input_dict[
            'driver_type']
        assert updated_file_collection.created_at == updated_file_collection_input_dict[
            'created_at']

    def test_delete_file_collection(self):
        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        self.dal.file_collection.delete(file_collection.id)
        deleted = False
        try:
            self.dal.file_collection.get_by_id(file_collection.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_file_collections_basic(self):
        file_collection = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        assert len(self.dal.file_collection.query({
            "id": file_collection.id
        })) == 1

    def test_query_file_collections_multiple(self):
        file_collection_1 = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))
        file_collection_2 = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))
        file_collection_3 = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))

        results = self.dal.file_collection.query(
            {}, sort_key="created_at", sort_order="ascending")
        assert len(results) == 3
        assert results[0].created_at == file_collection_1.created_at
        assert results[1].created_at == file_collection_2.created_at

        results = self.dal.file_collection.query(
            {}, sort_key="created_at", sort_order="descending")
        assert len(results) == 3
        assert results[0].created_at == file_collection_3.created_at
        assert results[1].created_at == file_collection_2.created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.dal.file_collection.query(
                {}, sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.dal.file_collection.query(
                {}, sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.dal.file_collection.query(
            {}, sort_key='created_at', sort_order='ascending')
        items = self.dal.file_collection.query(
            {}, sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_items]
        ids = [item.id for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_file_collections_range_query(self):
        _ = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))
        _ = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))
        _ = self.dal.file_collection.create(
            FileCollection(self.file_collection_input_dict))
        file_collections = self.dal.file_collection.query(
            {}, sort_key="created_at", sort_order="descending")
        result = self.dal.file_collection.query({
            "created_at": {
                "$lt":
                    file_collections[1]
                    .created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        })
        assert len(file_collections) == 3
        assert len(result) == 1
