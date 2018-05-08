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
from datmo.core.entity.user import User
from datmo.core.util.exceptions import EntityNotFound, InvalidArgumentType


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
        self.user_input_dict = {
            "name": "user_1",
            "email": "test@test.com",
        }

    def teardown_class(self):
        pass

    def test_create_user_by_dictionary(self):
        user = self.dal.user.create(User(self.user_input_dict))
        assert user.id
        assert user.name == self.user_input_dict['name']
        assert user.created_at
        assert user.updated_at

        user_2 = self.dal.user.create(User(self.user_input_dict))
        assert user_2.id != user.id

        test_user_input_dict = self.user_input_dict.copy()
        test_user_input_dict['id'] = "user_id"
        user_3 = self.dal.user.create(User(test_user_input_dict))
        assert user_3.id == test_user_input_dict['id']

    def test_get_by_id_user(self):
        user = self.dal.user.create(User(self.user_input_dict))

        result = self.dal.user.get_by_id(user.id)
        assert user.id == result.id

    def test_get_by_id_user_new_driver_instance(self):
        user = self.dal.user.create(User(self.user_input_dict))

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        new_user_1 = new_dal_instance.user.get_by_id(user.id)
        assert new_user_1.id == user.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_user_2 = new_dal_instance.user.get_by_id(user.id)
        assert new_user_2.id == user.id

    def test_update_user(self):
        user = self.dal.user.create(User(self.user_input_dict))

        # Update required and optional parameters
        updated_user_input_dict = self.user_input_dict.copy()
        updated_user_input_dict['id'] = user.id
        updated_user_input_dict['name'] = "cooldude"
        updated_user_input_dict['created_at'] = datetime.utcnow()
        updated_user = self.dal.user.update(updated_user_input_dict)

        assert user.id == updated_user.id
        assert user.updated_at < updated_user.updated_at
        assert updated_user.name == updated_user_input_dict['name']
        assert updated_user.created_at == updated_user_input_dict['created_at']

    def test_delete_user(self):
        user = self.dal.user.create(User(self.user_input_dict))

        self.dal.user.delete(user.id)
        deleted = False
        try:
            self.dal.user.get_by_id(user.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_users(self):
        user = self.dal.user.create(User(self.user_input_dict))

        assert len(self.dal.user.query({"id": user.id})) == 1
        assert len(
            self.dal.user.query({
                "name": self.user_input_dict['name']
            })) == 6

        user_input_dict_1 = {
            "name": "user_2",
            "email": "test@test.com",
            "created_at": datetime(2017, 1, 1)
        }

        user_input_dict_2 = {
            "name": "user_2",
            "email": "test@test.com",
            "created_at": datetime(2017, 2, 1)
        }

        user_input_dict_3 = {
            "name": "user_2",
            "email": "test@test.com",
            "created_at": datetime(2017, 3, 1)
        }

        self.dal.user.create(User(user_input_dict_1))
        self.dal.user.create(User(user_input_dict_2))
        self.dal.user.create(User(user_input_dict_3))

        results = self.dal.user.query(
            {
                "name": "user_2"
            }, sort_key="created_at", sort_order="ascending")
        assert len(results) == 3
        assert results[0].created_at == user_input_dict_1["created_at"]

        results = self.dal.user.query(
            {
                "name": "user_2"
            }, sort_key="created_at", sort_order="descending")
        assert len(results) == 3
        assert results[0].created_at == user_input_dict_3["created_at"]

        # Wrong order being passed in
        failed = False
        try:
            _ = self.dal.user.query(
                {
                    "name": "user_2"
                },
                sort_key='created_at',
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.dal.user.query(
                {
                    "name": "user_2"
                },
                sort_key='wrong_key',
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.dal.user.query(
            {
                "name": "user_2"
            }, sort_key='created_at', sort_order='ascending')
        items = self.dal.user.query(
            {
                "name": "user_2"
            }, sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_items]
        ids = [item.id for item in items]
        assert set(expected_ids) == set(ids)
