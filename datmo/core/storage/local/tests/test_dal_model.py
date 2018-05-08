"""
Tests for LocalDAL
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile
import platform

from datetime import datetime

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.storage.local.dal import LocalDAL
from datmo.core.entity.model import Model
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
        model_name = "model_1"
        self.model_input_dict = {"name": model_name}

    def teardown_class(self):
        pass

    def test_create_model_by_dictionary(self):
        model = self.dal.model.create(Model(self.model_input_dict))
        assert model.id
        assert model.name == self.model_input_dict['name']
        assert model.created_at
        assert model.updated_at

        model_2 = self.dal.model.create(Model(self.model_input_dict))
        assert model.id != model_2.id

        test_model_input_dict = self.model_input_dict.copy()
        test_model_input_dict['id'] = "cool"
        model_3 = self.dal.model.create(Model(test_model_input_dict))
        assert model_3.id == test_model_input_dict['id']

    def test_get_by_id_model(self):
        model = self.dal.model.create(Model(self.model_input_dict))
        result = self.dal.model.get_by_id(model.id)
        assert model.id == result.id

    def test_get_by_id_model_same_dir(self):
        test_dir = "test-dir"
        datadriver = BlitzDBDALDriver("file", test_dir)
        dal = LocalDAL(datadriver)
        model1 = dal.model.create(Model(self.model_input_dict))
        del datadriver
        del dal
        datadriver = BlitzDBDALDriver("file", test_dir)
        dal = LocalDAL(datadriver)
        model2 = dal.model.create(Model(self.model_input_dict))
        del datadriver
        del dal
        datadriver = BlitzDBDALDriver("file", test_dir)
        dal = LocalDAL(datadriver)
        model3 = dal.model.create(Model(self.model_input_dict))

        model1 = dal.model.get_by_id(model1.id)
        model2 = dal.model.get_by_id(model2.id)
        model3 = dal.model.get_by_id(model3.id)

        assert model1
        assert model2
        assert model3

        shutil.rmtree(test_dir)

    def test_get_by_id_model_new_driver_instance(self):
        model = self.dal.model.create(Model(self.model_input_dict))
        # create new dal with new driver instance (success)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        new_model_1 = new_dal_instance.model.get_by_id(model.id)
        assert new_model_1.id == model.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_model_2 = new_dal_instance.model.get_by_id(model.id)
        assert new_model_2.id == model.id

    def test_update_model(self):
        model = self.dal.model.create(Model(self.model_input_dict))

        # Update required and optional parameters
        updated_model_input_dict = self.model_input_dict.copy()
        updated_model_input_dict['id'] = model.id
        updated_model_input_dict['name'] = "model_4a"
        updated_model_input_dict['description'] = "this is a cool model"
        updated_model = self.dal.model.update(updated_model_input_dict)
        assert model.id == updated_model.id
        assert model.updated_at < updated_model.updated_at
        assert updated_model.name == updated_model_input_dict['name']
        assert updated_model.description == updated_model_input_dict[
            'description']

    def test_delete_model(self):
        model = self.dal.model.create(Model(self.model_input_dict))

        self.dal.model.delete(model.id)

        deleted = False
        try:
            self.dal.model.get_by_id(model.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_models(self):
        model = self.dal.model.create(Model(self.model_input_dict))
        assert len(self.dal.model.query({"id": model.id})) == 1
        assert len(
            self.dal.model.query({
                "name": self.model_input_dict['name']
            })) == 6

        # Query for multiple models
        model_input_dict_1 = {
            "name": "model_sort",
            "created_at": datetime(2017, 1, 1)
        }
        model_input_dict_2 = {
            "name": "model_sort",
            "created_at": datetime(2017, 2, 1)
        }
        model_input_dict_3 = {
            "name": "model_sort",
            "created_at": datetime(2017, 3, 1)
        }

        self.dal.model.create(Model(model_input_dict_1))
        self.dal.model.create(Model(model_input_dict_2))
        self.dal.model.create(Model(model_input_dict_3))

        results = self.dal.model.query(
            {
                "name": "model_sort"
            },
            sort_key="created_at",
            sort_order="ascending")
        assert len(results) == 3
        assert results[0].created_at == model_input_dict_1["created_at"]

        results = self.dal.model.query(
            {
                "name": "model_sort"
            },
            sort_key="created_at",
            sort_order="descending")
        assert len(results) == 3
        assert results[0].created_at == model_input_dict_3["created_at"]

        # Wrong order being passed in
        failed = False
        try:
            _ = self.dal.model.query(
                {
                    "name": "model_sort"
                },
                sort_key='created_at',
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.dal.model.query(
                {
                    "name": "model_sort"
                },
                sort_key='wrong_key',
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.dal.model.query(
            {
                "name": "model_sort"
            },
            sort_key='created_at',
            sort_order='ascending')
        items = self.dal.model.query(
            {
                "name": "model_sort"
            },
            sort_key='wrong_key',
            sort_order='ascending')
        expected_ids = [item.id for item in expected_items]
        ids = [item.id for item in items]
        assert set(expected_ids) == set(ids)
