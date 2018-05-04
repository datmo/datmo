"""
Tests for LocalDAL
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import platform

from datetime import datetime
from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.storage.local.dal import LocalDAL
from datmo.core.entity.model import Model
from datmo.core.entity.session import Session
from datmo.core.entity.snapshot import Snapshot
from datmo.core.util.exceptions import EntityNotFound


class TestLocalDAL():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.datadriver = BlitzDBDALDriver("file", self.temp_dir)

        self.dal = LocalDAL(self.datadriver)
        model_name = "model_1"
        model = self.dal.model.create(Model({"name": model_name}))
        session_name = "session_1"
        session = self.dal.session.create(
            Session({
                "name": session_name,
                "model_id": model.id
            }))

        self.snapshot_input_dict = {
            "model_id": model.id,
            "session_id": session.id,
            "message": "my message",
            "code_id": "code_id",
            "environment_id": "environment_id",
            "file_collection_id": "file_collection_id",
            "config": {"test": 0.45},
            "stats": {"test": 0.98},
            "created_at": datetime(2017, 2, 1)
        }

        self.snapshot_input_dict_1 = {
            "model_id": model.id,
            "session_id": session.id,
            "message": "my message for 1",
            "code_id": "code_id",
            "environment_id": "environment_id",
            "file_collection_id": "file_collection_id",
            "config": {"test": 0.90},
            "stats": {"test": 1.23},
            "created_at": datetime(2017, 3, 1)
        }

    def teardown_class(self):
        pass

    def test_create_snapshot_by_dictionary(self):
        snapshot = self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))
        assert snapshot.id
        assert snapshot.model_id == self.snapshot_input_dict['model_id']
        assert snapshot.session_id == self.snapshot_input_dict['session_id']
        assert snapshot.message == self.snapshot_input_dict['message']
        assert snapshot.code_id == self.snapshot_input_dict['code_id']
        assert snapshot.environment_id == self.snapshot_input_dict[
            'environment_id']
        assert snapshot.file_collection_id == self.snapshot_input_dict[
            'file_collection_id']
        assert snapshot.config == self.snapshot_input_dict['config']
        assert snapshot.stats == self.snapshot_input_dict['stats']
        assert snapshot.created_at
        assert snapshot.updated_at

        snapshot_2 = self.dal.snapshot.create(
            Snapshot(self.snapshot_input_dict))

        assert snapshot_2.id != snapshot.id

        test_snapshot_input_dict = self.snapshot_input_dict.copy()
        test_snapshot_input_dict['id'] = "snapshot_id"
        snapshot_3 = self.dal.snapshot.create(
            Snapshot(test_snapshot_input_dict))

        assert snapshot_3.id == test_snapshot_input_dict['id']

    def test_get_by_id_snapshot(self):
        snapshot = self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))

        result = self.dal.snapshot.get_by_id(snapshot.id)
        assert snapshot.id == result.id

    def test_get_by_id_snapshot_new_driver_instance(self):
        snapshot = self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        new_snapshot_1 = new_dal_instance.snapshot.get_by_id(snapshot.id)
        assert new_snapshot_1.id == snapshot.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_snapshot_2 = new_dal_instance.snapshot.get_by_id(snapshot.id)
        assert new_snapshot_2.id == snapshot.id

    def test_update_snapshot(self):
        snapshot = self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))

        # Update required and optional parameters
        updated_snapshot_input_dict = self.snapshot_input_dict.copy()
        updated_snapshot_input_dict['id'] = snapshot.id
        updated_snapshot_input_dict['message'] = "this is really cool"
        updated_snapshot_input_dict['label'] = "new"
        updated_snapshot = self.dal.snapshot.update(
            updated_snapshot_input_dict)

        assert snapshot.id == updated_snapshot.id
        assert snapshot.updated_at < updated_snapshot.updated_at
        assert updated_snapshot.message == updated_snapshot_input_dict[
            'message']
        assert updated_snapshot.label == updated_snapshot_input_dict['label']

    def test_delete_snapshot(self):
        snapshot = self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))

        self.dal.snapshot.delete(snapshot.id)
        deleted = False
        try:
            self.dal.snapshot.get_by_id(snapshot.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_snapshots(self):
        snapshot = self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))

        # All snapshots created are the same, 1 is deleted => 7
        assert len(self.dal.snapshot.query({"id": snapshot.id})) == 1
        assert len(self.dal.snapshot.query({"code_id": self.snapshot_input_dict['code_id']})) == 7
        assert len(self.dal.snapshot.query({"visible": True})) == 7

    def test_sort_snapshots(self):
        self.dal.snapshot.create(Snapshot(self.snapshot_input_dict))
        self.dal.snapshot.create(Snapshot(self.snapshot_input_dict_1))

        # Sorting of snapshot in descending
        items = self.dal.snapshot.query({"model_id": self.snapshot_input_dict["model_id"]},
                                        sort_key='created_at', sort_order='descending')
        assert items[0].created_at == self.snapshot_input_dict_1["created_at"]

        # Sorting of snapshot in ascending
        items = self.dal.snapshot.query({"model_id": self.snapshot_input_dict["model_id"]},
                                        sort_key='created_at', sort_order='ascending')
        assert items[0].created_at == self.snapshot_input_dict["created_at"]

        # Random variable being passed in
        expected_items = self.dal.snapshot.query({"model_id": self.snapshot_input_dict["model_id"]})
        items = self.dal.snapshot.query({"model_id": self.snapshot_input_dict["model_id"]},
                                        sort_key='wrong_variable', sort_order='wrong_order')
        assert len(items) == len(expected_items)
