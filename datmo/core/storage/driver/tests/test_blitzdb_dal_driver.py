"""
Tests for blitzdb_dal_driver.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import datetime
import platform

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.util.exceptions import EntityNotFound, InvalidArgumentType


class TestBlitzDBDALDriverInit():
    """
    Checks init of BlitzDBDALDriver
    """

    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_class(self):
        pass

    def test_file_db_init(self):
        database = BlitzDBDALDriver("file", self.temp_dir)
        assert database != None

    def test_remote_db_init(self):
        mongo_connection = "mongodb://localhost:27017"
        # Make mongo db connection required for testing?
        database = BlitzDBDALDriver("service", mongo_connection)
        assert database != None


class TestBlitzDBDALDriver():
    """
    Checks all functions of BlitzDBDALDriver
    """

    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # TODO: Automatically create Document class from collection
        # For now, use one of pre-defined collections:
        # model, datmo_session, datmo_task, datmo_snapshot, datmo_user
        self.collection = 'model'
        self.database = BlitzDBDALDriver("file", self.temp_dir)

    def teardown_class(self):
        pass

    def test_filebased_db(self):
        assert self.database != None

    def test_db_set(self):
        test_obj = {"foo": "bar"}
        result = self.database.set(self.collection, test_obj)
        assert result.get('id') != None

    def test_db_get(self):
        test_obj = {"foo": "bar_1"}
        result = self.database.set(self.collection, test_obj)
        result1 = self.database.get(self.collection, result.get('id'))
        assert result1.get('id') == result.get('id')

    def test_db_update(self):
        test_obj = {"foo": "bar_2"}
        result = self.database.set(self.collection, test_obj)
        test_obj2 = {"id": result.get('id'), "foo": "bar_3"}
        result2 = self.database.set(self.collection, test_obj2)
        assert result.get('id') == result2.get('id')
        assert result2.get('foo') == "bar_3"

    def test_db_query(self):
        test_obj = {"foo": "bar"}
        results = self.database.query(self.collection, test_obj)
        assert len(results) == 1

    def test_db_query_bool(self):
        test_obj = {"bool": True}
        result = self.database.set(self.collection, test_obj)
        results = self.database.query(self.collection, test_obj)
        assert result.get('id') == results[0].get('id')

    def test_db_exists(self):
        test_obj = {"foo": "bar_2"}
        result = self.database.set(self.collection, test_obj)
        assert self.database.exists(self.collection, result.get('id'))
        assert not self.database.exists(self.collection, 'not_found')

    def test_db_query_all(self):
        results = self.database.query(self.collection, {})
        assert len(results) == 5
        # ensure each entity returns an 'id'
        for entity in results:
            assert entity['id'] != None

    def test_raise_entity_not_found(self):
        exp_thrown = False
        try:
            _ = self.database.get(self.collection, 'not_found')
        except EntityNotFound:
            exp_thrown = True
        assert exp_thrown

    def test_delete_entity(self):
        test_obj = {"name": "delete_me"}
        obj_to_delete = self.database.set(self.collection, test_obj)
        result = self.database.delete(self.collection, obj_to_delete.get('id'))
        exp_thrown = False
        try:
            result = self.database.get(self.collection,
                                       obj_to_delete.get('id'))
        except EntityNotFound:
            exp_thrown = True
        assert exp_thrown

    def test_document_type_2(self):
        """
        Collections are associated to a specific class, so
        this should fail
        """

        test_obj = {"car": "baz"}
        collection_2 = self.collection + '_2'
        thrown = False
        try:
            result = self.database.set(collection_2, test_obj)
        except:
            thrown = True
        assert thrown

    def test_multiple_blitzdb_objects(self):
        database_2 = BlitzDBDALDriver("file", self.temp_dir)
        test_obj_dict = {"foo": "bar"}
        test_obj = database_2.set(self.collection, test_obj_dict)
        # new_test_obj = database_2.get(self.collection, test_obj.get('id'))
        results_2 = database_2.query(self.collection, {})
        # Try a new data base
        database_3 = BlitzDBDALDriver("file", self.temp_dir)
        results_3 = database_3.query(self.collection, {})

        assert len(results_2) == len(results_3)

    def test_multiple_blitzdb_objects_intermediate_creation(self):
        # Test to check failure for intermediate creation
        database_2 = BlitzDBDALDriver("file", self.temp_dir)
        database_3 = BlitzDBDALDriver("file", self.temp_dir)
        test_obj_dict = {"foo": "bar"}
        # Set value after instantiation of database_3
        test_obj = database_2.set(self.collection, test_obj_dict)
        # Try to retrieve value from database_3
        test_obj_3 = database_3.get(self.collection, test_obj['id'])
        # Test to ensure the intermediate object is found
        assert test_obj_3['id'] == test_obj['id']

    def test_query_gte_int(self):
        collection = 'snapshot'
        self.database.set(collection, {"range_query": 1})
        self.database.set(collection, {"range_query": 2})
        self.database.set(collection, {"range_query": 3})

        items = self.database.query(collection, {"range_query": {"$gte": 2}})
        assert len(items) == 2

    def test_query_gte_date_str(self):
        collection = 'snapshot'
        self.database.set(
            collection, {
                "range_query2":
                    datetime.datetime(2017, 1, 1)
                    .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })
        self.database.set(
            collection, {
                "range_query2":
                    datetime.datetime(2017, 2, 1)
                    .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })
        self.database.set(
            collection, {
                "range_query2":
                    datetime.datetime(2017, 3, 1)
                    .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })

        items = self.database.query(
            collection, {
                "range_query2": {
                    "$gte":
                        datetime.datetime(2017, 2, 1)
                        .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            })
        assert len(items) == 2

    def test_query_gte_datetime_should_fail(self):
        collection = 'snapshot'
        self.database.set(collection,
                          {"range_query3": datetime.datetime(2017, 1, 1)})
        self.database.set(collection,
                          {"range_query3": datetime.datetime(2017, 2, 1)})
        self.database.set(collection,
                          {"range_query3": datetime.datetime(2017, 3, 1)})

        failed = False
        try:
            _ = self.database.query(
                collection,
                {"range_query2": {
                    "$gte": datetime.datetime(2017, 2, 1)
                }})
        except:
            failed = True
        assert failed

    def test_query_sort_date_str(self):
        collection = 'snapshot'
        self.database.set(collection, {"range_query4": datetime.datetime(2017,1,1).strftime('%Y-%m-%dT%H:%M:%S.%fZ') })
        self.database.set(collection, {"range_query4": datetime.datetime(2017,2,1).strftime('%Y-%m-%dT%H:%M:%S.%fZ') })
        self.database.set(collection, {"range_query4": datetime.datetime(2017,3,1).strftime('%Y-%m-%dT%H:%M:%S.%fZ') })
        # ascending
        items = self.database.query(collection, {"range_query4": {"$gte": datetime.datetime(2017,2,1).strftime('%Y-%m-%dT%H:%M:%S.%fZ') }},
                                    sort_key="range_query4", sort_order='ascending')
        assert items[0]['range_query4'] == datetime.datetime(2017,2,1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        # descending
        items = self.database.query(collection, {
            "range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                    sort_key="range_query4", sort_order='descending')
        assert items[0]['range_query4'] == datetime.datetime(2017, 3, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        # none is passed
        items = self.database.query(collection, {
            "range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                    sort_key="range_query4")
        assert len(items) == 2

        # none is passed
        items = self.database.query(collection, {
            "range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                    sort_order='descending')
        assert len(items) == 2

        failed = False
        try:
            _ = self.database.query(collection, {
                "range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                        sort_key="range_query4", sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        failed = False
        try:
            _ = self.database.query(collection, {
                "range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                    sort_key="wrong_key", sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.database.query(collection, {"range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                             sort_key="range_query4", sort_order='ascending')
        items = self.database.query(collection, {"range_query4": {"$gte": datetime.datetime(2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')}},
                                             sort_key="wrong_key", sort_order='ascending')
        expected_ids = [item['id'] for item in expected_items]
        ids = [item['id'] for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_sort_int(self):
        collection = 'snapshot'
        self.database.set(collection, {"range_query5": 1})
        self.database.set(collection, {"range_query5": 2})
        self.database.set(collection, {"range_query5": 3})

        # ascending
        items = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_key="range_query5", sort_order='ascending')
        assert items[0]['range_query5'] == 2

        # descending
        items = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_key="range_query5",
                                    sort_order='descending')
        assert items[0]['range_query5'] == 3

        # none is passed
        items = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_key="range_query5")
        assert len(items) == 2

        # none is passed
        items = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_order='descending')
        assert len(items) == 2

        failed = False
        try:
            _ = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_key="range_query5",
                                        sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        failed = False
        try:
            _ = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_key="wrong_key",
                                        sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items =self.database.query(collection, {"range_query5": {"$gte": 2}})
        items = self.database.query(collection, {"range_query5": {"$gte": 2}}, sort_key="wrong_key",
                                    sort_order='ascending')
        expected_ids = [item['id'] for item in expected_items]
        ids = [item['id'] for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_sort_bool(self):
        collection = 'snapshot'
        self.database.set(collection, {"range_query6": 1, "bool_query": True})
        self.database.set(collection, {"range_query6": 2, "bool_query": False})
        self.database.set(collection, {"range_query6": 3, "bool_query": True})
        self.database.set(collection, {"range_query6": 4, "bool_query": True})

        # ascending
        items = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_key="bool_query", sort_order='ascending')
        assert items[0]['range_query6'] == 2
        assert items[0]['bool_query'] == False

        # descending
        items = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_key="bool_query",
                                    sort_order='descending')
        assert items[0]['range_query6'] == 3
        assert items[0]['bool_query'] == True

        # none is passed
        items = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_key="bool_query")
        assert len(items) == 3

        # none is passed
        items = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_order='descending')
        assert len(items) == 3

        # wrong order being passed in
        failed = False
        try:
            _ = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_key="range_query6",
                                    sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and order being passed in
        failed = False
        try:
            _ = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_key="wrong_key",
                                    sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items =self.database.query(collection, {"range_query6": {"$gte": 2}})
        items = self.database.query(collection, {"range_query6": {"$gte": 2}}, sort_key="wrong_key",
                                    sort_order='ascending')
        expected_ids = [item['id'] for item in expected_items]
        ids = [item['id'] for item in items]
        assert set(expected_ids) == set(ids)
