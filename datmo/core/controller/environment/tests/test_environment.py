"""
Tests for EnvironmentController
"""
import os
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import \
    EnvironmentController
from datmo.core.util.exceptions import (EntityNotFound, PathDoesNotExist,
                                        EnvironmentDoesNotExist)


class TestEnvironmentController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir)

    def teardown_method(self):
        pass

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
        failed = False
        try:
            self.environment.create({})
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

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
            os.path.join(file_collection_dir, "requirements.txt"))
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

    def test_run(self):
        # 1) Test run simple command with simple Dockerfile
        # 2) Test run script, with autogenerated definition
        self.project.init("test5", "test description")

        # 1) Test option 1

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": None,
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "gpu": False,
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

        run_options = {
            "command": ["python", "script.py"],
            "ports": ["8888:8888"],
            "name": None,
            "volumes": {
                self.environment.home: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            },
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "gpu": False,
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

    def test_stop(self):
        self.project.init("test5", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home, "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:8888"],
            "name": None,
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "gpu": False,
            "api": False
        }

        # Create environment_driver definition
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

        # Run environment in the project
        _, run_id, _ = \
            self.environment.run(environment_obj.id, run_options, log_filepath)

        # Stop the running environment
        return_code = self.environment.stop(run_id)
        assert return_code

        # teardown
        self.environment.delete(environment_obj.id)
