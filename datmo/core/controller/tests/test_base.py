"""
Tests for BaseController
"""
from __future__ import division
from __future__ import unicode_literals

import os
import tempfile
import platform

from datmo.config import Config
from datmo.core.controller.base import BaseController
from datmo.core.controller.code.driver.file import FileCodeDriver
from datmo.core.controller.file.driver.local import LocalFileDriver
from datmo.core.controller.environment.driver.dockerenv import DockerEnvironmentDriver
from datmo.core.entity.model import Model
from datmo.core.entity.session import Session
from datmo.core.util.exceptions import  \
    DatmoModelNotInitialized, InvalidProjectPath
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestBaseController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.base_controller = BaseController()

    def teardown_method(self):
        pass

    def test_failed_controller_instantiation(self):
        failed = False
        try:
            Config().set_home("does_not_exists")
            BaseController()
        except InvalidProjectPath:
            failed = True
        assert failed

    def test_instantiation(self):
        assert self.base_controller != None

    def test_datmo_model(self):
        # Test failure case
        assert self.base_controller.model == None

        # Test success case
        self.base_controller.dal.model.create(
            Model({
                "name": "test",
                "description": "test"
            }))
        model = self.base_controller.model

        assert model.id
        assert model.name == "test"
        assert model.description == "test"

    def test_current_session(self):
        # Test failure case
        failed = False
        try:
            _ = self.base_controller.current_session
        except DatmoModelNotInitialized:
            failed = True
        assert failed

        # Test success case
        self.base_controller.dal.model.create(
            Model({
                "name": "test",
                "description": "test"
            }))
        _ = self.base_controller.model
        self.base_controller.dal.session.create(
            Session({
                "name": "test",
                "model_id": "test",
                "current": True
            }))
        session = self.base_controller.current_session

        assert session.id
        assert session.name == "test"
        assert session.model_id == "test"
        assert session.current == True

    def test_default_code_driver(self):
        assert self.base_controller.code_driver != None
        assert self.base_controller.code_driver.type == "file"

    def test_default_file_driver(self):
        assert self.base_controller.file_driver != None
        assert self.base_controller.file_driver.type == "local"
        assert self.base_controller.file_driver.root == self.base_controller.home

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_default_environment_driver(self):
        assert self.base_controller.environment_driver != None
        assert self.base_controller.environment_driver.type == "docker"
        assert self.base_controller.environment_driver.filepath == self.base_controller.home

    def test_is_initialized(self):
        assert self.base_controller.is_initialized == \
               (self.base_controller.code_driver.is_initialized and \
               self.base_controller.file_driver.is_initialized and self.base_controller.model)

    def test_dal(self):
        assert self.base_controller.dal != None
        assert self.base_controller.dal.model != None

    def test_default_config_loader(self):
        # TODO: Test all Datmo default settings
        assert self.base_controller.config_loader("controller.code.driver")["constructor"] == \
               FileCodeDriver
        assert self.base_controller.config_loader("controller.file.driver")["constructor"] == \
               LocalFileDriver
        assert self.base_controller.config_loader("controller.environment.driver")["constructor"] == \
               DockerEnvironmentDriver

    def test_sanity_check_for_dal(self):
        model = self.base_controller.dal.model.create(Model({"name": "test"}))
        model2 = self.base_controller.dal.model.get_by_id(model.id)
        assert model and model2
        assert model.id == model2.id
