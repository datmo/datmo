"""
Tests for ProjectController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.controller.task import TaskController
from datmo.core.entity.snapshot import Snapshot
from datmo.core.entity.task import Task
from datmo.core.util.exceptions import ValidationFailed


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

    def test_init_none(self):
        # Test failed case
        failed = False
        try:
            self.project.init(None, None)
        except ValidationFailed:
            failed = True
        assert failed

    def test_init_empty_str(self):
        # Test failed case
        failed = False
        try:
            self.project.init("", "")
        except ValidationFailed:
            failed = True
        assert failed

    def test_init(self):

        result = self.project.init("test1", "test description")

        # Tested with is_initialized
        assert self.project.model.name == "test1"
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
        self.project.init("test2", "test description")
        result = self.project.cleanup()

        assert not self.project.code_driver.exists_code_refs_dir()
        assert not self.project.file_driver.exists_datmo_file_structure()
        assert not self.project.environment_driver.list_images("datmo-test2")
        # Ensure that containers built with this image do not exist
        # assert not self.project.environment_driver.list_containers(filters={
        #     "ancestor": image_id
        # })
        assert result == True

    def test_status_basic(self):
        self.project.init("test3", "test description")
        status_dict, latest_snapshot, ascending_unstaged_task_list = \
            self.project.status()

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == "test3"
        assert status_dict['description'] == "test description"
        assert isinstance(status_dict['config'], dict)
        assert not latest_snapshot
        assert not ascending_unstaged_task_list

    def test_status_snapshot_task(self):
        self.project.init("test4", "test description")
        self.snapshot = SnapshotController(self.temp_dir)
        self.task = TaskController(self.temp_dir)

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        input_dict = {
            "message":
                "my test snapshot",
            "filepaths": [
                os.path.join(self.snapshot.home, "dirpath1"),
                os.path.join(self.snapshot.home, "dirpath2"),
                os.path.join(self.snapshot.home, "filepath1")
            ],
            "environment_definition_filepath":
                env_def_path,
            "config_filename":
                config_filepath,
            "stats_filename":
                stats_filepath,
        }

        # Create snapshot in the project
        first_snapshot = self.snapshot.create(input_dict)

        status_dict, latest_snapshot, ascending_unstaged_task_list = \
            self.project.status()

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == "test4"
        assert status_dict['description'] == "test description"
        assert isinstance(status_dict['config'], dict)
        assert isinstance(latest_snapshot, Snapshot)
        assert latest_snapshot.id == first_snapshot.id
        assert not ascending_unstaged_task_list

        # Create and run a task and test if unstaged task is shown
        first_task = self.task.create()

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command": task_command}

        updated_first_task = self.task.run(first_task.id, task_dict=task_dict)

        status_dict, latest_snapshot, ascending_unstaged_task_list = \
            self.project.status()

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == "test4"
        assert status_dict['description'] == "test description"
        assert isinstance(status_dict['config'], dict)
        assert isinstance(latest_snapshot, Snapshot)
        assert latest_snapshot.id == first_snapshot.id
        assert isinstance(ascending_unstaged_task_list[0], Task)
        assert ascending_unstaged_task_list[0].id == updated_first_task.id