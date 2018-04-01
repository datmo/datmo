"""
Tests for ProjectController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import tempfile

from ..project import ProjectController

class TestProjectController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        self.temp_dir = tempfile.mkdtemp('project')
        self.project = ProjectController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        result = self.project.init("test", "test description")

        # Tested with is_initialized
        assert self.project.model.name == "test"
        assert self.project.code_driver.is_initialized
        assert self.project.file_driver.is_initialized
        assert self.project.environment_driver.is_initialized
        assert result and self.project.is_initialized

        # Changeable by user, not tested in is_initialized
        assert self.project.file_driver.exists_api_file()
        assert self.project.file_driver.exists_script_file()
        assert self.project.current_session.name == "default"

    def test_cleanup(self):
        self.project.init("test2", "test description")
        result = self.project.cleanup()
        assert not self.project.code_driver.exists_code_refs_dir()
        assert not self.project.file_driver.exists_datmo_file_structure()
        assert not self.project.environment_driver.list_images("datmo-test")
        # Ensure that containers built with this image do not exist
        # assert not self.project.environment_driver.list_containers(filters={
        #     "ancestor": image_id
        # })
        assert result == True

    def test_status(self):
        pass

