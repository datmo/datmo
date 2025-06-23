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
from datmo.core.entity.task import Task
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

        self.task_input_dict = {
            "model_id": model.id,
            "command": "task_1",
            "start_time": datetime.utcnow(),
            "end_time": datetime.utcnow(),
            "duration": 0.004,
        }

    def teardown_method(self):
        pass

    def test_create_task_by_dictionary(self):

        task = self.dal.task.create(Task(self.task_input_dict))

        assert task.id
        assert task.command == self.task_input_dict['command']
        assert isinstance(task.start_time, datetime)
        assert isinstance(task.end_time, datetime)
        assert isinstance(task.duration, float)
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

        # Create a new Task and test if None values work and not same as first
        test_task_input_dict = self.task_input_dict.copy()
        test_task_input_dict['start_time'] = None
        test_task_input_dict['end_time'] = None
        test_task_input_dict['duration'] = None

        task_2 = self.dal.task.create(Task(test_task_input_dict))

        assert task_2.id != task.id
        assert not task_2.start_time
        assert not task_2.end_time
        assert not task_2.duration

        test_task_input_dict_1 = self.task_input_dict.copy()
        test_task_input_dict_1['id'] = "task_id"
        task_3 = self.dal.task.create(Task(test_task_input_dict_1))

        assert task_3.id == test_task_input_dict_1['id']

    def test_get_by_id_task(self):
        task = self.dal.task.create(Task(self.task_input_dict))
        result = self.dal.task.get_by_id(task.id)
        assert task.id == result.id
        assert task.model_id == result.model_id
        assert task.command == result.command
        assert task.start_time == result.start_time
        assert task.end_time == result.end_time
        assert task.duration == result.duration

    def test_get_by_shortened_id_task(self):
        task = self.dal.task.create(Task(self.task_input_dict))
        result = self.dal.task.get_by_shortened_id(task.id[:10])
        assert task.id == result.id
        assert task.model_id == result.model_id
        assert task.command == result.command
        assert task.start_time == result.start_time
        assert task.end_time == result.end_time
        assert task.duration == result.duration

    def test_get_by_id_task_new_driver_instance(self):
        task = self.dal.task.create(Task(self.task_input_dict))

        # create new dal with new driver instance (success)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(
            self.driver_type, self.driver_options, driver=new_driver_instance)
        new_task_1 = new_dal_instance.task.get_by_id(task.id)
        assert new_task_1.id == task.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.driver_type, self.driver_options)
        new_task_2 = new_dal_instance.task.get_by_id(task.id)
        assert new_task_2.id == task.id

    def test_update_task(self):
        task = self.dal.task.create(Task(self.task_input_dict))

        # Update required and optional parameters
        updated_task_input_dict = self.task_input_dict.copy()
        updated_task_input_dict['id'] = task.id
        updated_task_input_dict['command'] = "task_new"
        updated_task_input_dict['ports'] = ["9000:9000"]
        updated_task_input_dict['interactive'] = True
        updated_task = self.dal.task.update(updated_task_input_dict)

        assert task.id == updated_task.id
        assert task.updated_at < updated_task.updated_at
        assert updated_task.command == updated_task_input_dict['command']
        assert updated_task.ports == updated_task_input_dict['ports']
        assert updated_task.interactive == updated_task_input_dict[
            'interactive']

    def test_delete_task(self):
        task = self.dal.task.create(Task(self.task_input_dict))

        self.dal.task.delete(task.id)
        deleted = False
        try:
            self.dal.task.get_by_id(task.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_tasks(self):
        task = self.dal.task.create(Task(self.task_input_dict))

        assert len(self.dal.task.query({"id": task.id})) == 1
        _ = self.dal.task.create(Task(self.task_input_dict))
        assert len(
            self.dal.task.query({
                "command": self.task_input_dict['command']
            })) == 2

    def test_query_tasks_range_query(self):
        _ = self.dal.task.create(Task(self.task_input_dict))
        _ = self.dal.task.create(Task(self.task_input_dict))
        _ = self.dal.task.create(Task(self.task_input_dict))
        tasks = self.dal.task.query(
            {}, sort_key="created_at", sort_order="descending")
        result = self.dal.task.query({
            "created_at": {
                "$lt": tasks[1].created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        })
        assert len(tasks) == 3
        assert len(result) == 1

    def test_query_tasks_range_query_no_task_obj(self):
        _ = self.dal.task.create(self.task_input_dict)
        _ = self.dal.task.create(self.task_input_dict)
        _ = self.dal.task.create(self.task_input_dict)
        tasks = self.dal.task.query(
            {}, sort_key="created_at", sort_order="descending")
        result = self.dal.task.query({
            "created_at": {
                "$lt": tasks[1].created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        })
        assert len(tasks) == 3
        assert len(result) == 1

    def test_sort_tasks(self):
        task_1 = self.dal.task.create(Task(self.task_input_dict))
        task_2 = self.dal.task.create(Task(self.task_input_dict))

        # Sorting of snapshot in descending
        items = self.dal.task.query(
            {
                "model_id": self.task_input_dict["model_id"]
            },
            sort_key="created_at",
            sort_order="descending")
        assert items[0].created_at == task_2.created_at

        # Sorting of snapshot in ascending
        items = self.dal.task.query(
            {
                "model_id": self.task_input_dict["model_id"]
            },
            sort_key="created_at",
            sort_order="ascending")
        assert items[0].created_at == task_1.created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.dal.task.query(
                {
                    "model_id": self.task_input_dict["model_id"]
                },
                sort_key="created_at",
                sort_order="wrong_order")
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.dal.task.query(
                {
                    "model_id": self.task_input_dict["model_id"]
                },
                sort_key="wrong_key",
                sort_order="wrong_order")
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_items = self.dal.task.query(
            {
                "model_id": self.task_input_dict["model_id"]
            },
            sort_key="created_at",
            sort_order="ascending")
        items = self.dal.task.query(
            {
                "model_id": self.task_input_dict["model_id"]
            },
            sort_key="wrong_key",
            sort_order="ascending")
        expected_ids = [item.id for item in expected_items]
        ids = [item.id for item in items]
        assert set(expected_ids) == set(ids)
