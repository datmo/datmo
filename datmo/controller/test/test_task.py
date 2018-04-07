"""
Tests for TaskController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import random
import string
import shutil
import tempfile

from datmo.controller.project import ProjectController
from datmo.controller.environment.environment import EnvironmentController
from datmo.controller.task import TaskController


class TestTaskController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        self.temp_dir = tempfile.mkdtemp('project')
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir)
        self.task = TaskController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test5", "test description")

        task_command = ["sh", "-c", "echo yo"]
        input_dict = {
            "command": task_command
        }

        # Create task in the project
        task_obj = self.task.create(input_dict)

        assert task_obj
        assert task_obj.command == task_command

    def test_run_helper(self):
        # TODO: Try out more options (see below)
        self.project.init("test5", "test description")

        # Create environment_driver id
        env_def_path = os.path.join(self.project.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        environment_obj = self.environment.create({
            "driver_type": "docker",
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
            "ports": [],
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

        return_code, container_id, hardware_info, logs = \
            self.task._run_helper(environment_obj.id,
                                  environment_obj.file_collection_id,
                                  log_filepath, options_dict)
        assert return_code == 0
        assert container_id and \
               self.task.environment_driver.get_container(container_id)
        assert hardware_info
        assert logs and \
               os.path.exists(log_filepath)
        self.task.environment_driver.stop_remove_containers_by_term(term=random_name)

        # Test option set 2
        random_name_2 = ''.join([random.choice(string.ascii_letters + string.digits)
                               for _ in range(32)])
        options_dict = {
            "command": ["sh", "-c", "echo yo"],
            "ports": [],
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

        return_code, container_id, hardware_info, logs = \
            self.task._run_helper(environment_obj.id,
                                  environment_obj.file_collection_id,
                                  log_filepath, options_dict)
        assert return_code == 0
        assert container_id and \
               self.task.environment_driver.get_container(container_id)
        assert hardware_info
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

        environment_obj = self.environment.create({
            "driver_type": "docker",
            "definition_filepath": env_def_path
        })

        # Create files to add
        self.project.file_driver.create("dirpath1", dir=True)
        self.project.file_driver.create("dirpath2", dir=True)
        self.project.file_driver.create("filepath1")

        # Task run dictionary
        task_run_dict = {
            "filepaths": [os.path.join(self.project.home, "dirpath1"),
                          os.path.join(self.project.home, "dirpath2"),
                          os.path.join(self.project.home, "filepath1")],
            "environment_id": environment_obj.id,
            "config": {},
            "stats": {},
            "environment_file_collection_id": environment_obj.file_collection_id
        }

        # Run a basic task in the project
        updated_task_obj = self.task.run(task_obj.id,
                                         task_run_dict)

        assert task_obj.id == updated_task_obj.id

        assert updated_task_obj.before_snapshot_id
        assert updated_task_obj.ports == []
        assert updated_task_obj.gpu == False
        assert updated_task_obj.interactive == False
        assert updated_task_obj.task_dirpath
        assert updated_task_obj.log_filepath

        assert updated_task_obj.after_snapshot_id
        assert updated_task_obj.hardware_info
        assert updated_task_obj.container_id
        assert updated_task_obj.logs
        assert updated_task_obj.status == "SUCCESS"