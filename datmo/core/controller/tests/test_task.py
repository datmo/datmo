"""
Tests for TaskController
"""
import os
import time
import random
import string
import tempfile
import platform
import timeout_decorator
from io import open, TextIOWrapper
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.task import TaskController
from datmo.core.entity.task import Task
from datmo.core.util.exceptions import EntityNotFound, TaskRunError, \
    InvalidArgumentType, RequiredArgumentMissing, ProjectNotInitialized, \
    InvalidProjectPath, TooManyArgumentsFound
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestTaskController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_method(self):
        pass

    def __setup(self):
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.environment = EnvironmentController(self.temp_dir)
        self.task = TaskController(self.temp_dir)

    def test_init_fail_project_not_init(self):
        failed = False
        try:
            TaskController(self.temp_dir)
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_init_fail_invalid_path(self):
        test_home = "some_random_dir"
        failed = False
        try:
            TaskController(test_home)
        except InvalidProjectPath:
            failed = True
        assert failed

    def test_create(self):
        self.__setup()
        # Create task in the project
        task_obj = self.task.create()

        assert isinstance(task_obj, Task)
        assert task_obj.created_at
        assert task_obj.updated_at

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_helper(self):
        self.__setup()
        # TODO: Try out more options (see below)
        # Create environment_driver id
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        environment_obj = self.environment.create({
            "definition_filepath": env_def_path
        })

        # Set log filepath
        log_filepath = os.path.join(self.task.home, "test.log")

        # create volume to mount
        temp_test_dirpath = os.path.join(self.temp_dir, "temp")
        os.makedirs(temp_test_dirpath)

        # Test option set 1
        random_name = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(32)
        ])
        options_dict = {
            "command": ["sh", "-c", "echo accuracy:0.45"],
            "ports": ["8888:8888"],
            "name": random_name,
            "volumes": {
                temp_test_dirpath: {
                    'bind': '/task/',
                    'mode': 'rw'
                }
            },
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False,
            "interactive": False
        }

        return_code, run_id, logs = \
            self.task._run_helper(environment_obj.id,
                                  options_dict, log_filepath)
        assert return_code == 0
        assert run_id and \
               self.task.environment_driver.get_container(run_id)
        assert logs and \
               os.path.exists(log_filepath)
        self.task.environment_driver.stop_remove_containers_by_term(
            term=random_name)

        # Test option set 2
        random_name_2 = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(32)
        ])
        options_dict = {
            "command": ["sh", "-c", "echo accuracy:0.45"],
            "ports": ["8888:8888"],
            "name": random_name_2,
            "volumes": {
                temp_test_dirpath: {
                    'bind': '/task/',
                    'mode': 'rw'
                }
            },
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": True,
            "interactive": False
        }

        return_code, run_id, logs = \
            self.task._run_helper(environment_obj.id,
                                  options_dict, log_filepath)
        assert return_code == 0
        assert run_id and \
               self.task.environment_driver.get_container(run_id)
        assert logs and \
               os.path.exists(log_filepath)
        self.task.environment_driver.stop_remove_containers_by_term(
            term=random_name_2)

    def test_parse_logs_for_results(self):
        self.__setup()
        test_logs = """
        this is a log
        accuracy is good
        accuracy : 0.94
        this did not work
        validation : 0.32
        model_type : logistic regression
        """
        result = self.task._parse_logs_for_results(test_logs)

        assert isinstance(result, dict)
        assert result['accuracy'] == "0.94"
        assert result['validation'] == "0.32"
        assert result['model_type'] == "logistic regression"

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        self.__setup()
        # 0) Test failure case without command and without interactive
        # 1) Test success case with default values and env def file
        # 2) Test failure case if running same task (conflicting containers)
        # 3) Test failure case if running same task with snapshot_dict (conflicting containers)
        # 4) Test success case with snapshot_dict
        # 5) Test success case with saved file during task run

        # TODO: look into log filepath randomness, sometimes logs are not written

        # Create task in the project
        task_obj = self.task.create()

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # 0) Test option 0
        failed = False
        try:
            self.task.run(task_obj.id)
        except RequiredArgumentMissing:
            failed = True
        assert failed

        failed = False
        try:
            self.task.run(
                task_obj.id,
                task_dict={
                    "command": None,
                    "interactive": False,
                    "ports": None
                })
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command": task_command}

        # 1) Test option 1
        updated_task_obj = self.task.run(task_obj.id, task_dict=task_dict)

        assert isinstance(updated_task_obj, Task)
        assert task_obj.id == updated_task_obj.id

        assert updated_task_obj.before_snapshot_id
        assert updated_task_obj.ports == None
        assert updated_task_obj.interactive == False
        assert updated_task_obj.task_dirpath
        assert updated_task_obj.log_filepath
        assert updated_task_obj.start_time

        assert updated_task_obj.after_snapshot_id
        assert updated_task_obj.run_id
        assert updated_task_obj.logs
        assert "accuracy" in updated_task_obj.logs
        assert updated_task_obj.results
        assert updated_task_obj.results == {"accuracy": "0.45"}
        assert updated_task_obj.status == "SUCCESS"
        assert updated_task_obj.end_time
        assert updated_task_obj.duration

        self.task.stop(task_obj.id)

        # 2) Test option 2
        failed = False
        try:
            self.task.run(task_obj.id)
        except TaskRunError:
            failed = True
        assert failed

        # 3) Test option 3

        # Create files to add
        self.project.file_driver.create("dirpath1", directory=True)
        self.project.file_driver.create("dirpath2", directory=True)
        self.project.file_driver.create("filepath1")

        # Snapshot dictionary
        snapshot_dict = {
            "filepaths": [
                os.path.join(self.project.home, "dirpath1"),
                os.path.join(self.project.home, "dirpath2"),
                os.path.join(self.project.home, "filepath1")
            ],
        }

        # Run a basic task in the project
        failed = False
        try:
            self.task.run(task_obj.id, snapshot_dict=snapshot_dict)
        except TaskRunError:
            failed = True
        assert failed

        # Test when the specific task id is already RUNNING
        # Create task in the project
        task_obj_1 = self.task.create()
        self.task.dal.task.update({"id": task_obj_1.id, "status": "RUNNING"})
        # Create environment_driver definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        failed = False
        try:
            self.task.run(task_obj_1.id, task_dict=task_dict)
        except TaskRunError:
            failed = True
        assert failed

        # 4) Test option 4

        # Create a new task in the project
        task_obj_2 = self.task.create()

        # Run another task in the project
        updated_task_obj_2 = self.task.run(
            task_obj_2.id, task_dict=task_dict, snapshot_dict=snapshot_dict)

        assert isinstance(updated_task_obj_2, Task)
        assert task_obj_2.id == updated_task_obj_2.id

        assert updated_task_obj_2.before_snapshot_id
        assert updated_task_obj_2.ports == None
        assert updated_task_obj_2.interactive == False
        assert updated_task_obj_2.task_dirpath
        assert updated_task_obj_2.log_filepath
        assert updated_task_obj_2.start_time

        assert updated_task_obj_2.after_snapshot_id
        assert updated_task_obj_2.run_id
        assert updated_task_obj_2.logs
        assert "accuracy" in updated_task_obj_2.logs
        assert updated_task_obj_2.results
        assert updated_task_obj_2.results == {"accuracy": "0.45"}
        assert updated_task_obj_2.status == "SUCCESS"
        assert updated_task_obj_2.end_time
        assert updated_task_obj_2.duration

        self.task.stop(task_obj_2.id)

        # 5) Test option 5

        # Create a basic script
        # (fails w/ no environment)
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import os\n"))
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print('hello')\n"))
            f.write(to_unicode("print(' accuracy: 0.56 ')\n"))
            f.write(
                to_unicode(
                    "with open(os.path.join('/task', 'new_file.txt'), 'a') as f:\n"
                ))
            f.write(to_unicode("    f.write('my test file')\n"))

        # Create task in the project
        task_obj_2 = self.task.create()

        # Create task_dict
        task_command = ["python", "script.py"]
        task_dict = {"command": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        updated_task_obj_2 = self.task.run(task_obj_2.id, task_dict=task_dict)

        assert isinstance(updated_task_obj_2, Task)
        assert updated_task_obj_2.before_snapshot_id
        assert updated_task_obj_2.ports == None
        assert updated_task_obj_2.interactive == False
        assert updated_task_obj_2.task_dirpath
        assert updated_task_obj_2.log_filepath
        assert updated_task_obj_2.start_time

        assert updated_task_obj_2.after_snapshot_id
        assert updated_task_obj_2.run_id
        assert updated_task_obj_2.logs
        assert "accuracy" in updated_task_obj_2.logs
        assert updated_task_obj_2.results
        assert updated_task_obj_2.results == {"accuracy": "0.56"}
        assert updated_task_obj_2.status == "SUCCESS"
        assert updated_task_obj_2.end_time
        assert updated_task_obj_2.duration

        self.task.stop(task_obj_2.id)

        # test if after snapshot has the file written
        after_snapshot_obj = self.task.dal.snapshot.get_by_id(
            updated_task_obj_2.after_snapshot_id)
        file_collection_obj = self.task.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)
        files_absolute_path = os.path.join(self.task.home,
                                           file_collection_obj.path)

        assert os.path.isfile(os.path.join(files_absolute_path, "task.log"))
        assert os.path.isfile(
            os.path.join(files_absolute_path, "new_file.txt"))

    def test_list(self):
        self.__setup()
        # Create tasks in the project
        task_obj_1 = self.task.create()
        task_obj_2 = self.task.create()

        # List all tasks regardless of filters
        result = self.task.list()

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

        # List all tasks regardless of filters in ascending
        result = self.task.list(sort_key='created_at', sort_order='ascending')

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result
        assert result[0].created_at <= result[-1].created_at

        # List all tasks regardless of filters in descending
        result = self.task.list(sort_key='created_at', sort_order='descending')
        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result
        assert result[0].created_at >= result[-1].created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.task.list(sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.task.list(sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_result = self.task.list(
            sort_key='created_at', sort_order='ascending')
        result = self.task.list(sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_result]
        ids = [item.id for item in result]
        assert set(expected_ids) == set(ids)

        # List all tasks and filter by session
        result = self.task.list(session_id=self.project.current_session.id)

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_files(self):
        self.__setup()
        # Create task in the project
        task_obj = self.task.create()

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create file to add
        self.project.file_driver.create("dirpath1", directory=True)
        self.project.file_driver.create(os.path.join("dirpath1", "filepath1"))

        # Snapshot dictionary
        snapshot_dict = {
            "filepaths": [
                os.path.join(self.project.home, "dirpath1", "filepath1")
            ],
        }

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command": task_command}

        # Test the default values
        updated_task_obj = self.task.run(
            task_obj.id, task_dict=task_dict, snapshot_dict=snapshot_dict)

        # TODO: Test case for during run and before_snapshot run
        # Get files for the task after run is complete (default)
        result = self.task.get_files(updated_task_obj.id)

        after_snapshot_obj = self.task.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        file_collection_obj = self.task.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)

        file_names = [item.name for item in result]

        assert len(result) == 2
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "r"
        assert os.path.join(self.task.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "task.log") in file_names
        assert os.path.join(self.task.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

        # Get files for the task after run is complete for different mode
        result = self.task.get_files(updated_task_obj.id, mode="a")

        assert len(result) == 2
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "a"
        assert os.path.join(self.task.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "task.log") in file_names
        assert os.path.join(self.task.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

        self.task.stop(task_obj.id)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_delete(self):
        self.__setup()
        # Create tasks in the project
        task_obj = self.task.create()

        # Delete task from the project
        result = self.task.delete(task_obj.id)

        # Check if task retrieval throws error
        thrown = False
        try:
            self.task.dal.snapshot.get_by_id(task_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
               thrown == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_failure(self):
        self.__setup()
        # 1) Test required arguments not provided
        # 2) Test too many arguments found
        # 3) Test incorrect task id given

        # 1) Test option 1
        failed = False
        try:
            self.task.stop()
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # 2) Test option 2
        failed = False
        try:
            self.task.stop(task_id="test_task_id", all=True)
        except TooManyArgumentsFound:
            failed = True
        assert failed

        # 3) Test option 3
        thrown = False
        try:
            self.task.stop(task_id="incorrect_task_id")
        except EntityNotFound:
            thrown = True
        assert thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_success(self):
        self.__setup()
        # 1) Test stop with task_id
        # 2) Test stop with all given

        # Create task in the project
        task_obj = self.task.create()

        # Create environment driver definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command": task_command}

        # 1) Test option 1
        updated_task_obj = self.task.run(task_obj.id, task_dict=task_dict)
        task_id = updated_task_obj.id
        result = self.task.stop(task_id=task_id)
        after_task_obj = self.task.dal.task.get_by_id(task_id)

        assert result
        assert after_task_obj.status == "STOPPED"

        # 2) Test option 2
        task_obj_2 = self.task.create()
        _ = self.task.run(task_obj_2.id, task_dict=task_dict)
        result = self.task.stop(all=True)
        all_task_objs = self.task.dal.task.query({})

        assert result
        for task_obj in all_task_objs:
            assert task_obj.status == "STOPPED"
