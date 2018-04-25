"""
Tests for TaskController
"""
import os
import random
import string
import shutil
import tempfile
from io import TextIOWrapper

from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.task import TaskController
from datmo.core.util.exceptions import EntityNotFound, \
    EnvironmentExecutionException


class TestTaskController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.environment = EnvironmentController(self.temp_dir)
        self.task = TaskController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        task_command = ["sh", "-c", "echo yo"]
        task_gpu = False
        input_dict = {
            "command": task_command,
            "gpu": task_gpu
        }

        # Create task in the project
        task_obj = self.task.create(input_dict)

        assert task_obj
        assert task_obj.command == task_command
        assert task_obj.gpu == task_gpu

    def test_run_helper(self):
        # TODO: Try out more options (see below)
        # Create environment_driver id
        env_def_path = os.path.join(self.project.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        environment_obj = self.environment.create({
            "definition_filepath": env_def_path
        })

        # Set log filepath
        log_filepath = os.path.join(self.task.home,
                                    "test.log")

        # create volume to mount
        temp_test_dirpath = os.path.join(self.temp_dir, "temp")
        os.makedirs(temp_test_dirpath)

        # Test option set 1
        random_name = ''.join([random.choice(string.ascii_letters + string.digits)
                               for _ in range(32)])
        options_dict = {
            "command": ["sh", "-c", "echo yo"],
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
        self.task.environment_driver.stop_remove_containers_by_term(term=random_name)

        # Test option set 2
        random_name_2 = ''.join([random.choice(string.ascii_letters + string.digits)
                               for _ in range(32)])
        options_dict = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "gpu": False,
            "name": random_name_2 ,
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
        self.task.environment_driver.stop_remove_containers_by_term(term=random_name_2)

    def test_run(self):
        # TODO: look into log filepath randomness, sometimes logs are not written
        task_command = ["sh", "-c", "echo yo"]
        input_dict = {
            "command": task_command
        }

        # Create task in the project
        task_obj = self.task.create(input_dict)

        # Create environment_driver definition
        env_def_path = os.path.join(self.project.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        # Test the default values
        updated_task_obj = self.task.run(task_obj.id)

        assert task_obj.id == updated_task_obj.id

        assert updated_task_obj.before_snapshot_id
        assert updated_task_obj.ports == []
        assert updated_task_obj.gpu == False
        assert updated_task_obj.interactive == False
        assert updated_task_obj.task_dirpath
        assert updated_task_obj.log_filepath
        assert updated_task_obj.start_time

        assert updated_task_obj.after_snapshot_id
        assert updated_task_obj.run_id
        assert updated_task_obj.logs
        assert updated_task_obj.status == "SUCCESS"
        assert updated_task_obj.results == {}
        assert updated_task_obj.end_time
        assert updated_task_obj.duration

        # Test running the same task again with different parameters
        # THIS WILL UPDATE THE SAME TASK AND LOSE ORIGINAL TASK WORK
        # This will fail because running the same task id (conflicting containers)

        # Create files to add
        self.project.file_driver.create("dirpath1", dir=True)
        self.project.file_driver.create("dirpath2", dir=True)
        self.project.file_driver.create("filepath1")

        # Snapshot dictionary
        snapshot_dict = {
            "filepaths": [os.path.join(self.project.home, "dirpath1"),
                          os.path.join(self.project.home, "dirpath2"),
                          os.path.join(self.project.home, "filepath1")],
        }

        # Run a basic task in the project
        failed = False
        try:
            self.task.run(task_obj.id,
                          snapshot_dict=snapshot_dict)
        except EnvironmentExecutionException:
            failed = True
        assert failed

        # Test for Task where the snapshot dictionary is passed in and succeeds

        # Create a new task in the project
        task_obj_1 = self.task.create(input_dict)

        # Run another task in the project
        updated_task_obj_1 = self.task.run(task_obj_1.id,
                                           snapshot_dict=snapshot_dict)

        assert task_obj_1.id == updated_task_obj_1.id

        assert updated_task_obj_1.before_snapshot_id
        assert updated_task_obj_1.ports == []
        assert updated_task_obj_1.gpu == False
        assert updated_task_obj_1.interactive == False
        assert updated_task_obj_1.task_dirpath
        assert updated_task_obj_1.log_filepath
        assert updated_task_obj_1.start_time

        assert updated_task_obj_1.after_snapshot_id
        assert updated_task_obj_1.run_id
        assert updated_task_obj_1.logs
        assert updated_task_obj_1.status == "SUCCESS"
        assert updated_task_obj_1.results == {}
        assert updated_task_obj_1.end_time
        assert updated_task_obj_1.duration

    def test_list(self):
        task_command = ["sh", "-c", "echo yo"]
        input_dict = {
            "command": task_command
        }

        # Create tasks in the project
        task_obj_1 = self.task.create(input_dict)
        task_obj_2 = self.task.create(input_dict)

        # List all tasks regardless of filters
        result = self.task.list()

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

        # List all tasks and filter by session
        result = self.task.list(session_id=
                                self.project.current_session.id)

        assert len(result) == 2 and \
               task_obj_1 in result and \
               task_obj_2 in result

    def test_get_files(self):
        task_command = ["sh", "-c", "echo yo"]
        input_dict = {
            "command": task_command
        }

        # Create task in the project
        task_obj = self.task.create(input_dict)

        # Create environment definition
        env_def_path = os.path.join(self.project.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        # Create file to add
        self.project.file_driver.create("dirpath1", dir=True)
        self.project.file_driver.create(os.path.join("dirpath1", "filepath1"))

        # Snapshot dictionary
        snapshot_dict = {
            "filepaths": [os.path.join(self.project.home, "dirpath1", "filepath1")],
        }

        # Test the default values
        updated_task_obj = self.task.run(task_obj.id,
                                         snapshot_dict=snapshot_dict)

        # TODO: Test case for during run and before_snapshot run
        # Get files for the task after run is complete (default)
        result = self.task.get_files(updated_task_obj.id)

        after_snapshot_obj = self.task.dal.snapshot.get_by_id(
            updated_task_obj.after_snapshot_id
        )
        file_collection_obj = self.task.dal.file_collection.get_by_id(
            after_snapshot_obj.file_collection_id
        )

        assert len(result) == 2
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].name == os.path.join(self.task.home, ".datmo",
                                              "collections",
                                              file_collection_obj.filehash,
                                              "task.log")
        assert result[0].mode == "r"
        assert isinstance(result[1], TextIOWrapper)
        assert result[1].name == os.path.join(self.task.home, ".datmo",
                                              "collections",
                                              file_collection_obj.filehash,
                                              "filepath1")
        assert result[1].mode == "r"

        # Get files for the task after run is complete for different mode
        result = self.task.get_files(updated_task_obj.id, mode="a")

        assert len(result) == 2
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].name == os.path.join(self.task.home, ".datmo",
                                              "collections",
                                              file_collection_obj.filehash,
                                              "task.log")
        assert result[0].mode == "a"
        assert isinstance(result[1], TextIOWrapper)
        assert result[1].name == os.path.join(self.task.home, ".datmo",
                                              "collections",
                                              file_collection_obj.filehash,
                                              "filepath1")
        assert result[1].mode == "a"

    def test_delete(self):
        task_command = ["sh", "-c", "echo yo"]
        input_dict = {
            "command": task_command
        }

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
        task_command = ["sh", "-c", "echo yo"]
        input_dict = {
            "command": task_command
        }

        # Create task in the project
        task_obj = self.task.create(input_dict)

        # Create environment driver definition
        env_def_path = os.path.join(self.project.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

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