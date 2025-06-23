"""
Tests for EnvironmentController
"""
import os
import uuid
import threading
import tempfile
import platform
import timeout_decorator
from io import open
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
from datmo.core.controller.environment.environment import \
    EnvironmentController
from datmo.core.entity.environment import Environment
from datmo.core.util.exceptions import (
    EntityNotFound, RequiredArgumentMissing, TooManyArgumentsFound,
    FileAlreadyExistsError, UnstagedChanges, EnvironmentDoesNotExist,
    ProjectNotInitialized)
from datmo.core.util.misc_functions import check_docker_inactive, pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestEnvironmentController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.project_controller = ProjectController()
        self.environment_ids = []

    def teardown_method(self):
        if not check_docker_inactive(test_datmo_dir,
                                     Config().datmo_directory_name):
            if self.project_controller.is_initialized:
                self.environment_controller = EnvironmentController()
                for env_id in list(set(self.environment_ids)):
                    if not self.environment_controller.delete(env_id):
                        raise Exception

    def __setup(self):
        self.project_controller.init("test_setup", "test description")
        self.environment_controller = EnvironmentController()
        with open(os.path.join(self.temp_dir, "test.txt"), "wb") as f:
            f.write(to_bytes("hello"))
        self.random_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "test")
        with open(self.random_filepath, "wb") as f:
            f.write(to_bytes("cool"))
        self.definition_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "Dockerfile")
        with open(self.definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

    def test_init_fail_project_not_init(self):
        Config().set_home(self.temp_dir)
        failed = False
        try:
            EnvironmentController()
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_get_environment_type(self):
        self.__setup()
        result = self.environment_controller.get_environment_types()
        assert result

    def test_get_supported_environments(self):
        self.__setup()
        environment_type = "cpu"
        result = self.environment_controller.get_supported_frameworks(
            environment_type)
        assert result

    def test_get_supported_languages(self):
        self.__setup()
        environment_type = "cpu"
        environment_name = "data-analytics"
        result = self.environment_controller.get_supported_languages(
            environment_type, environment_name)
        assert result

    def test_setup(self):
        # TODO: Run all environment options and test if success
        self.project_controller.init("test_setup", "test description")
        self.environment_controller = EnvironmentController()

        # Test success setup once (no files present)
        options = {
            "environment_framework": "data-analytics",
            "environment_type": "cpu",
            "environment_language": "py27"
        }
        result = self.environment_controller.setup(options=options)
        output_definition_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "Dockerfile")

        assert isinstance(result, Environment)
        assert result.name == "%s:%s-%s" % (options['environment_framework'],
                                            options['environment_type'],
                                            options['environment_language'])
        assert result.description == "supported environment created by datmo"
        assert os.path.isfile(output_definition_filepath)
        assert "FROM datmo/data-analytics:cpu-py27" in open(
            output_definition_filepath, "r").read()
        # Test success setup again (files present, but staged)
        options = {
            "environment_framework": "data-analytics",
            "environment_type": "cpu",
            "environment_language": "py27"
        }
        result = self.environment_controller.setup(options=options)
        output_definition_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "Dockerfile")

        assert isinstance(result, Environment)
        assert result.name == "%s:%s-%s" % (options['environment_framework'],
                                            options['environment_type'],
                                            options['environment_language'])
        assert result.description == "supported environment created by datmo"
        assert os.path.isfile(output_definition_filepath)
        assert "FROM datmo/data-analytics:cpu-py27" in open(
            output_definition_filepath, "r").read()

        # Test failure in downstream function (e.g. bad inputs, no name given)
        failed = False
        try:
            self.environment_controller.setup(options={})
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        # Change environment file
        with open(output_definition_filepath, "wb") as f:
            f.write(to_bytes("new content"))

        # Test failure setup (unstaged changes)
        failed = False
        try:
            self.environment_controller.setup(options=options)
        except UnstagedChanges:
            failed = True
        assert failed

    def test_current_environment(self):
        self.__setup()
        # Test failure with unstaged changes
        failed = False
        try:
            self.environment_controller.current_environment()
        except UnstagedChanges:
            failed = True
        assert failed
        # Test successful current environment
        input_dict = {"name": "test", "description": "test description"}
        environment_obj = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj.id)
        current_environment_obj = self.environment_controller.current_environment(
        )
        assert current_environment_obj == environment_obj

    def test_create(self):
        # 0) Test SUCCESS create when definition path exists in project environment directory (no input, no root) -- with hardware file
        # 1) Test SUCCESS create when definition path exists in project environment directory (no input, no root)
        # 5) Test SUCCESS when definition path exists in project environment directory and passed from input dict (takes input)
        # 2) Test SUCCESS create when definition path exists in root project folder (no input, no project environment dir)
        # 3) Test SUCCESS create when definition path is passed into input dict (takes input, no project environment dir)
        # 4) Test SUCCESS create when definition path is passed into input dict along with expected filename to be saved
        # 6) Test FAIL when passing same filepath with same filename into input dict

        self.__setup()

        input_dict_0 = {"name": "test", "description": "test description"}

        # 0) Test option 0 (cannot test hash because hardware is machine-dependent)
        environment_obj_0 = self.environment_controller.create(input_dict_0)
        self.environment_ids.append(environment_obj_0.id)
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
        file_collection_obj = self.environment_controller.dal.file_collection. \
            get_by_id(environment_obj_0.file_collection_id)
        file_collection_dir = self.environment_controller.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert os.path.isfile(os.path.join(file_collection_dir, "test"))
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        output = open(os.path.join(file_collection_dir, "Dockerfile"),
                      "r").read()
        print(repr(output))
        assert os.path.isfile(
            os.path.join(file_collection_dir, "hardware_info"))
        output = open(os.path.join(file_collection_dir, "hardware_info"),
                      "r").read()
        print(repr(output))

        # 1) Test option 1
        environment_obj_0 = self.environment_controller.create(
            input_dict_0, save_hardware_file=False)
        self.environment_ids.append(environment_obj_0.id)
        assert environment_obj_0
        assert isinstance(environment_obj_0, Environment)
        assert environment_obj_0.id
        assert environment_obj_0.driver_type == "docker"
        assert environment_obj_0.file_collection_id
        assert environment_obj_0.definition_filename
        assert environment_obj_0.hardware_info
        # Get file collection path
        file_collection_obj = self.environment_controller.dal.file_collection. \
            get_by_id(environment_obj_0.file_collection_id)
        file_collection_dir = self.environment_controller.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert os.path.isfile(os.path.join(file_collection_dir, "test"))
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        output = open(os.path.join(file_collection_dir, "Dockerfile"),
                      "r").read()
        print(repr(output))
        assert environment_obj_0.unique_hash == "1e32ff083520f792cbe4bafdc2de2a01"
        assert environment_obj_0.name == "test"
        assert environment_obj_0.description == "test description"
        # Files ["test", "Dockerfile"]

        # 5) Test option 5
        input_dict_1 = {
            "name": "test",
            "description": "test description",
            "paths": [self.definition_filepath],
        }

        environment_obj = self.environment_controller.create(
            input_dict_1, save_hardware_file=False)
        self.environment_ids.append(environment_obj.id)
        assert environment_obj
        assert isinstance(environment_obj, Environment)
        assert environment_obj.id
        assert environment_obj.driver_type == "docker"
        assert environment_obj.file_collection_id
        assert environment_obj.definition_filename
        assert environment_obj.hardware_info
        # Get file collection path
        file_collection_obj = self.environment_controller.dal.file_collection. \
            get_by_id(environment_obj.file_collection_id)
        file_collection_dir = self.environment_controller.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        output = open(os.path.join(file_collection_dir, "Dockerfile"),
                      "r").read()
        print(repr(output))
        assert not os.path.isfile(
            os.path.join(file_collection_dir, "datmoDockerfile"))
        print(repr(output))
        assert environment_obj.unique_hash == "fd725be022ce93f870c81e2ee170189c"
        assert environment_obj.name == "test"
        assert environment_obj.description == "test description"
        # Files ["Dockerfile"]

        # remove the project environment directory
        os.remove(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "Dockerfile"))
        os.remove(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "test"))

        # Create environment definition in root directory
        home_definition_filepath = os.path.join(
            self.environment_controller.home, "Dockerfile")
        with open(home_definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # 2) Test option 2
        environment_obj_1 = self.environment_controller.create(
            input_dict_0, save_hardware_file=False)
        self.environment_ids.append(environment_obj_1.id)
        assert environment_obj_1
        assert isinstance(environment_obj_1, Environment)
        assert environment_obj_1.id
        assert environment_obj_1.driver_type == "docker"
        assert environment_obj_1.file_collection_id
        assert environment_obj_1.definition_filename
        assert environment_obj_1.hardware_info
        assert environment_obj_1.unique_hash == file_collection_obj.filehash
        # Get file collection path
        file_collection_obj = self.environment_controller.dal.file_collection. \
            get_by_id(environment_obj_1.file_collection_id)
        file_collection_dir = self.environment_controller.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert environment_obj_1.name == "test"
        assert environment_obj_1.description == "test description"
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert environment_obj_1.unique_hash == "fd725be022ce93f870c81e2ee170189c"

        # 3) Test option 3
        input_dict_2 = {
            "name": "test",
            "description": "test description",
            "paths": [home_definition_filepath],
        }

        # Create environment in the project
        environment_obj_2 = self.environment_controller.create(
            input_dict_2, save_hardware_file=False)
        self.environment_ids.append(environment_obj_2.id)
        assert environment_obj_2
        assert isinstance(environment_obj_2, Environment)
        assert environment_obj_2.id
        assert environment_obj_2.driver_type == "docker"
        assert environment_obj_2.file_collection_id
        assert environment_obj_2.definition_filename
        assert environment_obj_2.hardware_info
        assert environment_obj_2.unique_hash == file_collection_obj.filehash
        # Get file collection path
        file_collection_obj = self.environment_controller.dal.file_collection. \
            get_by_id(environment_obj_2.file_collection_id)
        file_collection_dir = self.environment_controller.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert environment_obj_2.name == "test"
        assert environment_obj_2.description == "test description"
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert environment_obj_2.unique_hash == "fd725be022ce93f870c81e2ee170189c"

        # 4) Test option 4
        input_dict_3 = {
            "paths": [home_definition_filepath + ">Dockerfile"],
        }

        # Create environment in the project
        environment_obj_3 = self.environment_controller.create(
            input_dict_3, save_hardware_file=False)
        self.environment_ids.append(environment_obj_3.id)
        assert environment_obj_3
        assert isinstance(environment_obj_3, Environment)
        assert environment_obj_3.id
        assert environment_obj_3.driver_type == "docker"
        assert environment_obj_3.file_collection_id
        assert environment_obj_3.definition_filename
        assert environment_obj_3.hardware_info
        assert environment_obj_3.unique_hash == file_collection_obj.filehash
        # Get file collection path
        file_collection_obj = self.environment_controller.dal.file_collection. \
            get_by_id(environment_obj_3.file_collection_id)
        file_collection_dir = self.environment_controller.file_driver. \
            get_collection_path(file_collection_obj.filehash)
        assert environment_obj_3.name == "test"
        assert environment_obj_3.description == "test description"
        assert os.path.isfile(os.path.join(file_collection_dir, "Dockerfile"))
        assert environment_obj_3.unique_hash == "fd725be022ce93f870c81e2ee170189c"

        # 6) Test option 6
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")

        input_dict = {
            "paths": [
                definition_filepath + ">Dockerfile",
                definition_filepath + ">Dockerfile"
            ],
        }

        # Create environment in the project
        failed = False
        try:
            _ = self.environment_controller.create(
                input_dict, save_hardware_file=False)
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
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()
        # 1) Test option 1
        failed = False
        try:
            _ = self.environment_controller.build("does_not_exist")
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        # Create environment definition
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))
        input_dict = {
            "paths": [definition_filepath],
        }

        # 2) Test option 2
        # Create environment in the project
        environment_obj_1 = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj_1.id)
        result = self.environment_controller.build(environment_obj_1.id)
        assert result

        # 3) Test option 3
        # Create environment in the project
        environment_obj_2 = self.environment_controller.create({})
        result = self.environment_controller.build(environment_obj_2.id)
        assert result

        # Create script to test
        test_filepath = os.path.join(self.environment_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
            f.write(to_bytes("print('hello')\n"))

        # 4) Test option 4
        environment_obj_3 = self.environment_controller.create({})
        result = self.environment_controller.build(environment_obj_3.id)
        assert result

        # test 2), 3), and 4) will result in the same environment
        assert environment_obj_1.id == environment_obj_2.id
        assert environment_obj_2.id == environment_obj_3.id

        # Test for building dockerfile when there exists not
        os.remove(definition_filepath)

        # 5) Test option 5
        # Create environment definition in project environment directory
        definition_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))
        environment_obj_4 = self.environment_controller.create({})
        self.environment_ids.append(environment_obj_4.id)
        result = self.environment_controller.build(environment_obj_4.id)
        assert result

        # 6) Test option 6
        # Create environment definition in project environment directory with datmo base image
        definition_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(
                to_bytes("FROM datmo/data-analytics:cpu-py27%s" % os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))
        environment_obj_4 = self.environment_controller.create({})
        self.environment_ids.append(environment_obj_4.id)
        result = self.environment_controller.build(
            environment_obj_4.id, workspace="notebook")
        assert result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_extract_workspace_url(self):
        # Create environment definition
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(
                to_bytes(
                    "FROM datmo/python-base:cpu-py27-notebook" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))

        image_name = "test"
        input_dict = {"name": image_name, "description": "test description"}
        # Create environment in the project
        environment_obj = self.environment_controller.create(
            input_dict, save_hardware_file=False)
        self.environment_controller.build(environment_obj.id)

        # Test when there is no container being run
        workspace_url = self.environment_controller.extract_workspace_url(
            image_name, "notebook")
        assert workspace_url == None

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # Test run simple command with simple Dockerfile
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()

        # 0) Test option 0
        # Create environment definition in project environment directory
        definition_filepath = os.path.join(
            self.environment_controller.environment_driver.
            environment_directory_path, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))

        random_name = str(uuid.uuid1())
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": random_name,
            "volumes": None,
            "detach": True,
            "stdin_open": False,
            "mem_limit": "4g",
            "tty": False,
            "api": False
        }

        # Create environment in the project
        environment_obj = self.environment_controller.create({})
        self.environment_ids.append(environment_obj.id)
        log_filepath = os.path.join(self.project_controller.home, "task.log")

        # Build environment in the project
        _ = self.environment_controller.build(environment_obj.id)

        # Run environment in the project
        return_code, run_id, logs = \
            self.environment_controller.run(environment_obj.id, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs
        # remove Dockerfile
        os.remove(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "Dockerfile"))

        # 1) Test option 1
        # Create environment definition
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))

        random_name = str(uuid.uuid1())
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8889:8889"],
            "name": random_name,
            "volumes": None,
            "mem_limit": "4g",
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": False
        }

        input_dict = {
            "paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj.id)
        log_filepath = os.path.join(self.project_controller.home, "task.log")

        # Build environment in the project
        _ = self.environment_controller.build(environment_obj.id)

        # Run environment in the project
        return_code, run_id, logs = \
            self.environment_controller.run(environment_obj.id, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs

        # 2) Test option 2
        os.remove(definition_filepath)

        # Create script to test
        test_filepath = os.path.join(self.environment_controller.home,
                                     "script.py")
        with open(test_filepath, "wb") as f:
            f.write(to_bytes("import os\n"))
            f.write(to_bytes("import sys\n"))
            f.write(to_bytes("print('hello')\n"))

        # Create environment in the project
        environment_obj = self.environment_controller.create({})
        self.environment_ids.append(environment_obj.id)
        self.environment_controller.build(environment_obj.id)

        random_name = str(uuid.uuid1())
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8899:8899"],
            "name": random_name,
            "volumes": {
                self.environment_controller.home: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            },
            "mem_limit": "4g",
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False
        }

        # Run environment in the project
        return_code, run_id, logs = \
            self.environment_controller.run(environment_obj.id, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_interactive_run(self):
        # 1) Test run interactive terminal in environment
        # 2) Test run jupyter notebook in environment
        # Create environment definition
        self.project_controller.init("test6", "test description")
        self.environment_controller = EnvironmentController()

        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "wb") as f:
            f.write(
                to_bytes("FROM nbgallery/jupyter-alpine:latest" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))

        input_dict = {
            "paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj.id)
        # 1) Test option 1
        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run):
            run_options = {
                "command": [],
                "ports": ["8889:8889"],
                "name": environment_obj.id + "-" + container_name,
                "volumes": None,
                "mem_limit": "4g",
                "detach": True,
                "stdin_open": True,
                "tty": True,
                "api": False
            }

            log_filepath = os.path.join(self.project_controller.home,
                                        "task.log")

            # Build environment in the project
            _ = self.environment_controller.build(environment_obj.id)

            # Run environment in the project
            self.environment_controller.run(environment_obj.id, run_options,
                                            log_filepath)

            return timed_run

        container_name = str(uuid.uuid1())
        timed_run_result = False
        try:
            timed_run_result = timed_run(container_name, timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

        # 2) Test option 2
        environment_obj = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj.id)

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run):
            run_options = {
                "command": ["jupyter", "notebook", "--allow-root"],
                "ports": ["8888:8888"],
                "name": environment_obj.id + "-" + container_name,
                "volumes": None,
                "mem_limit": "4g",
                "detach": True,
                "stdin_open": False,
                "tty": False,
                "api": False
            }

            log_filepath = os.path.join(self.project_controller.home,
                                        "task.log")

            # Build environment in the project
            _ = self.environment_controller.build(environment_obj.id)

            # Run environment in the project
            self.environment_controller.run(environment_obj.id, run_options,
                                            log_filepath)

            return timed_run

        container_name = str(uuid.uuid1())
        timed_run_result = False
        try:
            timed_run_result = timed_run(container_name, timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

    def test_list(self):
        self.project_controller.init("test4", "test description")
        self.environment_controller = EnvironmentController()

        # Create environment definition for object 1
        definition_path_1 = os.path.join(self.environment_controller.home,
                                         "Dockerfile")
        with open(definition_path_1, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        input_dict_1 = {
            "paths": [definition_path_1],
        }

        # Create environment in the project
        environment_obj_1 = self.environment_controller.create(input_dict_1)
        self.environment_ids.append(environment_obj_1.id)
        # Create environment definition for object 2
        definition_path_2 = os.path.join(self.environment_controller.home,
                                         "Dockerfile2")
        with open(definition_path_2, "wb") as f:
            f.write(to_bytes("FROM python:3.4-alpine"))

        input_dict_2 = {
            "paths": [definition_path_2 + ">Dockerfile"],
        }

        # Create second environment in the project
        environment_obj_2 = self.environment_controller.create(input_dict_2)
        self.environment_ids.append(environment_obj_2.id)
        # List all environments and ensure they exist
        result = self.environment_controller.list()

        assert len(result) == 2 and \
            environment_obj_1 in result and \
            environment_obj_2 in result

    def test_update(self):
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()

        # Create environment definition
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        input_dict = {
            "paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj.id)
        # Test success update
        new_name = "test name"
        new_description = "test description"
        result = self.environment_controller.update(
            environment_obj.id, name=new_name, description=new_description)
        assert result
        assert isinstance(result, Environment)
        assert result.name == new_name
        assert result.description == new_description

        # Test failed update
        failed = False
        try:
            self.environment_controller.update(
                "random_id", name=new_name, description=new_description)
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_delete(self):
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()

        # Create environment definition
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        input_dict = {
            "paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment_controller.create(input_dict)

        # Delete environment in the project
        result = self.environment_controller.delete(environment_obj.id)

        # Check if environment retrieval throws error
        thrown = False
        try:
            self.environment_controller.dal.environment.get_by_id(
                environment_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_failure(self):
        # 1) Test failure with RequiredArgumentMissing
        # 2) Test failure with TooManyArgumentsFound
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()
        # 1) Test option 1
        failed = False
        try:
            self.environment_controller.stop()
        except RequiredArgumentMissing:
            failed = True
        assert failed

        # 2) Test option 2
        failed = False
        try:
            self.environment_controller.stop(
                run_id="hello", match_string="there")
        except TooManyArgumentsFound:
            failed = True
        assert failed

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_success(self):
        # TODO: test more run options
        # 1) Test run_id input to stop
        # 2) Test match_string input to stop
        # 3) Test all input to stop
        # 4) Test if the image was removed by stop
        self.project_controller.init("test5", "test description")
        self.environment_controller = EnvironmentController()

        # Create environment definition
        definition_filepath = os.path.join(self.environment_controller.home,
                                           "Dockerfile")
        with open(definition_filepath, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name":
                "datmo-task-" + self.environment_controller.model.id + "-" +
                "test",
            "volumes":
                None,
            "mem_limit":
                "4g",
            "detach":
                False,
            "stdin_open":
                False,
            "tty":
                False,
            "api":
                False
        }

        # Create environment definition
        env_def_path = os.path.join(self.project_controller.home, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + os.linesep))
            f.write(to_bytes(str("RUN echo " + random_text)))

        input_dict = {
            "paths": [definition_filepath],
        }

        # Create environment in the project
        environment_obj = self.environment_controller.create(input_dict)
        self.environment_ids.append(environment_obj.id)
        log_filepath = os.path.join(self.project_controller.home, "task.log")

        # Build environment in the project
        _ = self.environment_controller.build(environment_obj.id)

        # 1) Test option 1

        _, run_id, _ = \
            self.environment_controller.run(environment_obj.id, run_options, log_filepath)
        return_code = self.environment_controller.stop(run_id=run_id)

        assert return_code

        # 2) Test option 2

        # Rebuild environment in the project
        _ = self.environment_controller.build(environment_obj.id)

        _, _, _ = \
            self.environment_controller.run(environment_obj.id, run_options, log_filepath)
        return_code = self.environment_controller.stop(
            match_string="datmo-task-" + self.environment_controller.model.id)

        assert return_code

        # 3) Test option 3

        # Rebuild environment in the project
        _ = self.environment_controller.build(environment_obj.id)
        _, _, _ = \
            self.environment_controller.run(environment_obj.id, run_options, log_filepath)
        run_options_2 = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8889:8889"],
            "name":
                "datmo-task-" + self.environment_controller.model.id + "-" +
                "test2",
            "volumes":
                None,
            "mem_limit":
                "4g",
            "detach":
                False,
            "stdin_open":
                False,
            "tty":
                False,
            "api":
                False
        }
        _, _, _ = \
            self.environment_controller.run(environment_obj.id, run_options_2, log_filepath)
        return_code = self.environment_controller.stop(all=True)

        assert return_code

    def test_exists(self):
        # Test failure, not initialized
        failed = False
        try:
            _ = self.environment_controller.create({})
        except:
            failed = True
        assert failed

        # Setup
        self.__setup()
        environment_obj = self.environment_controller.create({})
        self.environment_ids.append(environment_obj.id)
        # Check by environment id
        result = self.environment_controller.exists(
            environment_id=environment_obj.id)
        assert result

        # Check by unique hash
        result = self.environment_controller.exists(
            environment_unique_hash=environment_obj.unique_hash)
        assert result

        # Test with wrong environment id
        result = self.environment_controller.exists(
            environment_id='test_wrong_env_id')
        assert not result

    def test_calculate_project_environment_hash(self):
        # Setup
        self.__setup()
        # Test hashing the default (with hardware info)
        result = self.environment_controller._calculate_project_environment_hash(
        )
        assert result
        # Test hashing the default Dockerfile
        result = self.environment_controller._calculate_project_environment_hash(
            save_hardware_file=False)
        assert result == "1e32ff083520f792cbe4bafdc2de2a01"
        # Test if hash is the same as that of create
        environment_obj = self.environment_controller.create(
            {}, save_hardware_file=False)
        self.environment_ids.append(environment_obj.id)
        result = self.environment_controller._calculate_project_environment_hash(
            save_hardware_file=False)
        assert result == "1e32ff083520f792cbe4bafdc2de2a01"
        assert result == environment_obj.unique_hash

        # Test if the hash is the same if the same file is passed in as an input
        input_dict = {
            "paths": [self.definition_filepath, self.random_filepath]
        }
        environment_obj_1 = self.environment_controller.create(
            input_dict, save_hardware_file=False)
        self.environment_ids.append(environment_obj_1.id)
        result = self.environment_controller._calculate_project_environment_hash(
            save_hardware_file=False)
        assert result == "1e32ff083520f792cbe4bafdc2de2a01"
        assert result == environment_obj_1.unique_hash

    def test_has_unstaged_changes(self):
        # Setup
        self.__setup()
        environment_obj = self.environment_controller.create({})
        self.environment_ids.append(environment_obj.id)
        # Check for no unstaged changes
        result = self.environment_controller._has_unstaged_changes()
        assert not result

        # Make a change to the file (update python version)
        with open(
                os.path.join(self.environment_controller.environment_driver.
                             environment_directory_path, "Dockerfile"),
                "wb") as f:
            f.write(to_bytes("FROM python:3.6-alpine"))

        # Check again, should have unstaged changes
        result = self.environment_controller._has_unstaged_changes()
        assert result

    def test_check_unstaged_changes(self):
        # Setup
        self.__setup()
        environment_obj = self.environment_controller.create({})
        self.environment_ids.append(environment_obj.id)

        # 1) After commiting the changes
        # Check for no unstaged changes because already committed
        result = self.environment_controller.check_unstaged_changes()
        assert not result

        # Add a new file
        with open(
                os.path.join(self.environment_controller.environment_driver.
                             environment_directory_path, "test2"), "wb") as f:
            f.write(to_bytes("cool"))

        # 2) Not commiting the changes, should error and raise UnstagedChanges
        failed = False
        try:
            self.environment_controller.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # Remove new file
        os.remove(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "test2"))

        # 3) Files are the same as before but no new commit, should have no unstaged changes
        result = self.environment_controller.check_unstaged_changes()
        assert not result

        # 4) Remove another file, now it is different and should have unstaged changes
        os.remove(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "test"))
        failed = False
        try:
            self.environment_controller.check_unstaged_changes()
        except UnstagedChanges:
            failed = True
        assert failed

        # 5) Remove the rest of the files, now it is empty and should return as already staged
        os.remove(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "Dockerfile"))
        result = self.environment_controller.check_unstaged_changes()
        assert not result

    def test_checkout(self):
        # Setup and create all environment files
        self.__setup()

        # Create environment to checkout to with defaults
        environment_obj = self.environment_controller.create({})
        self.environment_ids.append(environment_obj.id)
        # Checkout success with there are no unstaged changes
        result = self.environment_controller.checkout(environment_obj.id)
        assert result
        current_hash = self.environment_controller._calculate_project_environment_hash(
        )
        assert environment_obj.unique_hash == current_hash
        # Check the filenames as well because the hash does not take this into account
        assert os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "test"))
        assert os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "Dockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "datmoDockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "hardware_info"))

        # Change file contents to make it unstaged
        with open(self.definition_filepath, "wb") as f:
            f.write(to_bytes("new content"))

        # Checkout failure with unstaged changes
        failed = False
        try:
            _ = self.environment_controller.checkout(environment_obj.id)
        except UnstagedChanges:
            failed = True
        assert failed

        # Create new environment to checkout to with defaults (no hardware)
        environment_obj_1 = self.environment_controller.create(
            {}, save_hardware_file=False)
        self.environment_ids.append(environment_obj_1.id)
        # Checkout success with there are no unstaged changes
        result = self.environment_controller.checkout(environment_obj.id)
        assert result
        current_hash = self.environment_controller._calculate_project_environment_hash(
        )
        assert environment_obj.unique_hash == current_hash
        assert environment_obj_1.unique_hash != current_hash
        # Check the filenames as well because the hash does not take this into account
        assert os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "test"))
        assert os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "Dockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "datmoDockerfile"))
        assert not os.path.isfile(
            os.path.join(self.environment_controller.environment_driver.
                         environment_directory_path, "hardware_info"))
