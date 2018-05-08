"""
Tests for SnapshotController
"""
import os
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.controller.task import TaskController
from datmo.core.util.exceptions import (
    EntityNotFound, EnvironmentDoesNotExist, GitCommitDoesNotExist,
    SessionDoesNotExistException, RequiredArgumentMissing, TaskNotComplete,
    InvalidArgumentType)


class TestSnapshotController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.task = TaskController(self.temp_dir)
        self.snapshot = SnapshotController(self.temp_dir)

    def teardown_method(self):
        pass

    def test_create_fail_no_message(self):
        # Test no message
        failed = False
        try:
            self.snapshot.create({})
        except RequiredArgumentMissing:
            failed = True
        assert failed

    def test_create_fail_no_code(self):
        # Test default values for snapshot, fail due to code
        failed = False
        try:
            self.snapshot.create({"message": "my test snapshot"})
        except GitCommitDoesNotExist:
            failed = True
        assert failed

    def test_create_fail_no_environment_with_language(self):
        # Test default values for snapshot, fail due to environment with other than default
        self.snapshot.file_driver.create("filepath1")
        failed = False
        try:
            self.snapshot.create({
                "message": "my test snapshot",
                "language": "java"
            })
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

    def test_create_fail_no_environment_detected_in_file(self):
        # Test default values for snapshot, fail due to no environment from file
        self.snapshot.file_driver.create("filepath1")
        failed = False
        try:
            self.snapshot.create({
                "message": "my test snapshot",
            })
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

    def test_create_success_default_detected_in_file(self):
        # Test default values for snapshot when there is no environment
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print('hello')\n"))

        snapshot_obj_1 = self.snapshot.create({"message": "my test snapshot"})

        assert snapshot_obj_1
        assert snapshot_obj_1.code_id
        assert snapshot_obj_1.environment_id
        assert snapshot_obj_1.file_collection_id
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

    def test_create_success_default_env_def(self):
        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Test default values for snapshot, success
        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        assert snapshot_obj
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_create_success_default_env_def_duplicate(self):
        # Test 2 snapshots with same parameters
        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        snapshot_obj_1 = self.snapshot.create({"message": "my test snapshot"})

        # Should return the same object back
        assert snapshot_obj_1 == snapshot_obj
        assert snapshot_obj_1.code_id == snapshot_obj.code_id
        assert snapshot_obj_1.environment_id == \
               snapshot_obj.environment_id
        assert snapshot_obj_1.file_collection_id == \
               snapshot_obj.file_collection_id
        assert snapshot_obj_1.config == \
               snapshot_obj.config
        assert snapshot_obj_1.stats == \
               snapshot_obj.stats

    def test_create_success_given_files_env_def_config_file_stats_file(self):
        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str('{"foo":"bar"}')))

        input_dict = {
            "message":
                "my test snapshot",
            "filepaths": [
                os.path.join(self.snapshot.home, "dirpath1"),
                os.path.join(self.snapshot.home, "dirpath2"),
                os.path.join(self.snapshot.home, "filepath1")
            ],
            "environment_definition_filepath":
                env_def_path,
            "config_filepath":
                config_filepath,
            "stats_filepath":
                stats_filepath,
        }
        # Create snapshot in the project
        snapshot_obj_4 = self.snapshot.create(input_dict)

        assert snapshot_obj_4 != snapshot_obj
        assert snapshot_obj_4.code_id != snapshot_obj.code_id
        assert snapshot_obj_4.environment_id == \
               snapshot_obj.environment_id
        assert snapshot_obj_4.file_collection_id != \
               snapshot_obj.file_collection_id
        assert snapshot_obj_4.config == {"foo": "bar"}
        assert snapshot_obj_4.stats == {"foo": "bar"}

    def test_create_success_given_files_env_def_different_config_stats(self):
        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str('{"foo":"bar"}')))

        # Test different config and stats inputs
        input_dict = {
            "message":
                "my test snapshot",
            "filepaths": [
                os.path.join(self.snapshot.home, "dirpath1"),
                os.path.join(self.snapshot.home, "dirpath2"),
                os.path.join(self.snapshot.home, "filepath1")
            ],
            "environment_definition_filepath":
                env_def_path,
            "config_filename":
                "different_name",
            "stats_filename":
                "different_name",
        }

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot.create(input_dict)

        assert snapshot_obj_1 != snapshot_obj
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

    def test_create_success_given_files_env_def_direct_config_stats(self):
        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Test different config and stats inputs
        input_dict = {
            "message":
                "my test snapshot",
            "filepaths": [
                os.path.join(self.snapshot.home, "dirpath1"),
                os.path.join(self.snapshot.home, "dirpath2"),
                os.path.join(self.snapshot.home, "filepath1")
            ],
            "environment_definition_filepath":
                env_def_path,
            "config": {
                "foo": "bar"
            },
            "stats": {
                "foo": "bar"
            },
        }

        # Create snapshot in the project
        snapshot_obj_6 = self.snapshot.create(input_dict)

        assert snapshot_obj_6.config == {"foo": "bar"}
        assert snapshot_obj_6.stats == {"foo": "bar"}

    def test_create_from_task(self):
        # 1) Test if fails with TaskNotComplete error
        # 2) Test if success with task files, results, and message
        # 3) Test if success with message, label, config and stats
        # 4) Test if success with updated stats from after_snapshot_id and task_results

        # Create task in the project
        task_obj = self.task.create()

        # 1) Test option 1
        failed = False
        try:
            _ = self.snapshot.create_from_task(
                message="my test snapshot", task_id=task_obj.id)
        except TaskNotComplete:
            failed = True
        assert failed

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Test the default values
        updated_task_obj = self.task.run(task_obj.id, task_dict=task_dict)

        # 2) Test option 2
        snapshot_obj = self.snapshot.create_from_task(
            message="my test snapshot", task_id=updated_task_obj.id)

        assert snapshot_obj.id == updated_task_obj.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.stats == updated_task_obj.results
        assert snapshot_obj.visible == True

        # 3) Test option 3
        test_config = {"algo": "regression"}
        test_stats = {"accuracy": 0.9}
        snapshot_obj = self.snapshot.create_from_task(
            message="my test snapshot",
            task_id=updated_task_obj.id,
            label="best",
            config=test_config,
            stats=test_stats)

        assert snapshot_obj.id == updated_task_obj.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.label == "best"
        assert snapshot_obj.config == test_config
        assert snapshot_obj.stats == test_stats
        assert snapshot_obj.visible == True

        # 4) Test option 4
        test_config = {"algo": "regression"}
        test_stats = {"new_key": 0.9}
        task_obj_2 = self.task.create()
        updated_task_obj_2 = self.task.run(
            task_obj_2.id,
            task_dict=task_dict,
            snapshot_dict={
                "config": test_config,
                "stats": test_stats
            })

        snapshot_obj = self.snapshot.create_from_task(
            message="my test snapshot",
            task_id=updated_task_obj_2.id,
            label="best")

        updated_stats_dict = {}
        updated_stats_dict.update(test_stats)
        updated_stats_dict.update(updated_task_obj.results)

        assert snapshot_obj.id == updated_task_obj_2.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.label == "best"
        assert snapshot_obj.stats == updated_stats_dict
        assert snapshot_obj.visible == True

    def __default_create(self):
        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        input_dict = {
            "message":
                "my test snapshot",
            "filepaths": [
                os.path.join(self.snapshot.home, "dirpath1"),
                os.path.join(self.snapshot.home, "dirpath2"),
                os.path.join(self.snapshot.home, "filepath1")
            ],
            "environment_definition_filepath":
                env_def_path,
            "config_filename":
                config_filepath,
            "stats_filename":
                stats_filepath,
        }

        # Create snapshot in the project
        return self.snapshot.create(input_dict)

    def test_checkout(self):
        # Create snapshot
        snapshot_obj_1 = self.__default_create()

        code_obj_1 = self.snapshot.dal.code.get_by_id(snapshot_obj_1.code_id)

        # Create duplicate snapshot in project
        self.snapshot.file_driver.create("test")
        snapshot_obj_2 = self.__default_create()

        assert snapshot_obj_2 != snapshot_obj_1

        # Checkout to snapshot 1 using snapshot id
        result = self.snapshot.checkout(snapshot_obj_1.id)

        # Snapshot directory in user directory
        snapshot_obj_1_path = os.path.join(
            self.snapshot.home, "datmo_snapshots", snapshot_obj_1.id)

        assert result == True and \
               self.snapshot.code_driver.latest_commit() == code_obj_1.commit_id and \
               os.path.isdir(snapshot_obj_1_path)

    def test_list(self):
        # Check for error if incorrect session given
        failed = False
        try:
            self.snapshot.list(session_id="does_not_exist")
        except SessionDoesNotExistException:
            failed = True
        assert failed

        # Create file to add to snapshot
        test_filepath_1 = os.path.join(self.snapshot.home, "test.txt")
        with open(test_filepath_1, "w") as f:
            f.write(to_unicode(str("test")))

        # Create snapshot in the project
        snapshot_obj_1 = self.__default_create()

        # Create file to add to second snapshot
        test_filepath_2 = os.path.join(self.snapshot.home, "test2.txt")
        with open(test_filepath_2, "w") as f:
            f.write(to_unicode(str("test2")))

        # Create second snapshot in the project
        snapshot_obj_2 = self.__default_create()

        # List all snapshots and ensure they exist
        result = self.snapshot.list()

        assert len(result) == 2 and \
            snapshot_obj_1 in result and \
            snapshot_obj_2 in result

        # List all tasks regardless of filters in ascending
        result = self.snapshot.list(
            sort_key='created_at', sort_order='ascending')

        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result
        assert result[0].created_at <= result[-1].created_at

        # List all tasks regardless of filters in descending
        result = self.snapshot.list(
            sort_key='created_at', sort_order='descending')
        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result
        assert result[0].created_at >= result[-1].created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.snapshot.list(
                sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.snapshot.list(
                sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_result = self.snapshot.list(
            sort_key='created_at', sort_order='ascending')
        result = self.snapshot.list(
            sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_result]
        ids = [item.id for item in result]
        assert set(expected_ids) == set(ids)

        # List all snapshots with session filter
        result = self.snapshot.list(session_id=self.project.current_session.id)

        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result

        # List snapshots with visible filter
        result = self.snapshot.list(visible=False)
        assert len(result) == 0

        result = self.snapshot.list(visible=True)
        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result

    def test_delete(self):
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Delete snapshot in the project
        result = self.snapshot.delete(snapshot_obj.id)

        # Check if snapshot retrieval throws error
        thrown = False
        try:
            self.snapshot.dal.snapshot.get_by_id(snapshot_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True
