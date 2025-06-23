"""
Tests for blitzdb_dal_driver.py
"""

import os
import tempfile
import datetime
import platform

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.util.exceptions import EntityNotFound, InvalidArgumentType, \
    RequiredArgumentMissing
from datmo.core.util.misc_functions import create_unique_hash

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

    def test_db_set_multiple_objs(self):
        test_obj = {"foo": "bar"}
        result = self.database.set(self.collection, test_obj)
        assert result.get('id') != None

        # updating with new key in obj
        test_obj = {"foo": "bar", "foo1": "bar1"}
        result = self.database.set(self.collection, test_obj)
        assert result.get('id') != None

        # removing the previously added key
        test_obj = {"foo2": "bar2"}
        result = self.database.set(self.collection, test_obj)
        assert result.get('id') != None

        # get all entries till now
        items = self.database.query(self.collection, {})
        assert len(items) == 4

    def test_db_get(self):
        test_obj = {"foo": "bar_0"}
        result = self.database.set(self.collection, test_obj)
        result1 = self.database.get(self.collection, result.get('id'))
        assert result1.get('id') == result.get('id')

    def test_db_get_by_shortened_id(self):
        test_obj = {"foo": "bar_1"}
        result = self.database.set(self.collection, test_obj)
        # Test with substring to get with regex
        result2 = self.database.get_by_shortened_id(self.collection,
                                                    result.get('id')[:10])
        assert result2.get('id') == result.get('id')

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
        assert len(results) == 3

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
        assert len(results) == 9
        # ensure each entity returns an 'id'
        for entity in results:
            assert entity['id'] != None

    def test_db_wildcard_query(self):
        random_id = create_unique_hash()
        test_obj = {"random_id": random_id}
        self.database.set(self.collection, test_obj)
        wildcard_query_obj = {"random_id": {"$regex": "%s" % random_id[:10]}}
        results = self.database.query(self.collection, wildcard_query_obj)
        assert len(results) == 1
        assert results[0].get('random_id') == random_id

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
        except Exception:
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
        except Exception:
            failed = True
        assert failed

    def test_query_sort_date_str(self):
        collection = 'snapshot'
        self.database.set(
            collection, {
                "range_query4":
                    datetime.datetime(2017, 1, 1)
                    .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })
        self.database.set(
            collection, {
                "range_query4":
                    datetime.datetime(2017, 2, 1)
                    .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })
        self.database.set(
            collection, {
                "range_query4":
                    datetime.datetime(2017, 3, 1)
                    .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            })
        # ascending
        items = self.database.query(
            collection, {
                "range_query4": {
                    "$gte":
                        datetime.datetime(2017, 2, 1)
                        .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            },
            sort_key="range_query4",
            sort_order='ascending')
        assert items[0]['range_query4'] == datetime.datetime(
            2017, 2, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        # descending
        items = self.database.query(
            collection, {
                "range_query4": {
                    "$gte":
                        datetime.datetime(2017, 2, 1)
                        .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            },
            sort_key="range_query4",
            sort_order='descending')
        assert items[0]['range_query4'] == datetime.datetime(
            2017, 3, 1).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        # only sort_key is passed in with no sort_order
        failed = False
        try:
            _ = self.database.query(
                collection, {
                    "range_query4": {
                        "$gte":
                            datetime.datetime(2017, 2, 1)
                            .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    }
                },
                sort_key="range_query4")
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # only sort_order is passed in with no sort_key
        failed = False
        try:
            _ = self.database.query(
                collection, {
                    "range_query4": {
                        "$gte":
                            datetime.datetime(2017, 2, 1)
                            .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    }
                },
                sort_order='descending')
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # both passed and wrong sort order
        failed = False
        try:
            _ = self.database.query(
                collection, {
                    "range_query4": {
                        "$gte":
                            datetime.datetime(2017, 2, 1)
                            .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    }
                },
                sort_key="range_query4",
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # both passed and both are wrong
        failed = False
        try:
            _ = self.database.query(
                collection, {
                    "range_query4": {
                        "$gte":
                            datetime.datetime(2017, 2, 1)
                            .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    }
                },
                sort_key="wrong_key",
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.database.query(
            collection, {
                "range_query4": {
                    "$gte":
                        datetime.datetime(2017, 2, 1)
                        .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            },
            sort_key="range_query4",
            sort_order='ascending')
        items = self.database.query(
            collection, {
                "range_query4": {
                    "$gte":
                        datetime.datetime(2017, 2, 1)
                        .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            },
            sort_key="wrong_key",
            sort_order='ascending')
        expected_ids = [item['id'] for item in expected_items]
        ids = [item['id'] for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_sort_int(self):
        collection = 'snapshot'
        self.database.set(collection, {"range_query5": 1})
        self.database.set(collection, {"range_query5": 2})
        self.database.set(collection, {"range_query5": 3})

        # ascending
        items = self.database.query(
            collection, {"range_query5": {
                "$gte": 2
            }},
            sort_key="range_query5",
            sort_order='ascending')
        assert items[0]['range_query5'] == 2

        # descending
        items = self.database.query(
            collection, {"range_query5": {
                "$gte": 2
            }},
            sort_key="range_query5",
            sort_order='descending')
        assert items[0]['range_query5'] == 3

        # sort_key passed in but sort_order missing
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query5": {
                    "$gte": 2
                }},
                sort_key="range_query5")
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # sort_order passed in but sort_key missing
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query5": {
                    "$gte": 2
                }},
                sort_order='descending')
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # both passed but wrong sort_order
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query5": {
                    "$gte": 2
                }},
                sort_key="range_query5",
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # both passed and both wrong key and order
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query5": {
                    "$gte": 2
                }},
                sort_key="wrong_key",
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.database.query(collection,
                                             {"range_query5": {
                                                 "$gte": 2
                                             }})
        items = self.database.query(
            collection, {"range_query5": {
                "$gte": 2
            }},
            sort_key="wrong_key",
            sort_order='ascending')
        expected_ids = [item['id'] for item in expected_items]
        ids = [item['id'] for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_sort_bool(self):
        collection = 'snapshot'
        self.database.set(collection, {"range_query6": 1, "current": True})
        self.database.set(collection, {"range_query6": 2, "current": False})
        self.database.set(collection, {"range_query6": 3, "current": True})
        self.database.set(collection, {"range_query6": 4, "current": True})

        # ascending
        items = self.database.query(
            collection, {"range_query6": {
                "$gte": 2
            }},
            sort_key="current",
            sort_order='ascending')
        assert items[0]['range_query6'] == 2
        assert items[0]['current'] == False

        # descending
        items = self.database.query(
            collection, {"range_query6": {
                "$gte": 2
            }},
            sort_key="current",
            sort_order='descending')
        assert items[0]['range_query6'] == 3
        assert items[0]['current'] == True

        # sort_key passed in but sort_order missing
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query6": {
                    "$gte": 2
                }}, sort_key="current")
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # sort_order passed in but sort_key missing
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query6": {
                    "$gte": 2
                }},
                sort_order='descending')
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # wrong order being passed in
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query6": {
                    "$gte": 2
                }},
                sort_key="range_query6",
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and order being passed in
        failed = False
        try:
            _ = self.database.query(
                collection, {"range_query6": {
                    "$gte": 2
                }},
                sort_key="wrong_key",
                sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.database.query(collection,
                                             {"range_query6": {
                                                 "$gte": 2
                                             }})
        items = self.database.query(
            collection, {"range_query6": {
                "$gte": 2
            }},
            sort_key="wrong_key",
            sort_order='ascending')
        expected_ids = [item['id'] for item in expected_items]
        ids = [item['id'] for item in items]
        assert set(expected_ids) == set(ids)

    def test_query_filter_bool(self):
        collection = 'snapshot'

        # Filter False
        items = self.database.query(collection, {"current": False})
        assert len(items) == 1

        # Filter True
        items = self.database.query(collection, {"current": True})
        assert len(items) == 3

    def test_set_update_key_to_same_value(self):
        self.database.set("snapshot", {"id": 1, "key": "hello"})
        self.database.set("snapshot", {"id": 2, "key": "there"})
        items = [
            item for item in self.database.query("snapshot", {"key": "there"})
        ]
        next_item = items[0]

        items = [
            item for item in self.database.query("snapshot", {"key": "hello"})
        ]
        current_item = items[0]
        current_item['key'] = next_item['key']
        self.database.set("snapshot", current_item)

        next_item['key'] = "hello"
        self.database.set("snapshot", next_item)

        items = self.database.query("snapshot", {"key": "hello"})
        assert len(items) == 1
        assert items[0] == next_item
        items = self.database.query("snapshot", {"key": "there"})
        assert len(items) == 1
        assert items[0] == current_item
