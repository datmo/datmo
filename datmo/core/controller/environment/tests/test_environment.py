"""
Tests for EnvironmentController
"""
import os
import uuid
import random
import string
import tempfile
import platform
import timeout_decorator
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import \
    EnvironmentController
from datmo.core.util.exceptions import (
    EntityNotFound, EnvironmentDoesNotExist, RequiredArgumentMissing,
    TooManyArgumentsFound)
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
        with open(os.path.join(self.temp_dir, "test.txt"), "w") as f:
            f.write("hello")
        datmo_path_environment = os.path.join(self.temp_dir, "datmo_environment")
        if not os.path.exists(datmo_path_environment):
            os.makedirs(datmo_path_environment)
        with open(
                os.path.join(self.temp_dir, "datmo_environment", "test"),
                "w") as f:
            f.write("cool")
        datmo_path_files = os.path.join(self.temp_dir, "datmo_files")
        if not os.path.exists(datmo_path_files):
            os.makedirs(datmo_path_files)
        with open(os.path.join(self.temp_dir, "datmo_files", "test"),
                  "w") as f:
            f.write("man")


    def test_create(self):
        # 0) Test create when unsupported language given
        # 1) Test create when NO file exists and NO definition path exists
        # 2) Test create when NO file exists and definition path exists
        # 3) Test create when definition path exists and given
        # 4) Test create when file exists and definition path exists
        # 5) Test create when file exists but NO definition path exists
        # 6) Test create when definition path exists and given for NEW definition filepath

        self.project.init("test3", "test description")

        # 0) Test option 0
        try:
            self.environment.create({"language": "java"})
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        # 1) Test option 1
        # Creates environment with python3 based docker image
        environment_obj_0 = self.environment.create({})
        assert environment_obj_0
        assert environment_obj_0.id
        assert environment_obj_0.driver_type == "docker"
        assert environment_obj_0.file_collection_id
        assert environment_obj_0.definition_filename
        assert environment_obj_0.hardware_info

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # 2) Test option 2
        environment_obj_1 = self.environment.create({})

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_1.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_1
        assert environment_obj_1.id
        assert environment_obj_1.driver_type == "docker"
        assert environment_obj_1.file_collection_id
        assert environment_obj_1.definition_filename
        assert environment_obj_1.hardware_info
        assert environment_obj_1.unique_hash == file_collection_obj.filehash
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))

        # 3) Test option 3
        input_dict = {
            "definition_filepath": definition_filepath,
        }

        # Create environment in the project
        environment_obj_2 = self.environment.create(input_dict)

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_2.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_2
        assert environment_obj_2.id
        assert environment_obj_2.driver_type == "docker"
        assert environment_obj_2.file_collection_id
        assert environment_obj_2.definition_filename
        assert environment_obj_2.hardware_info
        assert environment_obj_2.unique_hash == file_collection_obj.filehash
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))

        # Create script to test
        test_filepath = os.path.join(self.environment.home, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print('hello')\n"))

        # 4) Test option 4
        environment_obj_3 = self.environment.create({})

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_3.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_3
        assert environment_obj_3.id
        assert environment_obj_3.driver_type == "docker"
        assert environment_obj_3.file_collection_id
        assert environment_obj_3.definition_filename
        assert environment_obj_3.hardware_info
        assert environment_obj_3.unique_hash == file_collection_obj.filehash
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))

        # Remove definition filepath
        os.remove(definition_filepath)

        assert environment_obj_1.id == environment_obj_2.id
        assert environment_obj_2.id == environment_obj_3.id

        # 5) Test option 5
        environment_obj_4 = self.environment.create({})

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_4.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_4
        assert environment_obj_4.id
        assert environment_obj_4.driver_type == "docker"
        assert environment_obj_4.file_collection_id
        assert environment_obj_4.definition_filename
        assert environment_obj_4.hardware_info
        assert environment_obj_4.unique_hash == file_collection_obj.filehash
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmorequirements.txt"))
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))

        assert environment_obj_1.id != environment_obj_4.id

        # 6) Test option 6

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM cloudgear/ubuntu:14.04")))

        input_dict = {
            "definition_filepath": definition_filepath,
        }

        # Create a new environment obj
        environment_obj_5 = self.environment.create(input_dict)

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection. \
            get_by_id(environment_obj_5.file_collection_id)
        file_collection_dir = self.environment.file_driver. \
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj_5
        assert environment_obj_5.id
        assert environment_obj_5.driver_type == "docker"
        assert environment_obj_5.file_collection_id
        assert environment_obj_5.definition_filename
        assert environment_obj_5.hardware_info
        assert environment_obj_5.unique_hash == file_collection_obj.filehash
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))

        assert environment_obj_5.id != environment_obj_1.id
        assert environment_obj_5.id != environment_obj_4.id

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
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))
        input_dict = {
            "definition_filepath": definition_filepath,
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
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print('hello')\n"))

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
        environment_obj_4 = self.environment.create({})
        result = self.environment.build(environment_obj_4.id)
        assert result
        assert environment_obj_4.id != environment_obj_1.id

        # teardown
        self.environment.delete(environment_obj_1.id)
        self.environment.delete(environment_obj_4.id)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # 1) Test run simple command with simple Dockerfile
        self.project.init("test5", "test description")

        # 1) Test option 1

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

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
            "definition_filepath": definition_filepath,
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
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print('hello')\n"))

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
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        input_dict = {
            "definition_filepath": definition_filepath,
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
        with open(definition_path_1, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        input_dict_1 = {
            "definition_filepath": definition_path_1,
        }

        # Create environment in the project
        environment_obj_1 = self.environment.create(input_dict_1)

        # Create environment definition for object 2
        definition_path_2 = os.path.join(self.environment.home, "Dockerfile2")
        with open(definition_path_2, "w") as f:
            f.write(to_unicode(str("FROM datmo/scikit-opencv")))

        input_dict_2 = {
            "definition_filepath": definition_path_2,
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
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        input_dict = {
            "definition_filepath": definition_filepath,
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
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

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
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        input_dict = {
            "definition_filepath": definition_filepath,
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
        result = self.environment.exists(environment_unique_hash=environment_obj.unique_hash)
        assert result

        # Test with wrong environment id
        result = self.environment.exists(environment_id='test_wrong_env_id')
        assert not result

    def test_calculate_environment_hash(self):
        # Setup
        self.__setup()
        self.environment.create({})
        assert self.environment._calculate_environment_hash() == '03c44e04cdb4bb7f9da53f4b88c164ba'

        environment_def_path = os.path.join(self.temp_dir, "datmo_environment", "Dockerfile")
        with open(environment_def_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu\n")

        environment_obj_0 = self.environment.create({})

        environment_obj_1 = self.environment.create({"definition_filepath": environment_def_path})

        # TODO: Fix this test
        #assert environment_obj_0 == environment_obj_1
        # assert environment_obj_0.id == environment_obj_1.id
        # assert environment_obj_0.unique_hash == environment_obj_1.unique_hash

    def test_has_unstaged_changes(self):

        # Setup
        # self.__setup()
        # obj = self.environment.create({})

        # TODO: Fix this test after merging PR from environment
        # # Check for no unstaged changes
        # result = self.environment._has_unstaged_changes()
        # assert not result
        #
        # with open(
        #         os.path.join(self.temp_dir, "datmo_environment", "Dockerfile"),
        #         "w") as f:
        #     f.write("FROM datmo/xgboost:cpu\n")
        #
        # result = self.environment._has_unstaged_changes()
        # assert result
        pass

    def test_check_unstaged_changes(self):
        # Setup
        self.__setup()
        obj = self.environment.create({})

        # 1) After commiting the changes
        # Check for no unstaged changes
        result = self.environment.check_unstaged_changes()
        assert not result

        with open(
                os.path.join(self.temp_dir, "datmo_environment", "Dockerfile"),
                "w") as f:
            f.write("FROM datmo/xgboost:cpu\n")

        # TODO: Fix this test after merging PR from environment
        # 2) Not commiting the changes
        # result = self.environment._has_unstaged_changes()
        # assert result

    def test_checkout_env(self):
        # Setup
        self.__setup()
        environment_obj = self.environment.create({})
        # After committing the environment, make a checkout
        result = self.environment.checkout(environment_obj.id)
        assert result

        # TODO: After making changes in `datmo_environment` make a checkout experiment





