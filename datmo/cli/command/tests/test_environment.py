"""
Tests for SessionCommand
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import uuid
import tempfile
import shutil
import platform
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import os
from datmo.cli.driver.helper import Helper
from datmo.cli.command.environment import EnvironmentCommand
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation


# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestEnvironment():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.cli_helper = Helper()

    def teardown_class(self):
        pass

    def __set_variables(self):
        self.project = ProjectCommand(self.temp_dir, self.cli_helper)
        self.project.parse(
            ["init", "--name", "foobar", "--description", "test model"])
        self.project.execute()
        self.environment_command = EnvironmentCommand(self.temp_dir, self.cli_helper)

    def test_environment_create(self):
        # 1) Environment definition file in `datmo_environment` folder
        # 2) Environment definition file passed as on option
        # 3) Environment definition file in root project folder
        # 4) No environment definition file present
        self.__set_variables()
        # Test option 1
        # Create environment definition in `datmo_environment` folder
        datmo_environment_folder = os.path.join(self.temp_dir, "datmo_environment")
        os.makedirs(datmo_environment_folder)

        definition_filepath = os.path.join(datmo_environment_folder, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))

        self.environment_command.parse(["environment", "create"])
        result = self.environment_command.execute()

        assert result

        # remove datmo_environment directory
        shutil.rmtree(datmo_environment_folder)

        # Test option 2
        random_datmo_environment_folder = os.path.join(self.temp_dir, "random_datmo_dir")
        os.makedirs(random_datmo_environment_folder)

        definition_filepath = os.path.join(random_datmo_environment_folder, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))

        self.environment_command.parse(["environment", "create", "--environment-def", definition_filepath])
        result = self.environment_command.execute()

        assert result

        # remove radon datmo environment directory
        shutil.rmtree(random_datmo_environment_folder)

        # Test option 3
        definition_filepath = os.path.join(self.temp_dir, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(definition_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))

        self.environment_command.parse(["environment", "create"])
        result = self.environment_command.execute()

        assert result

        os.remove(definition_filepath)

        # Test option 4
        self.environment_command.parse(["environment", "create"])
        result = self.environment_command.execute()

        assert result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_environment_delete(self):
        self.__set_variables()
        self.environment_command.parse(["environment", "create"])
        environment_id = self.environment_command.execute()

        self.environment_command.parse(["environment", "delete", "--id", environment_id])
        result = self.environment_command.execute()

        assert result

    def test_environment_ls(self):
        self.__set_variables()
        self.environment_command.parse(["environment", "create"])
        environment_id = self.environment_command.execute()

        self.environment_command.parse(["environment", "ls"])
        environment_ids = self.environment_command.execute()

        assert environment_id in environment_ids