"""
Tests for TaskController
"""
import os
import random
import string
import shutil
import tempfile

from datmo.controller.project import ProjectController
from datmo.controller.environment.environment import EnvironmentController
from datmo.controller.task import TaskController
from datmo.util.exceptions import EntityNotFound, \
    EnvironmentExecutionException


class TestTaskController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir, self.project.dal.driver)
        self.task = TaskController(self.temp_dir, self.project.dal.driver)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test5", "test description")
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
        self.project.init("test5", "test description")

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

        return_code, container_id, logs = \
            self.task._run_helper(environment_obj.id,
                                  options_dict, log_filepath)
        assert return_code == 0
        assert container_id and \
               self.task.environment_driver.get_container(container_id)
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

        return_code, container_id, logs = \
            self.task._run_helper(environment_obj.id,
                                  options_dict, log_filepath)
        assert return_code == 0
        assert container_id and \
               self.task.environment_driver.get_container(container_id)
        assert logs and \
               os.path.exists(log_filepath)
        self.task.environment_driver.stop_remove_containers_by_term(term=random_name_2)

    def test_run(self):
        self.project.init("test5", "test description")

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

        assert updated_task_obj.after_snapshot_id
        assert updated_task_obj.container_id
        assert updated_task_obj.logs
        assert updated_task_obj.status == "SUCCESS"

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
        try:
            self.task.run(task_obj.id,
                          snapshot_dict=snapshot_dict)
        except EnvironmentExecutionException:
            assert True

        # Test running a different task again with different parameters
        # THIS WILL UPDATE THE SAME TASK AND LOSE ORIGINAL TASK WORK
        # This will fail because running the same task id (conflicting containers)

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

        assert updated_task_obj_1.after_snapshot_id
        assert updated_task_obj_1.container_id
        assert updated_task_obj_1.logs
        assert updated_task_obj_1.status == "SUCCESS"

    def test_list(self):
        self.project.init("test5", "test description")

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


    def test_delete(self):
        self.project.init("test5", "test description")

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