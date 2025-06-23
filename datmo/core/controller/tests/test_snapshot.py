"""
Tests for SnapshotController
"""
import os
import tempfile
import platform
from io import open, TextIOWrapper
try:
    to_unicode = str
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

from datmo.config import Config
from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.task import TaskController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.snapshot import Snapshot
from datmo.core.util.exceptions import (
    EntityNotFound, RequiredArgumentMissing, TaskNotComplete,
    InvalidArgumentType, ProjectNotInitialized, InvalidProjectPath,
    DoesNotExist, UnstagedChanges)
from datmo.core.util.misc_functions import check_docker_inactive, pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestSnapshotController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.environment_ids = []

    def teardown_method(self):
        if not check_docker_inactive(test_datmo_dir,
                                     Config().datmo_directory_name):
            self.__setup()
            self.environment_controller = EnvironmentController()
            for env_id in list(set(self.environment_ids)):
                if not self.environment_controller.delete(env_id):
                    raise Exception

    def __setup(self):
        Config().set_home(self.temp_dir)
        self.project_controller = ProjectController()
        self.project_controller.init("test", "test description")
        self.task_controller = TaskController()
        self.snapshot_controller = SnapshotController()

    def test_init_fail_project_not_init(self):
        Config().set_home(self.temp_dir)
        failed = False
        try:
            SnapshotController()
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_init_fail_invalid_path(self):
        test_home = "some_random_dir"
        Config().set_home(test_home)
        failed = False
        try:
            SnapshotController()
        except InvalidProjectPath:
            failed = True
        assert failed

    def test_current_snapshot(self):
        self.__setup()
        # Test failure for unstaged changes
        failed = False
        try:
            self.snapshot_controller.current_snapshot()
        except UnstagedChanges:
            failed = True
        assert failed
        # Test success after snapshot created
        snapshot_obj = self.__default_create()
        current_snapshot_obj = self.snapshot_controller.current_snapshot()
        assert current_snapshot_obj == snapshot_obj

    def test_create_fail_no_message(self):
        self.__setup()
        # Test no message
        failed = False
        try:
            self.snapshot_controller.create({})
        except RequiredArgumentMissing:
            failed = True
        assert failed

    def test_create_success_no_code(self):
        self.__setup()
        # Test default values for snapshot, fail due to code
        result = self.snapshot_controller.create({
            "message": "my test snapshot"
        })
        assert result

    def test_create_success_no_code_environment(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # test must pass when there is file present in root project folder
        result = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        assert result

    def test_create_success_no_code_environment_files(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        test_file = os.path.join(
            self.project_controller.file_driver.files_directory, "test.txt")
        with open(test_file, "wb") as f:
            f.write(to_bytes(str("hello")))

        # test must pass when there is file present in root project folder
        result = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        assert result

    def test_create_no_environment_detected_in_file(self):
        self.__setup()

        # Test default values for snapshot, fail due to no environment from file
        self.snapshot_controller.file_driver.create("filepath1")
        snapshot_obj_0 = self.snapshot_controller.create({
            "message": "my test snapshot"
        })
        assert isinstance(snapshot_obj_0, Snapshot)
        assert snapshot_obj_0.code_id
        assert snapshot_obj_0.environment_id
        assert snapshot_obj_0.file_collection_id
        assert snapshot_obj_0.config == {}
        assert snapshot_obj_0.stats == {}

    def test_create_success_default_detected_in_file(self):
        self.__setup()
        # Test default values for snapshot when there is no environment
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("import sys\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj_1 = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        assert isinstance(snapshot_obj_1, Snapshot)
        assert snapshot_obj_1.code_id
        assert snapshot_obj_1.environment_id
        assert snapshot_obj_1.file_collection_id
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

    def test_create_success_default_env_def(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # Test default values for snapshot, success
        snapshot_obj = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_create_success_with_environment(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # creating a file in project folder
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # Test default values for snapshot, success
        snapshot_obj = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_create_success_env_paths(self):
        self.__setup()
        # Create environment definition
        random_dir = os.path.join(self.snapshot_controller.home, "random_dir")
        os.makedirs(random_dir)
        env_def_path = os.path.join(random_dir, "randomDockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))
        environment_paths = [env_def_path + ">Dockerfile"]

        # Test default values for snapshot, success
        snapshot_obj = self.snapshot_controller.create({
            "message": "my test snapshot",
            "environment_paths": environment_paths
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
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        snapshot_obj_1 = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

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
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        # Create files to add
        _, files_directory_name = os.path.split(
            self.project_controller.file_driver.files_directory)
        files_directory_relative_path = os.path.join(
            self.project_controller.file_driver.datmo_directory_name,
            files_directory_name)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath1"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath2"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "filepath1"))

        # Create config
        config_filepath = os.path.join(self.snapshot_controller.home,
                                       "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot_controller.home,
                                      "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        input_dict = {
            "message": "my test snapshot",
            "config_filepath": config_filepath,
            "stats_filepath": stats_filepath,
        }
        # Create snapshot in the project
        snapshot_obj_4 = self.snapshot_controller.create(input_dict)

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
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        snapshot_obj = self.snapshot_controller.create({
            "message": "my test snapshot"
        })

        # Create files to add
        _, files_directory_name = os.path.split(
            self.project_controller.file_driver.files_directory)
        files_directory_relative_path = os.path.join(
            self.project_controller.file_driver.datmo_directory_name,
            files_directory_name)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath1"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath2"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "filepath1"))

        # Create config
        config_filepath = os.path.join(self.snapshot_controller.home,
                                       "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot_controller.home,
                                      "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":"bar"}')))

        # Test different config and stats inputs
        input_dict = {
            "message": "my test snapshot",
            "config_filename": "different_name",
            "stats_filename": "different_name",
        }

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot_controller.create(input_dict)

        assert snapshot_obj_1 != snapshot_obj
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

    def test_create_success_given_files_env_def_direct_config_stats(self):
        self.__setup()
        # Create environment definition
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create files to add
        _, files_directory_name = os.path.split(
            self.project_controller.file_driver.files_directory)
        files_directory_relative_path = os.path.join(
            self.project_controller.file_driver.datmo_directory_name,
            files_directory_name)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath1"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath2"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "filepath1"))

        # Creating a file in project folder
        test_filepath = os.path.join(self.snapshot_controller.home,
                                     "script.py")
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
        snapshot_obj_6 = self.snapshot_controller.create(input_dict)

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
        task_obj = self.task_controller.create()

        # 0) Test option 0
        failed = False
        try:
            _ = self.snapshot_controller.create_from_task(
                message="my test snapshot", task_id=task_obj.id)
        except TaskNotComplete:
            failed = True
        assert failed

        # 1) Test option 1

        # Create task_dict
        task_command = ["sh", "-c", "echo test"]
        task_dict = {"command_list": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        updated_task_obj = self.task_controller.run(
            task_obj.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

        snapshot_obj = self.snapshot_controller.create_from_task(
            message="my test snapshot", task_id=updated_task_obj.id)

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.id == updated_task_obj.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.stats == updated_task_obj.results
        assert snapshot_obj.visible == True

        # Create new task and corresponding dict
        task_obj = self.task_controller.create()
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command_list": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Test the default values
        updated_task_obj = self.task_controller.run(
            task_obj.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

        # 2) Test option 2
        snapshot_obj = self.snapshot_controller.create_from_task(
            message="my test snapshot", task_id=updated_task_obj.id)

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.id == updated_task_obj.after_snapshot_id
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.stats == updated_task_obj.results
        assert snapshot_obj.visible == True

        # 3) Test option 3
        test_config = {"algo": "regression"}
        test_stats = {"accuracy": 0.9}
        snapshot_obj = self.snapshot_controller.create_from_task(
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
        task_obj_2 = self.task_controller.create()
        updated_task_obj_2 = self.task_controller.run(
            task_obj_2.id,
            task_dict=task_dict,
            snapshot_dict={
                "config": test_config,
                "stats": test_stats
            })
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_2.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

        snapshot_obj = self.snapshot_controller.create_from_task(
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
        _, files_directory_name = os.path.split(
            self.project_controller.file_driver.files_directory)
        files_directory_relative_path = os.path.join(
            self.project_controller.file_driver.datmo_directory_name,
            files_directory_name)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath1"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "dirpath2"),
            directory=True)
        self.snapshot_controller.file_driver.create(
            os.path.join(files_directory_relative_path, "filepath1"))
        self.snapshot_controller.file_driver.create("filepath2")
        with open(
                os.path.join(self.snapshot_controller.home, "filepath2"),
                "wb") as f:
            f.write(to_bytes(str("import sys\n")))
        # Create environment_driver definition
        env_def_path = os.path.join(self.project_controller.environment_driver.
                                    environment_directory_path, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create config
        config_filepath = os.path.join(self.snapshot_controller.home,
                                       "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot_controller.home,
                                      "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        input_dict = {
            "message": "my test snapshot",
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
        }

        # Create snapshot in the project
        return self.snapshot_controller.create(input_dict)

    def test_check_unstaged_changes(self):
        self.__setup()
        # Check unstaged changes
        failed = False
        try:
            self.snapshot_controller.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed
        # Check no unstaged changes
        _ = self.__default_create()
        result = self.snapshot_controller.check_unstaged_changes()
        assert result == False

    def test_checkout(self):
        self.__setup()
        # Create snapshot
        snapshot_obj_1 = self.__default_create()

        # Create duplicate snapshot in project
        self.snapshot_controller.file_driver.create("test")
        snapshot_obj_2 = self.__default_create()

        assert snapshot_obj_2 != snapshot_obj_1

        # Checkout to snapshot 1 using snapshot id
        result = self.snapshot_controller.checkout(snapshot_obj_1.id)
        # TODO: Check for which snapshot we are on

        assert result == True

    def test_list(self):
        self.__setup()
        # Create file to add to snapshot
        test_filepath_1 = os.path.join(self.snapshot_controller.home,
                                       "test.txt")
        with open(test_filepath_1, "wb") as f:
            f.write(to_bytes(str("test")))

        # Create snapshot in the project
        snapshot_obj_1 = self.__default_create()

        # Create file to add to second snapshot
        test_filepath_2 = os.path.join(self.snapshot_controller.home,
                                       "test2.txt")
        with open(test_filepath_2, "wb") as f:
            f.write(to_bytes(str("test2")))

        # Create second snapshot in the project
        snapshot_obj_2 = self.__default_create()

        # List all snapshots and ensure they exist
        result = self.snapshot_controller.list()

        assert len(result) == 2 and \
            snapshot_obj_1 in result and \
            snapshot_obj_2 in result

        # List all tasks regardless of filters in ascending
        result = self.snapshot_controller.list(
            sort_key='created_at', sort_order='ascending')

        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result
        assert result[0].created_at <= result[-1].created_at

        # List all tasks regardless of filters in descending
        result = self.snapshot_controller.list(
            sort_key='created_at', sort_order='descending')
        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result
        assert result[0].created_at >= result[-1].created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.snapshot_controller.list(
                sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.snapshot_controller.list(
                sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_result = self.snapshot_controller.list(
            sort_key='created_at', sort_order='ascending')
        result = self.snapshot_controller.list(
            sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_result]
        ids = [item.id for item in result]
        assert set(expected_ids) == set(ids)

        # List snapshots with visible filter
        result = self.snapshot_controller.list(visible=False)
        assert len(result) == 0

        result = self.snapshot_controller.list(visible=True)
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
        self.snapshot_controller.update(
            snapshot_obj.id,
            config=test_config,
            stats=test_stats,
            message=test_message,
            label=test_label)

        # Get the updated snapshot obj
        updated_snapshot_obj = self.snapshot_controller.dal.snapshot.get_by_id(
            snapshot_obj.id)
        assert updated_snapshot_obj.config == test_config
        assert updated_snapshot_obj.stats == test_stats
        assert updated_snapshot_obj.message == test_message
        assert updated_snapshot_obj.label == test_label

        # Updating config, stats
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Update snapshot in the project
        self.snapshot_controller.update(
            snapshot_obj.id, config=test_config, stats=test_stats)

        # Get the updated snapshot obj
        updated_snapshot_obj = self.snapshot_controller.dal.snapshot.get_by_id(
            snapshot_obj.id)
        assert updated_snapshot_obj.config == test_config
        assert updated_snapshot_obj.stats == test_stats

        # Updating both message and label
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Update snapshot in the project
        self.snapshot_controller.update(
            snapshot_obj.id, message=test_message, label=test_label)

        # Get the updated snapshot obj
        updated_snapshot_obj = self.snapshot_controller.dal.snapshot.get_by_id(
            snapshot_obj.id)

        assert updated_snapshot_obj.message == test_message
        assert updated_snapshot_obj.label == test_label

        # Updating only message
        # Create snapshot in the project
        snapshot_obj_1 = self.__default_create()

        # Update snapshot in the project
        self.snapshot_controller.update(
            snapshot_obj_1.id, message=test_message)

        # Get the updated snapshot obj
        updated_snapshot_obj_1 = self.snapshot_controller.dal.snapshot.get_by_id(
            snapshot_obj_1.id)

        assert updated_snapshot_obj_1.message == test_message

        # Updating only label
        # Create snapshot in the project
        snapshot_obj_2 = self.__default_create()

        # Update snapshot in the project
        self.snapshot_controller.update(snapshot_obj_2.id, label=test_label)

        # Get the updated snapshot obj
        updated_snapshot_obj_2 = self.snapshot_controller.dal.snapshot.get_by_id(
            snapshot_obj_2.id)

        assert updated_snapshot_obj_2.label == test_label

    def test_get(self):
        self.__setup()
        # Test failure for no snapshot
        failed = False
        try:
            self.snapshot_controller.get("random")
        except DoesNotExist:
            failed = True
        assert failed

        # Test success for snapshot
        snapshot_obj = self.__default_create()
        snapshot_obj_returned = self.snapshot_controller.get(snapshot_obj.id)
        assert snapshot_obj == snapshot_obj_returned

    def test_get_files(self):
        self.__setup()
        # Test failure case
        failed = False
        try:
            self.snapshot_controller.get_files("random")
        except DoesNotExist:
            failed = True
        assert failed

        # Test success case
        snapshot_obj = self.__default_create()
        result = self.snapshot_controller.get_files(snapshot_obj.id)
        file_collection_obj = self.task_controller.dal.file_collection.get_by_id(
            snapshot_obj.file_collection_id)

        file_names = [item.name for item in result]

        assert len(result) == 1
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "r"
        assert os.path.join(self.task_controller.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

        result = self.snapshot_controller.get_files(snapshot_obj.id, mode="a")

        assert len(result) == 1
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "a"
        assert os.path.join(self.task_controller.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

    def test_delete(self):
        self.__setup()
        # Create snapshot in the project
        snapshot_obj = self.__default_create()

        # Delete snapshot in the project
        result = self.snapshot_controller.delete(snapshot_obj.id)

        # Check if snapshot retrieval throws error
        thrown = False
        try:
            self.snapshot_controller.dal.snapshot.get_by_id(snapshot_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True
