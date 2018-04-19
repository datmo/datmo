"""
Tests for BaseController
"""
from __future__ import division
from __future__ import unicode_literals

import os
import shutil
import tempfile

from datmo.core.controller.base import BaseController
from datmo.core.controller.code.driver.git import GitCodeDriver
from datmo.core.util.exceptions import  \
    DatmoModelNotInitializedException


class TestBaseController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp"
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.base = BaseController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_instantiation(self):
        assert self.base != None

    def test_datmo_model(self):
        # Test failure case
        assert self.base.model == None

        # Test success case
        self.base.dal.model.create({
            "name": "test",
            "description": "test"
        })
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
        self.base.dal.model.create({
            "name": "test",
            "description": "test"
        })
        _ = self.base.model
        self.base.dal.session.create({
            "name": "test",
            "model_id": "test",
            "current": True
        })
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

    def test_environment(self):
        assert self.base.environment_driver != None
        assert self.base.environment_driver.filepath == self.base.home

    def test_dal(self):
        assert self.base.dal != None
        assert self.base.dal.model != None

    def test_config_loader(self):
        # TODO: Test all Datmo default settings
        assert self.base.config_loader("controller.code.driver")["constructor"] == \
               GitCodeDriver

    def test_sanity_check_for_dal(self):
        model = self.base.dal.model.create({"name": "test"})
        model2 = self.base.dal.model.get_by_id(model.id)
        assert model and model2
        assert model.id == model2.id


