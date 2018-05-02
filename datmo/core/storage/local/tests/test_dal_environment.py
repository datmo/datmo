"""
Tests for LocalDAL
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import platform
from datetime import datetime

from datmo.core.storage.driver.blitzdb_dal_driver import BlitzDBDALDriver
from datmo.core.storage.local.dal import LocalDAL
from datmo.core.entity.model import Model
from datmo.core.entity.environment import Environment
from datmo.core.util.exceptions import EntityNotFound


class TestLocalDAL():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.datadriver = BlitzDBDALDriver("file", self.temp_dir)

        self.dal = LocalDAL(self.datadriver)
        model_name = "model_1"
        model = self.dal.model.create(Model({"name": model_name}))

        self.environment_input_dict = {
            "model_id": model.id,
            "driver_type": "docker",
            "file_collection_id": "test_file_id",
            "definition_filename": "Dockerfile",
            "hardware_info": {
                "system": "macosx"
            },
            "unique_hash": "slkdjfa23dk",
            "language": "python3"
        }

    def teardown_class(self):
        pass

    # TODO: Add tests for other variables once figured out.

    def test_create_environment_by_dictionary(self):
        environment = self.dal.environment.create(
            Environment(self.environment_input_dict))

        assert environment.id
        assert environment.driver_type == self.environment_input_dict[
            'driver_type']
        assert environment.file_collection_id == self.environment_input_dict[
            'file_collection_id']
        assert environment.definition_filename == self.environment_input_dict[
            'definition_filename']
        assert environment.hardware_info == self.environment_input_dict[
            'hardware_info']
        assert environment.unique_hash == self.environment_input_dict[
            'unique_hash']
        assert environment.language == self.environment_input_dict['language']
        assert environment.created_at
        assert environment.updated_at

        environment_2 = self.dal.environment.create(
            Environment(self.environment_input_dict))

        assert environment_2.id != environment.id

        test_environment_input_dict = self.environment_input_dict.copy()
        test_environment_input_dict['id'] = "environment_id"
        environment_3 = self.dal.environment.create(
            Environment(test_environment_input_dict))

        assert environment_3.id == test_environment_input_dict['id']

    def test_get_by_id_environment(self):
        environment = self.dal.environment.create(
            Environment(self.environment_input_dict))

        result = self.dal.environment.get_by_id(environment.id)
        assert environment.id == result.id

    def test_get_by_id_environment_new_driver_instance(self):
        environment = self.dal.environment.create(
            Environment(self.environment_input_dict))

        # create new dal with new driver instance (success)
        new_driver_instance = BlitzDBDALDriver("file", self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        new_environment_1 = new_dal_instance.environment.get_by_id(
            environment.id)
        assert new_environment_1.id == environment.id
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_environment_2 = new_dal_instance.environment.get_by_id(
            environment.id)
        assert new_environment_2.id == environment.id

    def test_update_environment(self):
        environment = self.dal.environment.create(
            Environment(self.environment_input_dict))

        # Update required and optional parameters
        updated_environment_input_dict = self.environment_input_dict.copy()
        updated_environment_input_dict['id'] = environment.id
        updated_environment_input_dict['driver_type'] = "new_driver"
        updated_environment_input_dict['created_at'] = datetime.utcnow()
        updated_environment = self.dal.environment.update(
            updated_environment_input_dict)
        assert environment.id == updated_environment.id
        assert environment.updated_at < updated_environment.updated_at
        assert updated_environment.driver_type == updated_environment_input_dict[
            'driver_type']
        assert updated_environment.created_at == updated_environment_input_dict[
            'created_at']

    def test_delete_environment(self):
        environment = self.dal.environment.create(
            Environment(self.environment_input_dict))

        self.dal.environment.delete(environment.id)
        deleted = False
        try:
            self.dal.environment.get_by_id(environment.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_environments(self):
        environment = self.dal.environment.create(
            Environment(self.environment_input_dict))

        assert len(self.dal.environment.query({"id": environment.id})) == 1
