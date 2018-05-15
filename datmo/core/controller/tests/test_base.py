"""
Tests for BaseController
"""
from __future__ import division
from __future__ import unicode_literals

import os
import tempfile
import platform

from datmo.core.controller.base import BaseController
from datmo.core.controller.code.driver.git import GitCodeDriver
from datmo.core.entity.model import Model
from datmo.core.entity.session import Session
from datmo.core.util.exceptions import  \
    DatmoModelNotInitializedException, InvalidProjectPathException
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestBaseController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.base = BaseController(home=self.temp_dir)

    def teardown_method(self):
        pass

    def test_failed_controller_instantiation(self):
        failed = False
        try:
            BaseController(home=os.path.join("does", "not", "exist"))
        except InvalidProjectPathException:
            failed = True
        assert failed

    def test_instantiation(self):
        assert self.base != None

    def test_datmo_model(self):
        # Test failure case
        assert self.base.model == None

        # Test success case
        self.base.dal.model.create(
            Model({
                "name": "test",
                "description": "test"
            }))
        model = self.base.model

        assert model.id
        assert model.name == "test"
        assert model.description == "test"

    def test_current_session(self):
        # Test failure case
        failed = False
        try:
            _ = self.base.current_session
        except DatmoModelNotInitializedException:
            failed = True
        assert failed

        # Test success case
        self.base.dal.model.create(
            Model({
                "name": "test",
                "description": "test"
            }))
        _ = self.base.model
        self.base.dal.session.create(
            Session({
                "name": "test",
                "model_id": "test",
                "current": True
            }))
        session = self.base.current_session

        assert session.id
        assert session.name == "test"
        assert session.model_id == "test"
        assert session.current == True

    def test_code_manager(self):
        assert self.base.code_driver != None
        assert self.base.code_driver.type == "git"

    def test_file_tree(self):
        assert self.base.file_driver != None
        assert self.base.file_driver.filepath == self.base.home

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_environment(self):
        assert self.base.environment_driver != None
        assert self.base.environment_driver.filepath == self.base.home

    def test_is_initialized(self):
        assert self.base.is_initialized == \
               (self.base.code_driver.is_initialized and \
               self.base.file_driver.is_initialized and self.base.model)

    def test_dal(self):
        assert self.base.dal != None
        assert self.base.dal.model != None

    def test_config_loader(self):
        # TODO: Test all Datmo default settings
        assert self.base.config_loader("controller.code.driver")["constructor"] == \
               GitCodeDriver

    def test_sanity_check_for_dal(self):
        model = self.base.dal.model.create(Model({"name": "test"}))
        model2 = self.base.dal.model.get_by_id(model.id)
        assert model and model2
        assert model.id == model2.id
