"""
Tests for EnvironmentController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
        self.temp_dir = tempfile.mkdtemp('project')
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir)

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
            "driver_type": "docker",
            "definition_filepath": definition_filepath,
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        assert environment_obj
        assert environment_obj.id
        assert environment_obj.file_collection_id
        assert environment_obj.definition_filename

    def test_build(self):
        self.project.init("test5", "test description")

        # Create environment definition
        definition_filepath = os.path.join(self.environment.home,
                                           "Dockerfile")
        with open(definition_filepath, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        input_dict = {
            "driver_type": "docker",
            "definition_filepath": definition_filepath,
        }

        # Create environment in the project
        environment_obj = self.environment.create(input_dict)

        # Build environment
        result = self.environment.build(environment_obj.id)

        assert result

    def test_list(self):
        self.project.init("test4", "test description")

        # Create environment definition for object 1
        definition_path_1 = os.path.join(self.environment.home,
                                    "Dockerfile")
        with open(definition_path_1, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        input_dict_1 = {
            "driver_type": "docker",
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
            "driver_type": "docker",
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
            "driver_type": "docker",
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