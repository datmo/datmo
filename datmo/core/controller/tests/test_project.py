"""
Tests for ProjectController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import platform

from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import RequiredArgumentMissing


class TestProjectController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)

    def teardown_method(self):
        pass

    def test_init(self):
        # Test failed case
        failed = False
        try:
            self.project.init(None, None)
        except RequiredArgumentMissing:
            failed = True
        assert failed

        result = self.project.init("test", "test description")

        # Tested with is_initialized
        assert self.project.model.name == "test"
        assert self.project.model.description == "test description"
        assert self.project.code_driver.is_initialized
        assert self.project.file_driver.is_initialized
        assert self.project.environment_driver.is_initialized
        assert result and self.project.is_initialized

        # Changeable by user, not tested in is_initialized
        assert self.project.current_session.name == "default"

        # Check Project template if user specified template
        # TODO: Add in Project template if user specifies

        # Test out functionality for re-initialize project
        result = self.project.init("anything", "else")

        assert self.project.model.name == "anything"
        assert self.project.model.description == "else"
        assert result == True

    def test_cleanup(self):
        self.project.init("test", "test description")
        result = self.project.cleanup()
        assert not self.project.code_driver.exists_code_refs_dir()
        assert not self.project.file_driver.exists_datmo_file_structure()
        assert not self.project.environment_driver.list_images("datmo-test2")
        # Ensure that containers built with this image do not exist
        # assert not self.project.environment_driver.list_containers(filters={
        #     "ancestor": image_id
        # })
        assert result == True

    def test_status(self):
        pass
