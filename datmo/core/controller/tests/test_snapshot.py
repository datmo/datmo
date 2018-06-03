"""
Tests for SnapshotController
"""
import os
import tempfile
import platform
from io import open, TextIOWrapper
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.controller.project import ProjectController
from datmo.core.controller.task import TaskController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.snapshot import Snapshot
from datmo.core.util.exceptions import (
    EntityNotFound, CommitFailed, SessionDoesNotExist, RequiredArgumentMissing,
    TaskNotComplete, InvalidArgumentType, ProjectNotInitialized,
    InvalidProjectPath, DoesNotExist)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestSnapshotController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_method(self):
        pass

    def __setup(self):
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.task = TaskController(self.temp_dir)
        self.snapshot = SnapshotController(self.temp_dir)

    def test_init_fail_project_not_init(self):
        failed = False
        try:
            SnapshotController(self.temp_dir)
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_init_fail_invalid_path(self):
        test_home = "some_random_dir"
        failed = False
        try:
            SnapshotController(test_home)
        except InvalidProjectPath:
            failed = True
        assert failed

    def test_create_fail_no_message(self):
        self.__setup()
        # Test no message
        failed = False
        try:
            self.snapshot.create({})
        except RequiredArgumentMissing:
            failed = True
        assert failed

    def test_create_fail_no_code(self):
        self.__setup()
        # Test default values for snapshot, fail due to code
        failed = False
        try:
            self.snapshot.create({"message": "my test snapshot"})
        except CommitFailed:
            failed = True
        assert failed

    def test_create_fail_no_code_environment(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # test must fail when there is file present in root project folder
        failed = False
        try:
            _ = self.snapshot.create({"message": "my test snapshot"})
        except CommitFailed:
            failed = True
        assert failed

    def test_create_fail_no_code_environment_files(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        test_file = os.path.join(self.project.files_directory, "test.txt")
        with open(test_file, "wb") as f:
            f.write(to_bytes(str("hello")))

        # test must fail when there is file present in root project folder
        failed = False
        try:
            _ = self.snapshot.create({"message": "my test snapshot"})
        except CommitFailed:
            failed = True
        assert failed

    def test_create_no_environment_detected_in_file(self):
        self.__setup()

        # Test default values for snapshot, fail due to no environment from file
        self.snapshot.file_driver.create("filepath1")
        snapshot_obj_0 = self.snapshot.create({"message": "my test snapshot"})
        assert isinstance(snapshot_obj_0, Snapshot)
        assert snapshot_obj_0.code_id
        assert snapshot_obj_0.environment_id
        assert snapshot_obj_0.file_collection_id
        assert snapshot_obj_0.config == {}
        assert snapshot_obj_0.stats == {}

    def test_create_success_default_detected_in_file(self):
        self.__setup()
        # Test default values for snapshot when there is no environment
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("import sys\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj_1 = self.snapshot.create({"message": "my test snapshot"})

        assert isinstance(snapshot_obj_1, Snapshot)
        assert snapshot_obj_1.code_id
        assert snapshot_obj_1.environment_id
        assert snapshot_obj_1.file_collection_id
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

    def test_create_success_default_env_def(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # Test default values for snapshot, success
        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_create_success_with_datmo_environment(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # creating a file in project folder
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # Test default values for snapshot, success
        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_create_success_env_definition_paths(self):
        self.__setup()
        # Create environment definition
        random_dir = os.path.join(self.snapshot.home, "random_dir")
        os.makedirs(random_dir)
        env_def_path = os.path.join(random_dir, "randomDockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))
        environment_definition_paths = [env_def_path + ">Dockerfile"]
        # Test default values for snapshot, success
        snapshot_obj = self.snapshot.create({
            "message": "my test snapshot",
            "environment_definition_paths": environment_definition_paths
        })

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_create_success_default_env_def_duplicate(self):
        self.__setup()
        # Test 2 snapshots with same parameters
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        snapshot_obj_1 = self.snapshot.create({"message": "my test snapshot"})

        # Should return the same object back
        assert snapshot_obj_1.id == snapshot_obj.id
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
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        # Create files to add
        _, project_directory_name = os.path.split(self.project.files_directory)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath1"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath2"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "filepath1"))

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        input_dict = {
            "message": "my test snapshot",
            "config_filepath": config_filepath,
            "stats_filepath": stats_filepath,
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
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj = self.snapshot.create({"message": "my test snapshot"})

        # Create files to add
        _, project_directory_name = os.path.split(self.project.files_directory)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath1"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath2"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "filepath1"))

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        # Test different config and stats inputs
        input_dict = {
            "message": "my test snapshot",
            "config_filename": "different_name",
            "stats_filename": "different_name",
        }

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot.create(input_dict)

        assert snapshot_obj_1 != snapshot_obj
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

    def test_create_success_given_files_env_def_direct_config_stats(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Create files to add
        _, project_directory_name = os.path.split(self.project.files_directory)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath1"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath2"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "filepath1"))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # Test different config and stats inputs
        input_dict = {
            "message": "my test snapshot",
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

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_create_from_task(self):
        self.__setup()
        # 0) Test if fails with TaskNotComplete error
        # 1) Test if success with empty task files, results
        # 2) Test if success with task files, results, and message
        # 3) Test if success with message, label, config and stats
        # 4) Test if success with updated stats from after_snapshot_id and task_results

        # Create task in the project
        task_obj = self.task.create()

        # 0) Test option 0
        failed = False
        try:
            _ = self.snapshot.create_from_task(
                message="my test snapshot", task_id=task_obj.id)
        except TaskNotComplete:
            failed = True
        assert failed

        # 1) Test option 1

        # Create task_dict
        task_command = ["sh", "-c", "echo test"]
        task_dict = {"command_list": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        updated_task_obj = self.task.run(task_obj.id, task_dict=task_dict)

        snapshot_obj = self.snapshot.create_from_task(
            message="my test snapshot", task_id=updated_task_obj.id)

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.id == updated_task_obj.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.stats == updated_task_obj.results
        assert snapshot_obj.visible == True

        # Create new task and corresponding dict
        task_obj = self.task.create()
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command_list": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Test the default values
        updated_task_obj = self.task.run(task_obj.id, task_dict=task_dict)

        # 2) Test option 2
        snapshot_obj = self.snapshot.create_from_task(
            message="my test snapshot", task_id=updated_task_obj.id)

        assert isinstance(snapshot_obj, Snapshot)
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

        assert isinstance(snapshot_obj, Snapshot)
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

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.id == updated_task_obj_2.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.label == "best"
        assert snapshot_obj.stats == updated_stats_dict
        assert snapshot_obj.visible == True

    def __default_create(self):
        # Create files to add
        _, project_directory_name = os.path.split(self.project.files_directory)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath1"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "dirpath2"), directory=True)
        self.snapshot.file_driver.create(
            os.path.join(project_directory_name, "filepath1"))
        self.snapshot.file_driver.create("filepath2")
        with open(os.path.join(self.snapshot.home, "filepath2"), "wb") as f:
            f.write(to_bytes(str("import sys\n")))
        # Create environment_driver definition
        env_def_path = os.path.join(self.project.environment_directory,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        input_dict = {
            "message": "my test snapshot",
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
        }

        # Create snapshot in the project
        return self.snapshot.create(input_dict)

    def test_checkout(self):
        self.__setup()
        # Create snapshot
        snapshot_obj_1 = self.__default_create()

        # Create duplicate snapshot in project
        self.snapshot.file_driver.create("test")
        snapshot_obj_2 = self.__default_create()

        assert snapshot_obj_2 != snapshot_obj_1

        # Checkout to snapshot 1 using snapshot id
        result = self.snapshot.checkout(snapshot_obj_1.id)
        # TODO: Check for which snapshot we are on

        assert result == True

    def test_list(self):
        self.__setup()
        # Check for error if incorrect session given
        failed = False
        try:
            self.snapshot.list(session_id="does_not_exist")
        except SessionDoesNotExist:
            failed = True
        assert failed

        # Create file to add to snapshot
        test_filepath_1 = os.path.join(self.snapshot.home, "test.txt")
        with open(test_filepath_1, "wb") as f:
            f.write(to_bytes(str("test")))

        # Create snapshot in the project
        snapshot_obj_1 = self.__default_create()

        # Create file to add to second snapshot
        test_filepath_2 = os.path.join(self.snapshot.home, "test2.txt")
        with open(test_filepath_2, "wb") as f:
            f.write(to_bytes(str("test2")))

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

    def test_update(self):
        self.__setup()
        test_config = {"config_foo": "bar"}
        test_stats = {"stats_foo": "bar"}
        test_message = 'test_message'
        test_label = 'test_label'

        # Updating all config, stats, message and label
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Update snapshot in the project
        self.snapshot.update(
            snapshot_obj.id,
            config=test_config,
            stats=test_stats,
            message=test_message,
            label=test_label)

        # Get the updated snapshot obj
        updated_snapshot_obj = self.snapshot.dal.snapshot.get_by_id(
            snapshot_obj.id)
        assert updated_snapshot_obj.config == test_config
        assert updated_snapshot_obj.stats == test_stats
        assert updated_snapshot_obj.message == test_message
        assert updated_snapshot_obj.label == test_label

        # Updating config, stats
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Update snapshot in the project
        self.snapshot.update(
            snapshot_obj.id, config=test_config, stats=test_stats)

        # Get the updated snapshot obj
        updated_snapshot_obj = self.snapshot.dal.snapshot.get_by_id(
            snapshot_obj.id)
        assert updated_snapshot_obj.config == test_config
        assert updated_snapshot_obj.stats == test_stats

        # Updating both message and label
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Update snapshot in the project
        self.snapshot.update(
            snapshot_obj.id, message=test_message, label=test_label)

        # Get the updated snapshot obj
        updated_snapshot_obj = self.snapshot.dal.snapshot.get_by_id(
            snapshot_obj.id)

        assert updated_snapshot_obj.message == test_message
        assert updated_snapshot_obj.label == test_label

        # Updating only message
        # Create snapshot in the project
        snapshot_obj_1 = self.__default_create()

        # Update snapshot in the project
        self.snapshot.update(snapshot_obj_1.id, message=test_message)

        # Get the updated snapshot obj
        updated_snapshot_obj_1 = self.snapshot.dal.snapshot.get_by_id(
            snapshot_obj_1.id)

        assert updated_snapshot_obj_1.message == test_message

        # Updating only label
        # Create snapshot in the project
        snapshot_obj_2 = self.__default_create()

        # Update snapshot in the project
        self.snapshot.update(snapshot_obj_2.id, label=test_label)

        # Get the updated snapshot obj
        updated_snapshot_obj_2 = self.snapshot.dal.snapshot.get_by_id(
            snapshot_obj_2.id)

        assert updated_snapshot_obj_2.label == test_label

    def test_get(self):
        self.__setup()
        # Test failure for no snapshot
        failed = False
        try:
            self.snapshot.get("random")
        except DoesNotExist:
            failed = True
        assert failed

        # Test success for snapshot
        snapshot_obj = self.__default_create()
        snapshot_obj_returned = self.snapshot.get(snapshot_obj.id)
        assert snapshot_obj == snapshot_obj_returned

    def test_get_files(self):
        self.__setup()
        # Test failure case
        failed = False
        try:
            self.snapshot.get_files("random")
        except DoesNotExist:
            failed = True
        assert failed

        # Test success case
        snapshot_obj = self.__default_create()
        result = self.snapshot.get_files(snapshot_obj.id)
        file_collection_obj = self.task.dal.file_collection.get_by_id(
            snapshot_obj.file_collection_id)

        file_names = [item.name for item in result]

        assert len(result) == 1
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "r"
        assert os.path.join(self.task.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

        result = self.snapshot.get_files(snapshot_obj.id, mode="a")

        assert len(result) == 1
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "a"
        assert os.path.join(self.task.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

    def test_delete(self):
        self.__setup()
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
