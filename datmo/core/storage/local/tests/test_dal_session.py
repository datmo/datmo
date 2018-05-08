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
from datmo.core.util.exceptions import EntityNotFound, InvalidArgumentType


class TestLocalDAL():
    def setup_method(self):
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

        self.session_input_dict = {
            "name": "session_1",
            "model_id": model.id,
        }

    def teardown_method(self):
        pass

    def test_create_session_by_dictionary(self):
        session = self.dal.session.create(Session(self.session_input_dict))

        assert session.id
        assert session.name == self.session_input_dict['name']
        assert session.created_at
        assert session.updated_at

        session_2 = self.dal.session.create(Session(self.session_input_dict))

        assert session_2.id != session.id

        test_session_input_dict = self.session_input_dict.copy()
        test_session_input_dict['id'] = "session_id"

        session_3 = self.dal.session.create(Session(test_session_input_dict))

        assert session_3.id == test_session_input_dict['id']

    def test_get_by_id_session(self):
        session = self.dal.session.create(Session(self.session_input_dict))

        result = self.dal.session.get_by_id(session.id)
        assert session.id == result.id

    def test_get_by_id_session_new_driver_instance(self):
        session = self.dal.session.create(Session(self.session_input_dict))

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        new_session_1 = new_dal_instance.session.get_by_id(session.id)
        assert new_session_1.id == session.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_session_2 = new_dal_instance.session.get_by_id(session.id)
        assert new_session_2.id == session.id

    def test_update_session(self):
        session = self.dal.session.create(Session(self.session_input_dict))

        # Update required and optional parameters
        updated_session_input_dict = self.session_input_dict.copy()
        updated_session_input_dict['id'] = session.id
        updated_session_input_dict['name'] = "session_yo"
        updated_session_input_dict['created_at'] = datetime.utcnow()
        updated_session = self.dal.session.update(updated_session_input_dict)

        assert session.id == updated_session.id
        assert session.updated_at < updated_session.updated_at
        assert updated_session.name == updated_session_input_dict['name']
        assert updated_session.created_at == updated_session_input_dict[
            'created_at']

    def test_delete_session(self):
        session = self.dal.session.create(Session(self.session_input_dict))

        self.dal.session.delete(session.id)
        deleted = False
        try:
            self.dal.session.get_by_id(session.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_sessions(self):
        session = self.dal.session.create(Session(self.session_input_dict))

        assert len(self.dal.session.query({"id": session.id})) == 1
        _ = self.dal.session.create(Session(self.session_input_dict))
        assert len(
            self.dal.session.query({
                "name": self.session_input_dict['name']
            })) == 2

    def test_sort_sessions(self):
        session_1 = self.dal.session.create(Session(self.session_input_dict))
        session_2 = self.dal.session.create(Session(self.session_input_dict))

        # Sorting of snapshot in descending
        items = self.dal.session.query(
            {
                "name": self.session_input_dict['name']
            },
            sort_key="created_at",
            sort_order="descending")
        assert items[0].created_at == session_2.created_at

        # Sorting of snapshot in ascending
        items = self.dal.session.query(
            {
                "name": self.session_input_dict["name"]
            },
            sort_key="created_at",
            sort_order="ascending")
        assert items[0].created_at == session_1.created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.dal.session.query(
                {
                    "name": self.session_input_dict['name']
                },
                sort_key="created_at",
                sort_order="wrong_order")
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.dal.session.query(
                {
                    "name": self.session_input_dict["name"]
                },
                sort_key="wrong_key",
                sort_order="wrong_order")
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.dal.session.query(
            {
                "name": self.session_input_dict["name"]
            },
            sort_key="created_at",
            sort_order="ascending")
        items = self.dal.session.query(
            {
                "name": self.session_input_dict["name"]
            },
            sort_key="wrong_key",
            sort_order="ascending")
        expected_ids = [item.id for item in expected_items]
        ids = [item.id for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_sessions_range_query(self):
        _ = self.dal.session.create(Session(self.session_input_dict))
        _ = self.dal.session.create(Session(self.session_input_dict))
        _ = self.dal.session.create(Session(self.session_input_dict))
        sessions = self.dal.session.query(
            {}, sort_key="created_at", sort_order="descending")
        result = self.dal.session.query({
            "created_at": {
                "$lt": sessions[1].created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        })
        assert len(sessions) == 3
        assert len(result) == 1
