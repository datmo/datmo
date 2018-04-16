"""
Tests for EnvironmentController
"""
import os
import shutil
import tempfile

from datmo.controller.project import ProjectController
from datmo.controller.environment.environment import \
    EnvironmentController
from datmo.util.exceptions import EntityNotFound


class TestEnvironmentController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir, self.project.dal.driver)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test3", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home,
                                    "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        input_dict = {
            "definition_filepath": definition_filepath,
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        # Get file collection path
        file_collection_obj = self.environment.dal.file_collection.\
            get_by_id(environment_obj.file_collection_id)
        file_collection_dir = self.environment.file_driver.\
            get_collection_path(file_collection_obj.filehash)

        assert environment_obj
        assert environment_obj.id
        assert environment_obj.file_collection_id
        assert environment_obj.definition_filename
        assert environment_obj.hardware_info
        assert environment_obj.unique_hash == file_collection_obj.filehash
        assert os.path.join(file_collection_dir, "Dockerfile")
        assert os.path.join(file_collection_dir, "datmoDockerfile")
        assert os.path.join(file_collection_dir, "hardware_info")

    def test_build(self):
        self.project.init("test5", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home,
                                           "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        input_dict = {
            "definition_filepath": definition_filepath,
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        # Build environment
        result = self.environment.build(environment_obj.id)

        assert result

        # teardown
        self.environment.delete(environment_obj.id)

    def test_run(self):
        self.project.init("test5", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home,
                                           "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": None,
            "name": None,
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "gpu": False,
            "api": False
        }


        # Create environment_driver definition
        env_def_path = os.path.join(self.project.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        input_dict = {
            "definition_filepath": definition_filepath,
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        log_filepath = os.path.join(self.project.home,
                                    "task.log")

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

    def test_list(self):
        self.project.init("test4", "test description")

        # Create environment definition for object 1
        definition_path_1 = os.path.join(self.environment.home,
                                    "Dockerfile")
        with open(definition_path_1, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        input_dict_1 = {
            "definition_filepath": definition_path_1,
        }

        # Create environment in the project
        environment_obj_1 = self.environment.create(input_dict_1)

        # Create environment definition for object 2
        definition_path_2 = os.path.join(self.environment.home,
                                         "Dockerfile2")
        with open(definition_path_2, "w") as f:
            f.write(str("FROM datmo/scikit-opencv"))

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
        definition_filepath = os.path.join(self.environment.home,
                                           "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

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