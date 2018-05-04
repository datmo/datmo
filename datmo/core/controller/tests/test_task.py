"""
Tests for TaskController
"""
import os
import random
import string
import tempfile
import platform
import datetime
from io import open, TextIOWrapper
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.task import TaskController
from datmo.core.util.exceptions import EntityNotFound, TaskRunException, InvalidArgumentType


class TestTaskController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.environment = EnvironmentController(self.temp_dir)
        self.task = TaskController(self.temp_dir)

    def teardown_method(self):
        pass

    def test_create(self):
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_gpu = False
        input_dict = {"command": task_command, "gpu": task_gpu}

        # Create task in the project
        task_obj = self.task.create(input_dict)

        assert task_obj
        assert task_obj.command == task_command
        assert task_obj.gpu == task_gpu

    def test_run_helper(self):
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
            "gpu": False,
            "name": random_name,
            "volumes": {
                temp_test_dirpath: {
                    'bind': '/task/',
                    'mode': 'rw'
                }
            },
            "detach": False,
            "stdin_open": True,
            "tty": False,
            "api": False
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
            "gpu": False,
            "name": random_name_2,
            "volumes": {
                temp_test_dirpath: {
                    'bind': '/task/',
                    'mode': 'rw'
                }
            },
            "detach": False,
            "stdin_open": True,
            "tty": False,
            "api": True
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

    def test_run(self):
        # 1) Test success case with default values and env def file
        # 2) Test failure case if running same task (conflicting containers)
        # 3) Test failure case if running same task with snapshot_dict (conflicting containers)
        # 4) Test success case with snapshot_dict
        # 5) Test success case with saved file during task run

        # TODO: look into log filepath randomness, sometimes logs are not written
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        input_dict = {"command": task_command}

        # Create task in the project
        task_obj = self.task.create(input_dict)

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # 1) Test option 1
        updated_task_obj = self.task.run(task_obj.id)

        assert task_obj.id == updated_task_obj.id

        assert updated_task_obj.before_snapshot_id
        assert updated_task_obj.ports == None
        assert updated_task_obj.gpu == False
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

        # 2) Test option 2
        failed = False
        try:
            self.task.run(task_obj.id)
        except TaskRunException:
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
        except TaskRunException:
            failed = True
        assert failed

        # Test when the specific task id is already RUNNING
        # Create task in the project
        task_obj_1 = self.task.create(input_dict)
        self.task.dal.task.update({"id": task_obj_1.id, "status": "RUNNING"})
        # Create environment_driver definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        failed = False
        try:
            self.task.run(task_obj_1.id)
        except TaskRunException:
            failed = True
        assert failed

        # 4) Test option 4

        # Create a new task in the project
        task_obj_2 = self.task.create(input_dict)

        # Run another task in the project
        updated_task_obj_2 = self.task.run(
            task_obj_2.id, snapshot_dict=snapshot_dict)

        assert task_obj_2.id == updated_task_obj_2.id

        assert updated_task_obj_2.before_snapshot_id
        assert updated_task_obj_2.ports == None
        assert updated_task_obj_2.gpu == False
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

        task_command = ["python", "script.py"]
        input_dict = {"command": task_command}

        # Create task in the project
        task_obj_2 = self.task.create(input_dict)

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        updated_task_obj_2 = self.task.run(task_obj_2.id)

        assert updated_task_obj_2.before_snapshot_id
        assert updated_task_obj_2.ports == None
        assert updated_task_obj_2.gpu == False
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
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        input_dict_1 = {
            "command": task_command,
            "created_at": datetime.datetime(2017, 2, 1)
        }

        input_dict_2 = {
            "command": task_command,
            "created_at": datetime.datetime(2017, 3, 1)
        }

        # Create tasks in the project
        task_obj_1 = self.task.create(input_dict_1)
        task_obj_2 = self.task.create(input_dict_2)

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
        expected_result = self.task.list(sort_key='created_at', sort_order='ascending')
        result = self.task.list(sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_result]
        ids = [item.id for item in result]
        assert set(expected_ids) == set(ids)

        # List all tasks and filter by session
        result = self.task.list(session_id=self.project.current_session.id)

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

    def test_get_files(self):
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        input_dict = {"command": task_command}

        # Create task in the project
        task_obj = self.task.create(input_dict)

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

        # Test the default values
        updated_task_obj = self.task.run(
            task_obj.id, snapshot_dict=snapshot_dict)

        # TODO: Test case for during run and before_snapshot run
        # Get files for the task after run is complete (default)
        result = self.task.get_files(updated_task_obj.id)

        after_snapshot_obj = self.task.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        file_collection_obj = self.task.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)

        assert len(result) == 2
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].name == os.path.join(
            self.task.home, ".datmo", "collections",
            file_collection_obj.filehash, "task.log")
        assert result[0].mode == "r"
        assert isinstance(result[1], TextIOWrapper)
        assert result[1].name == os.path.join(
            self.task.home, ".datmo", "collections",
            file_collection_obj.filehash, "filepath1")
        assert result[1].mode == "r"

        # Get files for the task after run is complete for different mode
        result = self.task.get_files(updated_task_obj.id, mode="a")

        assert len(result) == 2
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].name == os.path.join(
            self.task.home, ".datmo", "collections",
            file_collection_obj.filehash, "task.log")
        assert result[0].mode == "a"
        assert isinstance(result[1], TextIOWrapper)
        assert result[1].name == os.path.join(
            self.task.home, ".datmo", "collections",
            file_collection_obj.filehash, "filepath1")
        assert result[1].mode == "a"

    def test_delete(self):
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        input_dict = {"command": task_command}

        # Create tasks in the project
        task_obj = self.task.create(input_dict)

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

    def test_stop(self):
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        input_dict = {"command": task_command}

        # Create task in the project
        task_obj = self.task.create(input_dict)

        # Create environment driver definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Test the default values
        updated_task_obj = self.task.run(task_obj.id)

        # Stop the task
        task_id = updated_task_obj.id
        result = self.task.stop(task_id)

        # Check if task stop throws error when wrong task id is given
        thrown = False
        try:
            self.task.dal.snapshot.get_by_id(task_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
               thrown == True
