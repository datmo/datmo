"""
Tests for EnvironmentController
"""
import os
import uuid
import random
import string
import shutil
import tempfile
import platform
import timeout_decorator
from io import open
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
from datmo.core.controller.environment.environment import \
    EnvironmentController
from datmo.core.entity.environment import Environment
from datmo.core.util.exceptions import (
    EntityNotFound, RequiredArgumentMissing, TooManyArgumentsFound,
    FileAlreadyExistsError, UnstagedChanges, EnvironmentDoesNotExist)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestEnvironmentController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir)

    def teardown_method(self):
        pass

    def __setup(self):
        self.project.init("test_setup", "test description")
        with open(os.path.join(self.temp_dir, "test.txt"), "wb") as f:
            f.write(to_bytes("hello"))
        with open(
                os.path.join(self.environment.environment_directory, "test"),
                "wb") as f:
            f.write(to_bytes("cool"))
        self.definition_filepath = os.path.join(
            self.environment.environment_directory, "Dockerfile")
        with open(self.definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu"))

    def test_get_supported_environments(self):
        result = self.environment.get_supported_environments()
        assert result

    def test_setup(self):
        self.project.init("test_setup", "test description")

        # Test success setup once (no files present)
        options = {"name": "xgboost:cpu"}
        result = self.environment.setup(options=options)
        output_definition_filepath = os.path.join(
            self.environment.environment_directory, "Dockerfile")

        assert isinstance(result, Environment)
        assert result.name == options['name']
        assert result.description == "supported base environment created by datmo"
        assert os.path.isfile(output_definition_filepath)
        assert "FROM datmo/xgboost:cpu" in open(output_definition_filepath,
                                                "r").read()

        # Test success setup again (files present, but staged)
        options = {"name": "xgboost:cpu"}
        result = self.environment.setup(options=options)
        output_definition_filepath = os.path.join(
            self.environment.environment_directory, "Dockerfile")

        assert isinstance(result, Environment)
        assert result.name == options['name']
        assert result.description == "supported base environment created by datmo"
        assert os.path.isfile(output_definition_filepath)
        assert "FROM datmo/xgboost:cpu" in open(output_definition_filepath,
                                                "r").read()

        # Test failure in downstream function (e.g. bad inputs, no name given)
        failed = False
        try:
            self.environment.setup(options={})
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        # Change environment file
        with open(output_definition_filepath, "wb") as f:
            f.write(to_bytes("new content"))

        # Test failure setup (unstaged changes)
        failed = False
        try:
            self.environment.setup(options=options)
        except UnstagedChanges:
            failed = True
        assert failed

    def test_create(self):
        # 0) Test SUCCESS create when definition path exists in project environment directory (no input, no root) -- with hardware file
        # 1) Test SUCCESS create when definition path exists in project environment directory (no input, no root)
        # 5) Test SUCCESS when definition path exists in project environment directory and passed from input dict (takes input)
        # 2) Test SUCCESS create when definition path exists in root project folder (no input, no project environment dir)
        # 3) Test SUCCESS create when definition path is passed into input dict (takes input, no project environment dir)
        # 4) Test SUCCESS create when definition path is passed into input dict along with expected filename to be saved
        # 6) Test FAIL when passing same filepath with same filename into input dict

        self.project.init("test3", "test description")

        self.__setup()

        input_dict_0 = {"name": "test", "description": "test description"}

        # 0) Test option 0 (cannot test hash because hardware is machine-dependent)
        environment_obj_0 = self.environment.create(input_dict_0)
        assert environment_obj_0
        assert isinstance(environment_obj_0, Environment)
        assert environment_obj_0.id
        assert environment_obj_0.driver_type == "docker"
        assert environment_obj_0.file_collection_id
        assert environment_obj_0.definition_filename
        assert environment_obj_0.hardware_info
        assert environment_obj_0.unique_hash
        assert environment_obj_0.name == "test"
        assert environment_obj_0.description == "test description"

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_0.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert os.path.isfile(os.path.join(file_collection_dir, "test"))
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))

        # 1) Test option 1
        environment_obj_0 = self.environment.create(
            input_dict_0, save_hardware_file=False)
        assert environment_obj_0
        assert isinstance(environment_obj_0, Environment)
        assert environment_obj_0.id
        assert environment_obj_0.driver_type == "docker"
        assert environment_obj_0.file_collection_id
        assert environment_obj_0.definition_filename
        assert environment_obj_0.hardware_info
        assert environment_obj_0.unique_hash == "d4e62871c1e6033bf3d045f91107fafe"
        assert environment_obj_0.name == "test"
        assert environment_obj_0.description == "test description"
        # Files ["test", "Dockerfile", "datmoDockerfile"]

        # 5) Test option 5
        input_dict_1 = {
            "name": "test",
            "description": "test description",
            "definition_paths": [self.definition_filepath],
        }

        environment_obj = self.environment.create(
            input_dict_1, save_hardware_file=False)
        assert environment_obj
        assert isinstance(environment_obj, Environment)
        assert environment_obj.id
        assert environment_obj.driver_type == "docker"
        assert environment_obj.file_collection_id
        assert environment_obj.definition_filename
        assert environment_obj.hardware_info
        assert environment_obj.unique_hash == "93920b84be871138bf219cb73a3a8a3f"
        assert environment_obj.name == "test"
        assert environment_obj.description == "test description"
        # Files ["Dockerfile", "datmoDockerfile"]

        # remove the project environment directory
        shutil.rmtree(self.environment.environment_directory)

        # Create environment definition in root directory
        home_definition_filepath = os.path.join(self.environment.home,
                                                "Dockerfile")
        with open(home_definition_filepath, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        # 2) Test option 2
        environment_obj_1 = self.environment.create(
            input_dict_0, save_hardware_file=False)

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_1.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_1
        assert isinstance(environment_obj_1, Environment)
        assert environment_obj_1.id
        assert environment_obj_1.driver_type == "docker"
        assert environment_obj_1.file_collection_id
        assert environment_obj_1.definition_filename
        assert environment_obj_1.hardware_info
        assert environment_obj_1.unique_hash == file_collection_obj.filehash
        assert environment_obj_1.name == "test"
        assert environment_obj_1.description == "test description"
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert environment_obj_1.unique_hash == "93920b84be871138bf219cb73a3a8a3f"

        # 3) Test option 3
        input_dict_2 = {
            "name": "test",
            "description": "test description",
            "definition_paths": [home_definition_filepath],
        }

        # Create environment in the project
        environment_obj_2 = self.environment.create(
            input_dict_2, save_hardware_file=False)

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_2.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_2
        assert isinstance(environment_obj_2, Environment)
        assert environment_obj_2.id
        assert environment_obj_2.driver_type == "docker"
        assert environment_obj_2.file_collection_id
        assert environment_obj_2.definition_filename
        assert environment_obj_2.hardware_info
        assert environment_obj_2.unique_hash == file_collection_obj.filehash
        assert environment_obj_2.name == "test"
        assert environment_obj_2.description == "test description"
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert environment_obj_2.unique_hash == "93920b84be871138bf219cb73a3a8a3f"

        # 4) Test option 4
        input_dict_3 = {
            "definition_paths": [home_definition_filepath + ">Dockerfile"],
        }

        # Create environment in the project
        environment_obj_3 = self.environment.create(
            input_dict_3, save_hardware_file=False)

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_3.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_3
        assert isinstance(environment_obj_3, Environment)
        assert environment_obj_3.id
        assert environment_obj_3.driver_type == "docker"
        assert environment_obj_3.file_collection_id
        assert environment_obj_3.definition_filename
        assert environment_obj_3.hardware_info
        assert environment_obj_3.unique_hash == file_collection_obj.filehash
        assert environment_obj_3.name == "test"
        assert environment_obj_3.description == "test description"
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert environment_obj_3.unique_hash == "93920b84be871138bf219cb73a3a8a3f"

        # 6) Test option 6
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")

        input_dict = {
            "definition_paths": [
                definition_filepath + ">Dockerfile",
                definition_filepath + ">Dockerfile"
            ],
        }

        # Create environment in the project
        failed = False
        try:
            _ = self.environment.create(input_dict, save_hardware_file=False)
        except FileAlreadyExistsError:
            failed = True

        assert failed

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_build(self):
        # 1) Test build when no environment given
        # 2) Test build when definition path exists and given
        # 3) Test build when NO file exists and definition path exists
        # 4) Test build when file exists and definition path exists
        # 5) Test build when file exists but NO definition path exists
        self.project.init("test5", "test description")
        # 1) Test option 1
        failed = False
        try:
            _ = self.environment.build("does_not_exist")
        except EntityNotFound:
            failed = True
        assert failed

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        input_dict = {
            "definition_paths": [definition_filepath],
        }

        # 2) Test option 2
        # Create environment in the project
        environment_obj_1 = self.environment.create(input_dict)
        result = self.environment.build(environment_obj_1.id)
        assert result

        # 3) Test option 3
        # Create environment in the project
        environment_obj_2 = self.environment.create({})
        result = self.environment.build(environment_obj_2.id)
        assert result

        # Create script to test
        test_filepath = os.path.join(self.environment.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # 4) Test option 4
        environment_obj_3 = self.environment.create({})
        result = self.environment.build(environment_obj_3.id)
        assert result

        # test 2), 3), and 4) will result in the same environment
        assert environment_obj_1.id == environment_obj_2.id
        assert environment_obj_2.id == environment_obj_3.id

        # Test for building dockerfile when there exists not
        os.remove(definition_filepath)

        # 5) Test option 5
        # Create environment definition in project environment directory
        definition_filepath = os.path.join(
            self.environment.environment_directory, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        environment_obj_4 = self.environment.create({})
        result = self.environment.build(environment_obj_4.id)
        assert result

        # teardown
        self.environment.delete(environment_obj_1.id)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # Test run simple command with simple Dockerfile
        self.project.init("test5", "test description")

        # 0) Test option 0
        # Create environment definition in project environment directory
        definition_filepath = os.path.join(
            self.environment.environment_directory, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        random_name = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(32)
        ])
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": random_name,
            "volumes": None,
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": False
        }

        # Create environment in the project
        environment_obj = self.environment.create({})

        log_filepath = os.path.join(self.project.home, "task.log")

        # Build environment in the project
        _ = self.environment.build(environment_obj.id)

        # Run environment in the project
        return_code, run_id, logs = \
            self.environment.run(environment_obj.id, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs

        # teardown
        self.environment.delete(environment_obj.id)
        shutil.rmtree(self.environment.environment_directory)

        # 1) Test option 1
        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        random_name = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(32)
        ])
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": random_name,
            "volumes": None,
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": False
        }

        input_dict = {
            "definition_paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        log_filepath = os.path.join(self.project.home, "task.log")

        # Build environment in the project
        _ = self.environment.build(environment_obj.id)

        # Run environment in the project
        return_code, run_id, logs = \
            self.environment.run(environment_obj.id, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs

        # teardown
        self.environment.delete(environment_obj.id)

        # 2) Test option 2
        os.remove(definition_filepath)

        # Create script to test
        test_filepath = os.path.join(self.environment.home, "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("import sys\n"))
            f.write(to_bytes("print('hello')\n"))

        # Create environment in the project
        environment_obj = self.environment.create({})
        self.environment.build(environment_obj.id)

        random_name = ''.join([
            random.choice(string.ascii_letters + string.digits)
            for _ in range(32)
        ])
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": random_name,
            "volumes": {
                self.environment.home: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            },
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False
        }

        # Run environment in the project
        return_code, run_id, logs = \
            self.environment.run(environment_obj.id, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs

        # teardown
        self.environment.delete(environment_obj.id)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_interactive_run(self):
        # 1) Test run interactive terminal in environment
        # 2) Test run jupyter notebook in environment
        # Create environment definition
        self.project.init("test6", "test description")

        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        input_dict = {
            "definition_filepath": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)
        # 1) Test option 1
        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run):
            run_options = {
                "command": [],
                "ports": ["8888:8888"],
                "name": container_name,
                "volumes": None,
                "detach": True,
                "stdin_open": True,
                "tty": True,
                "api": False
            }

            log_filepath = os.path.join(self.project.home, "task.log")

            # Build environment in the project
            _ = self.environment.build(environment_obj.id)

            # Run environment in the project
            self.environment.run(environment_obj.id, run_options, log_filepath)

            return timed_run

        container_name = str(uuid.uuid1())
        timed_run_result = False
        try:
            timed_run_result = timed_run(container_name, timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

        # teardown
        self.environment.delete(environment_obj.id)

        # 2) Test option 2
        environment_obj = self.environment.create(input_dict)

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run):
            run_options = {
                "command": ["jupyter", "notebook"],
                "ports": ["8888:8888"],
                "name": container_name,
                "volumes": None,
                "detach": True,
                "stdin_open": False,
                "tty": False,
                "api": False
            }

            log_filepath = os.path.join(self.project.home, "task.log")

            # Build environment in the project
            _ = self.environment.build(environment_obj.id)

            # Run environment in the project
            self.environment.run(environment_obj.id, run_options, log_filepath)

            return timed_run

        container_name = str(uuid.uuid1())
        timed_run_result = False
        try:
            timed_run_result = timed_run(container_name, timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

        # Stop the running environment
        # self.environment.stop(container_name)

        # teardown
        self.environment.delete(environment_obj.id)

    def test_list(self):
        self.project.init("test4", "test description")

        # Create environment definition for object 1
        definition_path_1 = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_path_1, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        input_dict_1 = {
            "definition_paths": [definition_path_1],
        }

        # Create environment in the project
        environment_obj_1 = self.environment.create(input_dict_1)

        # Create environment definition for object 2
        definition_path_2 = os.path.join(self.environment.home, "Dockerfile2")
        with open(definition_path_2, "wb") as f:
            f.write(to_bytes(str("FROM datmo/scikit-opencv")))

        input_dict_2 = {
            "definition_paths": [definition_path_2 + ">Dockerfile"],
        }

        # Create second environment in the project
        environment_obj_2 = self.environment.create(input_dict_2)

        # List all environments and ensure they exist
        result = self.environment.list()

        assert len(result) == 2 and \
            environment_obj_1 in result and \
            environment_obj_2 in result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_delete(self):
        self.project.init("test5", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        input_dict = {
            "definition_paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        # Delete environment in the project
        result = self.environment.delete(environment_obj.id)

        # Check if environment retrieval throws error
        thrown = False
        try:
            self.environment.dal.environment.get_by_id(environment_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_failure(self):
        # 1) Test failure with RequiredArgumentMissing
        # 2) Test failure with TooManyArgumentsFound

        # 1) Test option 1
        failed = False
        try:
            self.environment.stop()
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # 2) Test option 2
        failed = False
        try:
            self.environment.stop(run_id="hello", match_string="there")
        except TooManyArgumentsFound:
            failed = True
        assert failed

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_success(self):
        # TODO: test more run options
        # 1) Test run_id input to stop
        # 2) Test match_string input to stop
        # 3) Test all input to stop
        self.project.init("test5", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": "datmo-task-" + self.environment.model.id + "-" + "test",
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False
        }

        # Create environment definition
        env_def_path = os.path.join(self.project.home, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

        input_dict = {
            "definition_paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        log_filepath = os.path.join(self.project.home, "task.log")

        # Build environment in the project
        _ = self.environment.build(environment_obj.id)

        # 1) Test option 1

        _, run_id, _ = \
            self.environment.run(environment_obj.id, run_options, log_filepath)
        return_code = self.environment.stop(run_id=run_id)

        assert return_code

        # 2) Test option 2
        _, _, _ = \
            self.environment.run(environment_obj.id, run_options, log_filepath)
        return_code = self.environment.stop(
            match_string="datmo-task-" + self.environment.model.id)

        assert return_code

        # 3) Test option 3
        _, _, _ = \
            self.environment.run(environment_obj.id, run_options, log_filepath)
        run_options_2 = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": "datmo-task-" + self.environment.model.id + "-" + "test2",
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False
        }
        _, _, _ = \
            self.environment.run(environment_obj.id, run_options_2, log_filepath)
        return_code = self.environment.stop(all=True)

        assert return_code

        # teardown
        self.environment.delete(environment_obj.id)

    def test_exists_env(self):
        # Test failure, not initialized
        failed = False
        try:
            _ = self.environment.create({})
        except:
            failed = True
        assert failed

        # Setup
        self.__setup()
        environment_obj = self.environment.create({})

        # Check by environment id
        result = self.environment.exists(environment_id=environment_obj.id)
        assert result

        # Check by unique hash
        result = self.environment.exists(
            environment_unique_hash=environment_obj.unique_hash)
        assert result

        # Test with wrong environment id
        result = self.environment.exists(environment_id='test_wrong_env_id')
        assert not result

    def test_calculate_project_environment_hash(self):
        # Setup
        self.__setup()
        # Test hashing the default (with hardware info)
        result = self.environment._calculate_project_environment_hash()
        assert result
        # Test hashing the default Dockerfile
        result = self.environment._calculate_project_environment_hash(
            save_hardware_file=False)
        assert result == "d4e62871c1e6033bf3d045f91107fafe"
        # Test if hash is the same as that of create
        environment_obj = self.environment.create({}, save_hardware_file=False)
        result = self.environment._calculate_project_environment_hash(
            save_hardware_file=False)
        assert result == "d4e62871c1e6033bf3d045f91107fafe"
        assert result == environment_obj.unique_hash

        # Test if the hash is the same if the same file is passed in as an input
        input_dict = {"definition_path": self.definition_filepath}
        environment_obj_1 = self.environment.create(
            input_dict, save_hardware_file=False)
        result = self.environment._calculate_project_environment_hash(
            save_hardware_file=False)
        assert result == "d4e62871c1e6033bf3d045f91107fafe"
        assert result == environment_obj_1.unique_hash

    def test_has_unstaged_changes(self):
        # Setup
        self.__setup()
        obj = self.environment.create({})
        # Check for no unstaged changes
        result = self.environment._has_unstaged_changes()
        assert not result

        with open(
                os.path.join(self.environment.environment_directory,
                             "Dockerfile"), "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu\n"))

        result = self.environment._has_unstaged_changes()
        assert result

    def test_check_unstaged_changes(self):
        # Setup
        self.__setup()
        obj = self.environment.create({})

        # 1) After commiting the changes
        # Check for no unstaged changes because already committed
        result = self.environment.check_unstaged_changes()
        assert not result

        # Add a new file
        with open(
                os.path.join(self.environment.environment_directory, "test2"),
                "wb") as f:
            f.write(to_bytes("cool"))

        # 2) Not commiting the changes, should error and raise UnstagedChanges
        failed = False
        try:
            self.environment.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # Remove new file
        os.remove(
            os.path.join(self.environment.environment_directory, "test2"))

        # 3) Files are the same as before but no new commit, should have no unstaged changes
        result = self.environment.check_unstaged_changes()
        assert not result

        # 4) Remove another file, now it is different and should have unstaged changes
        os.remove(os.path.join(self.environment.environment_directory, "test"))
        failed = False
        try:
            self.environment.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # 5) Remove the rest of the files, now it is empty and should return as already staged
        os.remove(
            os.path.join(self.environment.environment_directory, "Dockerfile"))
        result = self.environment.check_unstaged_changes()
        assert not result

    def test_checkout(self):
        # Setup and create all environment files
        self.__setup()

        # Create environment to checkout to with defaults
        environment_obj = self.environment.create({})

        # Checkout success with there are no unstaged changes
        result = self.environment.checkout(environment_obj.id)
        assert result
        current_hash = self.environment._calculate_project_environment_hash()
        assert environment_obj.unique_hash == current_hash
        # Check the filenames as well because the hash does not take this into account
        assert os.path.isfile(
            os.path.join(self.environment.environment_directory, "test"))
        assert os.path.isfile(
            os.path.join(self.environment.environment_directory, "Dockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment.environment_directory,
                         "datmoDockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment.environment_directory,
                         "hardware_info"))

        # Change file contents to make it unstaged
        with open(self.definition_filepath, "wb") as f:
            f.write(to_bytes("new content"))

        # Checkout failure with unstaged changes
        failed = False
        try:
            _ = self.environment.checkout(environment_obj.id)
        except UnstagedChanges:
            failed = True
        assert failed

        # Create new environment to checkout to with defaults (no hardware)
        environment_obj_1 = self.environment.create(
            {}, save_hardware_file=False)

        # Checkout success with there are no unstaged changes
        result = self.environment.checkout(environment_obj.id)
        assert result
        current_hash = self.environment._calculate_project_environment_hash()
        assert environment_obj.unique_hash == current_hash
        assert environment_obj_1.unique_hash != current_hash
        # Check the filenames as well because the hash does not take this into account
        assert os.path.isfile(
            os.path.join(self.environment.environment_directory, "test"))
        assert os.path.isfile(
            os.path.join(self.environment.environment_directory, "Dockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment.environment_directory,
                         "datmoDockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment.environment_directory,
                         "hardware_info"))
