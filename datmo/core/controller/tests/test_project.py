"""
Tests for ProjectController
"""

import os
import tempfile
import platform
import time
import timeout_decorator
from io import open
try:
    to_unicode = str
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

from datmo.config import Config
from datmo.core.controller.project import ProjectController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.task import TaskController
from datmo.core.entity.snapshot import Snapshot
from datmo.core.util.exceptions import ValidationFailed
from datmo.core.util.misc_functions import check_docker_inactive, pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestProjectController():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        self.project_controller = ProjectController()
        self.environment_ids = []

    def teardown_method(self):
        if not check_docker_inactive(test_datmo_dir,
                                     Config().datmo_directory_name):
            self.project_controller = ProjectController()
            if self.project_controller.is_initialized:
                self.environment_controller = EnvironmentController()
                for env_id in list(set(self.environment_ids)):
                    if not self.environment_controller.delete(env_id):
                        raise Exception

    def test_init_failure_none(self):
        # Test failed case
        failed = False
        try:
            self.project_controller.init(None, None)
        except ValidationFailed:
            failed = True
        assert failed

    def test_init_failure_empty_str(self):
        # Test failed case
        failed = False
        try:
            self.project_controller.init("", "")
        except ValidationFailed:
            failed = True
        assert failed
        assert not self.project_controller.code_driver.is_initialized
        assert not self.project_controller.file_driver.is_initialized
        assert not self.project_controller.environment_driver.is_initialized

    def test_init_failure_git_code_driver(self):
        # Create a HEAD.lock file in .git to make GitCodeDriver.init() fail
        if self.project_controller.code_driver.type == "git":
            git_dir = os.path.join(
                self.project_controller.code_driver.filepath, ".git")
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, "HEAD.lock"), "a+") as f:
                f.write(to_bytes("test"))
            failed = False
            try:
                self.project_controller.init("test1", "test description")
            except Exception:
                failed = True
            assert failed
            assert not self.project_controller.code_driver.is_initialized
            assert not self.project_controller.file_driver.is_initialized

    def test_init_success(self):
        result = self.project_controller.init("test1", "test description")

        # Tested with is_initialized
        assert self.project_controller.model.name == "test1"
        assert self.project_controller.model.description == "test description"
        assert result and self.project_controller.is_initialized

    # TODO: Test lower level functions (DAL, JSONStore, etc for interruptions)
    # def test_init_with_interruption(self):
    #     # Reinitializing after timed interruption during init
    #     @timeout_decorator.timeout(0.001, use_signals=False)
    #     def timed_init_with_interruption():
    #         result = self.project_controller.init("test1", "test description")
    #         return result
    #
    #     failed = False
    #     try:
    #         timed_init_with_interruption()
    #     except timeout_decorator.timeout_decorator.TimeoutError:
    #         failed = True
    #     # Tested with is_initialized
    #     assert failed
    #
    #     # Reperforming init after a wait of 2 seconds
    #     time.sleep(2)
    #     result = self.project_controller.init("test2", "test description")
    #     # Tested with is_initialized
    #     assert self.project_controller.model.name == "test2"
    #     assert self.project_controller.model.description == "test description"
    #     assert result and self.project_controller.is_initialized
    #

    def test_init_reinit_failure_empty_str(self):
        _ = self.project_controller.init("test1", "test description")
        failed = True
        try:
            self.project_controller.init("", "")
        except Exception:
            failed = True
        assert failed
        assert self.project_controller.model.name == "test1"
        assert self.project_controller.model.description == "test description"
        assert self.project_controller.code_driver.is_initialized
        assert self.project_controller.file_driver.is_initialized

    def test_init_reinit_success(self):
        _ = self.project_controller.init("test1", "test description")
        # Test out functionality for re-initialize project
        result = self.project_controller.init("anything", "else")

        assert self.project_controller.model.name == "anything"
        assert self.project_controller.model.description == "else"
        assert result == True

    def test_cleanup_no_environment(self):
        self.project_controller.init("test2", "test description")
        result = self.project_controller.cleanup()

        assert not self.project_controller.code_driver.is_initialized
        assert not self.project_controller.file_driver.is_initialized
        # Ensure that containers built with this image do not exist
        # assert not self.project_controller.environment_driver.list_containers(filters={
        #     "ancestor": image_id
        # })
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_cleanup_with_environment(self):
        self.project_controller.init("test2", "test description")
        result = self.project_controller.cleanup()

        assert not self.project_controller.code_driver.is_initialized
        assert not self.project_controller.file_driver.is_initialized
        assert not self.project_controller.environment_driver.list_images(
            "datmo-test2")
        # Ensure that containers built with this image do not exist
        # assert not self.project_controller.environment_driver.list_containers(filters={
        #     "ancestor": image_id
        # })
        assert result == True

    def test_status_basic(self):
        self.project_controller.init("test3", "test description")
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            self.project_controller.status()

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == "test3"
        assert status_dict['description'] == "test description"
        assert isinstance(status_dict['config'], dict)
        assert not current_snapshot
        assert not latest_snapshot_user_generated
        assert not latest_snapshot_auto_generated
        assert unstaged_code  # no files, but unstaged because blank commit id has not yet been created (no initial snapshot)
        assert not unstaged_environment
        assert not unstaged_files

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_status_snapshot_task(self):
        self.project_controller.init("test4", "test description")
        self.snapshot_controller = SnapshotController()
        self.task_controller = TaskController()

        # Create files to add
        self.snapshot_controller.file_driver.create("dirpath1", directory=True)
        self.snapshot_controller.file_driver.create("dirpath2", directory=True)
        self.snapshot_controller.file_driver.create("filepath1")

        # Create environment definition
        env_def_path = os.path.join(self.snapshot_controller.home,
                                    "Dockerfile")
        with open(env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        environment_paths = [env_def_path]

        # Create config
        config_filepath = os.path.join(self.snapshot_controller.home,
                                       "config.json")
        with open(config_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot_controller.home,
                                      "stats.json")
        with open(stats_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        input_dict = {
            "message":
                "my test snapshot",
            "paths": [
                os.path.join(self.snapshot_controller.home, "dirpath1"),
                os.path.join(self.snapshot_controller.home, "dirpath2"),
                os.path.join(self.snapshot_controller.home, "filepath1")
            ],
            "environment_paths":
                environment_paths,
            "config_filename":
                config_filepath,
            "stats_filename":
                stats_filepath,
        }

        # Create snapshot in the project, then wait, and try status
        first_snapshot = self.snapshot_controller.create(input_dict)

        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            self.project_controller.status()

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == "test4"
        assert status_dict['description'] == "test description"
        assert isinstance(status_dict['config'], dict)
        assert not current_snapshot  # snapshot was created from other environments and files (so user is not on any current snapshot)
        assert isinstance(latest_snapshot_user_generated, Snapshot)
        assert latest_snapshot_user_generated == first_snapshot
        assert not latest_snapshot_auto_generated
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files

        # Create and run a task and test if task is shown
        first_task = self.task_controller.create()

        # Create task_dict
        task_command = ["sh", "-c", "echo accuracy:0.45"]
        task_dict = {"command_list": task_command}

        updated_first_task = self.task_controller.run(
            first_task.id, task_dict=task_dict)
        before_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_first_task.before_snapshot_id)
        after_snapshot_obj = self.task_controller.dal.snapshot.get_by_id(
            updated_first_task.after_snapshot_id)
        before_environment_obj = self.task_controller.dal.environment.get_by_id(
            before_snapshot_obj.environment_id)
        after_environment_obj = self.task_controller.dal.environment.get_by_id(
            after_snapshot_obj.environment_id)
        assert before_environment_obj == after_environment_obj
        self.environment_ids.append(after_environment_obj.id)

        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            self.project_controller.status()

        assert status_dict
        assert isinstance(status_dict, dict)
        assert status_dict['name'] == "test4"
        assert status_dict['description'] == "test description"
        assert isinstance(status_dict['config'], dict)
        assert isinstance(current_snapshot, Snapshot)
        assert isinstance(latest_snapshot_user_generated, Snapshot)
        assert latest_snapshot_user_generated == first_snapshot
        assert isinstance(latest_snapshot_auto_generated, Snapshot)
        # current snapshot is the before snapshot for the run
        assert current_snapshot == before_snapshot_obj
        assert current_snapshot != latest_snapshot_auto_generated
        assert current_snapshot != latest_snapshot_user_generated
        # latest autogenerated snapshot is the after snapshot id
        assert latest_snapshot_auto_generated == after_snapshot_obj
        assert latest_snapshot_auto_generated != latest_snapshot_user_generated
        # user generated snapshot is not associated with any before or after snapshot
        assert latest_snapshot_user_generated != before_snapshot_obj
        assert latest_snapshot_user_generated != after_snapshot_obj
        assert not unstaged_code
        assert not unstaged_environment
        assert not unstaged_files
