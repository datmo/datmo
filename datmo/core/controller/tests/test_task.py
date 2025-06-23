"""
Tests for TaskController
"""
import os
import uuid
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
from datmo.core.entity.task import Task
from datmo.core.util.exceptions import EntityNotFound, TaskRunError, \
    InvalidArgumentType, RequiredArgumentMissing, ProjectNotInitialized, \
    InvalidProjectPath, TooManyArgumentsFound, DoesNotExist
from datmo.core.util.misc_functions import check_docker_inactive, pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestTaskController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
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
        self.environment_controller = EnvironmentController()
        self.task_controller = TaskController()

    def test_init_fail_project_not_init(self):
        Config().set_home(self.temp_dir)
        failed = False
        try:
            TaskController()
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_init_fail_invalid_path(self):
        test_home = "some_random_dir"
        Config().set_home(test_home)
        failed = False
        try:
            TaskController()
        except InvalidProjectPath:
            failed = True
        assert failed

    def test_create(self):
        self.__setup()
        # Create task in the project
        task_obj = self.task_controller.create()

        assert isinstance(task_obj, Task)
        assert task_obj.created_at
        assert task_obj.updated_at

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_helper(self):
        self.__setup()
        # TODO: Try out more options (see below)
        # Create environment_driver id
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        paths = [env_def_path]
        environment_obj = self.environment_controller.create({"paths": paths})
        self.environment_ids.append(environment_obj.id)

        # Set log filepath
        log_filepath = os.path.join(self.task_controller.home, "test.log")

        # create volume to mount
        temp_test_dirpath = os.path.join(self.temp_dir, "temp")
        os.makedirs(temp_test_dirpath)

        # Test option set 1
        random_name = str(uuid.uuid1())
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
            "mem_limit": "4g",
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False,
            "interactive": False
        }

        return_code, run_id, logs = \
            self.task_controller._run_helper(environment_obj.id,
                                  options_dict, log_filepath)
        assert return_code == 0
        assert run_id and \
               self.task_controller.environment_driver.get_container(run_id)
        assert logs and \
               os.path.exists(log_filepath)
        self.task_controller.environment_driver.stop_remove_containers_by_term(
            term=random_name)

        # Test option set 2
        random_name_2 = str(uuid.uuid1())
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
            "mem_limit": "4g",
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": True,
            "interactive": False
        }

        return_code, run_id, logs = \
            self.task_controller._run_helper(environment_obj.id,
                                  options_dict, log_filepath)
        assert return_code == 0
        assert run_id and \
               self.task_controller.environment_driver.get_container(run_id)
        assert logs and \
               os.path.exists(log_filepath)
        self.task_controller.environment_driver.stop_remove_containers_by_term(
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
        result = self.task_controller._parse_logs_for_results(test_logs)

        assert isinstance(result, dict)
        assert result['accuracy'] == "0.94"
        assert result['validation'] == "0.32"
        assert result['model_type'] == "logistic regression"

        test_logs = """test"""
        result = self.task_controller._parse_logs_for_results(test_logs)
        assert result is None

    def test_update_environment_run_options(self):
        self.__setup()
        environment_run_option = {
            "command": ["python", "script.py"],
            "volumes": {
                os.path.join(self.temp_dir, "/temp_task"): {
                    'bind': '/task/',
                    'mode': 'rw'
                },
                self.temp_dir: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            }
        }
        # create data file
        data_dirpath = os.path.join(self.temp_dir, "data")
        data_file_dirpath = os.path.join(self.temp_dir, "data_folder")
        data_filepath = os.path.join(data_file_dirpath, "data_file.txt")
        os.mkdir(data_dirpath)
        os.mkdir(data_file_dirpath)
        with open(data_filepath, "wb") as f:
            f.write(to_bytes("data file"))

        data_file_path_map = [(data_filepath, "data_file.txt")]
        data_directory_path_map = [(data_dirpath, "data_directory")]

        environment_run_option = self.task_controller._update_environment_run_options(
            environment_run_option, data_file_path_map,
            data_directory_path_map)

        assert environment_run_option["volumes"][data_file_dirpath] == {
            'bind': '/data/',
            'mode': 'rw'
        }
        assert environment_run_option["volumes"][data_dirpath] == {
            'bind': '/data/data_directory',
            'mode': 'rw'
        }

        # Error by passing directory which does not exist
        data_dirpath = os.path.join(self.temp_dir, "data_dne")
        data_filepath = os.path.join(self.temp_dir, "data_dne",
                                     "data_file.txt")
        data_file_path_map = [(data_filepath, "data_file.txt")]
        data_directory_path_map = [(data_dirpath, "data_directory")]
        failed = False
        try:
            self.task_controller._update_environment_run_options(
                environment_run_option, data_file_path_map,
                data_directory_path_map)
        except TaskRunError:
            failed = True

        assert failed

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        self.__setup()
        # 0) Test failure case without command and without interactive
        # 1) Test success case with default values and env def file
        # 2) Test failure case if running same task (conflicting containers)
        # 3) Test failure case if running same task with snapshot_dict (conflicting containers)
        # 4) Test success case with snapshot_dict
        # 5) Test success case with saved file during task run
        # 6) Test success case with data file path being passed
        # 7) Test success case with data directory path being passed

        # TODO: look into log filepath randomness, sometimes logs are not written

        # Create task in the project
        task_obj = self.task_controller.create()

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # 0) Test option 0
        failed = False
        try:
            self.task_controller.run(task_obj.id)
        except RequiredArgumentMissing:
            failed = True
        assert failed

        failed = False
        try:
            self.task_controller.run(
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
        task_dict = {"command_list": task_command}

        # 1) Test option 1
        updated_task_obj = self.task_controller.run(
            task_obj.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

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
        assert after_snapshot_obj.stats == {"accuracy": "0.45"}
        assert updated_task_obj.status == "SUCCESS"
        assert updated_task_obj.end_time
        assert updated_task_obj.duration

        self.task_controller.stop(task_obj.id)

        # 2) Test option 2
        failed = False
        try:
            self.task_controller.run(task_obj.id)
        except TaskRunError:
            failed = True
        assert failed

        # 3) Test option 3

        # Create files to add
        self.project_controller.file_driver.create("dirpath1", directory=True)
        self.project_controller.file_driver.create("dirpath2", directory=True)
        self.project_controller.file_driver.create("filepath1")

        # Snapshot dictionary
        snapshot_dict = {
            "paths": [
                os.path.join(self.project_controller.home, "dirpath1"),
                os.path.join(self.project_controller.home, "dirpath2"),
                os.path.join(self.project_controller.home, "filepath1")
            ],
        }

        # Run a basic task in the project
        failed = False
        try:
            self.task_controller.run(task_obj.id, snapshot_dict=snapshot_dict)
        except TaskRunError:
            failed = True
        assert failed

        # Test when the specific task id is already RUNNING
        # Create task in the project
        task_obj_1 = self.task_controller.create()
        self.task_controller.dal.task.update({
            "id": task_obj_1.id,
            "status": "RUNNING"
        })
        # Create environment_driver definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        failed = False
        try:
            self.task_controller.run(task_obj_1.id, task_dict=task_dict)
        except TaskRunError:
            failed = True
        assert failed

        # 4) Test option 4

        # Create a new task in the project
        task_obj_2 = self.task_controller.create()

        # Run another task in the project
        updated_task_obj_2 = self.task_controller.run(
            task_obj_2.id, task_dict=task_dict, snapshot_dict=snapshot_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_2.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

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

        self.task_controller.stop(task_obj_2.id)

        # 5) Test option 5

        # Create a basic script
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("import shutil\n"))
            f.write(to_bytes("print('hello')\n"))
            f.write(to_bytes("print(' accuracy: 0.56 ')\n"))
            f.write(
                to_bytes(
                    "with open(os.path.join('/task', 'new_file.txt'), 'a') as f:\n"
                ))
            f.write(to_bytes("    f.write('my test file')\n"))

        # Create task in the project
        task_obj_2 = self.task_controller.create()

        # Create task_dict
        task_command = ["python", "script.py"]
        task_dict = {"command_list": task_command}

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        updated_task_obj_2 = self.task_controller.run(
            task_obj_2.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_2.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

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

        self.task_controller.stop(task_obj_2.id)

        # test if after snapshot has the file written
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_2.after_snapshot_id)
        file_collection_obj = self.task_controller.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)
        files_absolute_path = os.path.join(self.task_controller.home,
                                           file_collection_obj.path)

        assert os.path.isfile(os.path.join(files_absolute_path, "task.log"))
        assert os.path.isfile(
            os.path.join(files_absolute_path, "new_file.txt"))

        # 6) Test Option 6
        self.project_controller.file_driver.create("dirpath1", directory=True)
        self.project_controller.file_driver.create(
            os.path.join("dirpath1", "file.txt"))
        with open(
                os.path.join(self.project_controller.home, "dirpath1",
                             "file.txt"), "wb") as f:
            f.write(to_bytes('my initial line\n'))
        test_filename = "script.py"
        test_filepath = os.path.join(self.temp_dir, test_filename)
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("print('hello')\n"))
            f.write(to_bytes("import shutil\n"))

            f.write(
                to_bytes(
                    "with open(os.path.join('/data', 'file.txt'), 'a') as f:\n"
                ))
            f.write(to_bytes("    f.write('my test file')\n"))

        # Create task in the project
        task_obj_3 = self.task_controller.create()

        # Create task_dict
        task_command = ["python", test_filename]
        task_dict = {
            "command_list":
                task_command,
            "data_file_path_map": [(os.path.join(self.project_controller.home,
                                                 "dirpath1", "file.txt"),
                                    'file.txt')]
        }

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        updated_task_obj_3 = self.task_controller.run(
            task_obj_3.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_3.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

        assert isinstance(updated_task_obj_3, Task)
        assert updated_task_obj_3.before_snapshot_id
        assert updated_task_obj_3.ports == None
        assert updated_task_obj_3.interactive == False
        assert updated_task_obj_3.task_dirpath
        assert updated_task_obj_3.log_filepath
        assert updated_task_obj_3.start_time

        assert updated_task_obj_3.after_snapshot_id
        assert updated_task_obj_3.run_id
        assert updated_task_obj_3.logs
        assert updated_task_obj_3.status == "SUCCESS"
        assert updated_task_obj_3.end_time
        assert updated_task_obj_3.duration

        self.task_controller.stop(task_obj_3.id)

        # test if after snapshot has the file written
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_3.after_snapshot_id)
        file_collection_obj = self.task_controller.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)
        files_absolute_path = os.path.join(self.task_controller.home,
                                           file_collection_obj.path)

        assert os.path.isfile(os.path.join(files_absolute_path, "task.log"))
        assert os.path.isfile(
            os.path.join(self.project_controller.home, "dirpath1", "file.txt"))
        assert "my initial line" in open(
            os.path.join(self.project_controller.home, "dirpath1", "file.txt"),
            "r").read()
        assert "my test file" in open(
            os.path.join(self.project_controller.home, "dirpath1", "file.txt"),
            "r").read()

        # 7) Test Option 7
        self.project_controller.file_driver.create("dirpath1", directory=True)
        self.project_controller.file_driver.create(
            os.path.join("dirpath1", "file.txt"))
        with open(
                os.path.join(self.project_controller.home, "dirpath1",
                             "file.txt"), "wb") as f:
            f.write(to_bytes('my initial line\n'))
        test_filename = "script.py"
        test_filepath = os.path.join(self.temp_dir, test_filename)
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("print('hello')\n"))
            f.write(to_bytes("import shutil\n"))

            f.write(
                to_bytes(
                    "with open(os.path.join('/data', 'dirpath1', 'file.txt'), 'a') as f:\n"
                ))
            f.write(to_bytes("    f.write('my test file')\n"))

        # Create task in the project
        task_obj_4 = self.task_controller.create()

        # Create task_dict
        task_command = ["python", test_filename]
        task_dict = {
            "command_list":
                task_command,
            "data_directory_path_map": [(os.path.join(
                self.project_controller.home, "dirpath1"), 'dirpath1')]
        }

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        updated_task_obj_4 = self.task_controller.run(
            task_obj_4.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_4.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

        assert isinstance(updated_task_obj_4, Task)
        assert updated_task_obj_4.before_snapshot_id
        assert updated_task_obj_4.ports == None
        assert updated_task_obj_4.interactive == False
        assert updated_task_obj_4.task_dirpath
        assert updated_task_obj_4.log_filepath
        assert updated_task_obj_4.start_time

        assert updated_task_obj_4.after_snapshot_id
        assert updated_task_obj_4.run_id
        assert updated_task_obj_4.logs
        assert updated_task_obj_4.status == "SUCCESS"
        assert updated_task_obj_4.end_time
        assert updated_task_obj_4.duration

        self.task_controller.stop(task_obj_4.id)

        # test if after snapshot has the file written
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj_4.after_snapshot_id)
        file_collection_obj = self.task_controller.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)
        files_absolute_path = os.path.join(self.task_controller.home,
                                           file_collection_obj.path)

        assert os.path.isfile(os.path.join(files_absolute_path, "task.log"))
        assert os.path.isfile(
            os.path.join(self.project_controller.home, "dirpath1", "file.txt"))
        assert "my initial line" in open(
            os.path.join(self.project_controller.home, "dirpath1", "file.txt"),
            "r").read()
        assert "my test file" in open(
            os.path.join(self.project_controller.home, "dirpath1", "file.txt"),
            "r").read()

    def test_list(self):
        self.__setup()
        # Create tasks in the project
        task_obj_1 = self.task_controller.create()
        task_obj_2 = self.task_controller.create()

        # List all tasks regardless of filters
        result = self.task_controller.list()

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

        # List all tasks regardless of filters in ascending
        result = self.task_controller.list(
            sort_key='created_at', sort_order='ascending')

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result
        assert result[0].created_at <= result[-1].created_at

        # List all tasks regardless of filters in descending
        result = self.task_controller.list(
            sort_key='created_at', sort_order='descending')
        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result
        assert result[0].created_at >= result[-1].created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.task_controller.list(
                sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.task_controller.list(
                sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_result = self.task_controller.list(
            sort_key='created_at', sort_order='ascending')
        result = self.task_controller.list(
            sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_result]
        ids = [item.id for item in result]
        assert set(expected_ids) == set(ids)

        # List all tasks
        result = self.task_controller.list()

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

    def test_get(self):
        self.__setup()
        # Test failure for no task
        failed = False
        try:
            self.task_controller.get("random")
        except DoesNotExist:
            failed = True
        assert failed

        # Test success for task
        task_obj = self.task_controller.create()
        task_obj_returned = self.task_controller.get(task_obj.id)
        assert task_obj == task_obj_returned

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_files(self):
        self.__setup()
        # Test failure case
        failed = False
        try:
            self.task_controller.get_files("random")
        except DoesNotExist:
            failed = True
        assert failed

        # Create task in the project
        task_obj = self.task_controller.create()

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create file to add
        self.project_controller.file_driver.create("dirpath1", directory=True)
        self.project_controller.file_driver.create(
            os.path.join("dirpath1", "filepath1"))

        # Snapshot dictionary
        snapshot_dict = {
            "paths": [
                os.path.join(self.project_controller.home, "dirpath1",
                             "filepath1")
            ],
        }

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command_list": task_command}

        # Test the default values
        updated_task_obj = self.task_controller.run(
            task_obj.id, task_dict=task_dict, snapshot_dict=snapshot_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)

        # TODO: Test case for during run and before_snapshot run
        # Get files for the task after run is complete (default)
        result = self.task_controller.get_files(updated_task_obj.id)

        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        file_collection_obj = self.task_controller.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id)

        file_names = [item.name for item in result]

        assert len(result) == 2
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "r"
        assert os.path.join(self.task_controller.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "task.log") in file_names
        assert os.path.join(self.task_controller.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

        # Get files for the task after run is complete for different mode
        result = self.task_controller.get_files(updated_task_obj.id, mode="a")

        assert len(result) == 2
        for item in result:
            assert isinstance(item, TextIOWrapper)
            assert item.mode == "a"
        assert os.path.join(self.task_controller.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "task.log") in file_names
        assert os.path.join(self.task_controller.home, ".datmo", "collections",
                            file_collection_obj.filehash,
                            "filepath1") in file_names

        self.task_controller.stop(task_obj.id)

    def test_update(self):
        self.__setup()
        # Create task in the project
        task_obj = self.task_controller.create()
        assert isinstance(task_obj, Task)

        # Test 1: When no meta data is passed
        updated_task_obj = self.task_controller.update(task_obj.id)
        assert updated_task_obj.workspace is None

        # Test 2: When meta data for workspace is passed
        test_workspace = "notebook"
        test_command = "python script.py"
        updated_task_obj = self.task_controller.update(
            task_obj.id, workspace=test_workspace, command=test_command)
        assert updated_task_obj.workspace == test_workspace
        assert updated_task_obj.command == test_command
        assert updated_task_obj.command_list == ["python", "script.py"]

        # Test 3: When meta data for workspace is passed
        test_interactive = True
        updated_task_obj = self.task_controller.update(
            task_obj.id, interactive=test_interactive)
        assert updated_task_obj.interactive == test_interactive

        # Test 4: When meta data for workspace is passed
        test_command_list = ["python", "script.py"]
        updated_task_obj = self.task_controller.update(
            task_obj.id, command_list=test_command_list)
        assert updated_task_obj.command_list == ["python", "script.py"]

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_delete(self):
        self.__setup()
        # Create tasks in the project
        task_obj = self.task_controller.create()

        # Delete task from the project
        result = self.task_controller.delete(task_obj.id)

        # Check if task retrieval throws error
        thrown = False
        try:
            self.task_controller.dal.snapshot.get_by_id(task_obj.id)
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
            self.task_controller.stop()
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # 2) Test option 2
        failed = False
        try:
            self.task_controller.stop(task_id="test_task_id", all=True)
        except TooManyArgumentsFound:
            failed = True
        assert failed

        # 3) Test option 3
        thrown = False
        try:
            self.task_controller.stop(task_id="incorrect_task_id")
        except DoesNotExist:
            thrown = True
        assert thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_success(self):
        self.__setup()
        # 1) Test stop with task_id
        # 2) Test stop with all given

        # Create task in the project
        task_obj = self.task_controller.create()

        # Create environment driver definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command_list": task_command}

        # 1) Test option 1
        updated_task_obj = self.task_controller.run(
            task_obj.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)
        task_id = updated_task_obj.id
        result = self.task_controller.stop(task_id=task_id)
        after_task_obj = self.task_controller.dal.task.get_by_id(task_id)

        assert result
        assert after_task_obj.status == "STOPPED"

        # 2) Test option 2
        task_obj_2 = self.task_controller.create()
        updated_task_obj = self.task_controller.run(
            task_obj_2.id, task_dict=task_dict)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id)
        environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        self.environment_ids.append(environment_obj.id)
        result = self.task_controller.stop(all=True)
        all_task_objs = self.task_controller.dal.task.query({})

        assert result
        for task_obj in all_task_objs:
            assert task_obj.status == "STOPPED"
