"""
Tests for BaseController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import tempfile

from ..base import BaseController
from datmo.controller.code.driver.git import GitCodeDriver

from datmo.util.exceptions import  \
    DatmoModelNotInitializedException

class TestBaseController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        self.temp_dir = tempfile.mkdtemp('datmo_project')
        self.base = BaseController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_instantiation(self):
        assert self.base != None

    def test_datmo_model(self):
        assert self.base.model == None

    def test_current_session(self):
        try:
            result = self.base.current_session
        except DatmoModelNotInitializedException:
            assert True

    def test_code_manager(self):
        assert self.base.code_driver != None
        assert self.base.code_driver.type == 'git'

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


