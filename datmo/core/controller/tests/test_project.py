"""
Tests for ProjectController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import platform
import time
import timeout_decorator
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.controller.project import ProjectController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.controller.task import TaskController
from datmo.core.entity.snapshot import Snapshot
from datmo.core.entity.task import Task
from datmo.core.util.exceptions import ValidationFailed
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestProjectController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)

    def teardown_method(self):
        pass

    def test_init_failure_none(self):
        # Test failed case
        failed = False
        try:
            self.project.init(None, None)
        except ValidationFailed:
            failed = True
        assert failed

    def test_init_failure_empty_str(self):
        # Test failed case
        failed = False
        try:
            self.project.init("", "")
        except ValidationFailed:
            failed = True
        assert failed
        assert not self.project.code_driver.is_initialized
        assert not self.project.file_driver.is_initialized

    def test_init_failure_git_code_driver(self):
        # Create a HEAD.lock file in .git to make GitCodeDriver.init() fail
        if self.project.code_driver.type == "git":
            git_dir = os.path.join(self.project.code_driver.filepath, ".git")
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, "HEAD.lock"), "a+") as f:
                f.write(to_bytes("test"))
            failed = False
            try:
                self.project.init("test1", "test description")
            except Exception:
                failed = True
            assert failed
            assert not self.project.code_driver.is_initialized
            assert not self.project.file_driver.is_initialized

    def test_init_success(self):
        result = self.project.init("test1", "test description")

        # Tested with is_initialized
        assert self.project.model.name == "test1"
        assert self.project.model.description == "test description"
        assert result and self.project.is_initialized

        # Changeable by user, not tested in is_initialized
        assert self.project.current_session.name == "default"

    def test_init_with_interuption(self):
        # Reinitializing after timed interuption during init

        @timeout_decorator.timeout(0.01, use_signals=False)
        def timed_init_with_interuption():
            result = self.project.init("test1", "test description")
            return result

        failed = False
        try:
            timed_init_with_interuption()
        except timeout_decorator.timeout_decorator.TimeoutError:
            failed = True
        # Tested with is_initialized
        assert failed

        # Reperforming init after a wait of 1 second
        time.sleep(1)
        result = self.project.init("test2", "test description")
        # Tested with is_initialized
        assert self.project.model.name == "test2"
        assert self.project.model.description == "test description"
        assert result and self.project.is_initialized

        # Changeable by user, not tested in is_initialized
        assert self.project.current_session.name == "default"


    def test_init_reinit_failure_empty_str(self):
        _ = self.project.init("test1", "test description")
        failed = True
        try:
            self.project.init("", "")
        except Exception:
            failed = True
        assert failed
        assert self.project.model.name == "test1"
        assert self.project.model.description == "test description"
        assert self.project.code_driver.is_initialized
        assert self.project.file_driver.is_initialized

    def test_init_reinit_success(self):
        _ = self.project.init("test1", "test description")
        # Test out functionality for re-initialize project
        result = self.project.init("anything", "else")

        assert self.project.model.name == "anything"
        assert self.project.model.description == "else"
        assert result == True

    def test_cleanup_no_environment(self):
        self.project.init("test2", "test description")
        result = self.project.cleanup()

        assert not self.project.code_driver.is_initialized
        assert not self.project.file_driver.is_initialized
        # Ensure that containers built with this image do not exist
        # assert not self.project.environment_driver.list_containers(filters={
        #     "ancestor": image_id
        # })
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_cleanup_with_environment(self):
        self.project.init("test2", "test description")
        result = self.project.cleanup()

        assert not self.project.code_driver.is_initialized
        assert not self.project.file_driver.is_initialized
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
        with open(env_def_path, "wb") as f:
            f.write(to_bytes(str("FROM datmo/xgboost:cpu")))

        environment_paths = [env_def_path]

        # Create config
        config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        input_dict = {
            "message":
                "my test snapshot",
            "paths": [
                os.path.join(self.snapshot.home, "dirpath1"),
                os.path.join(self.snapshot.home, "dirpath2"),
                os.path.join(self.snapshot.home, "filepath1")
            ],
            "environment_paths":
                environment_paths,
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
        task_dict = {"command_list": task_command}

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
