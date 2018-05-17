"""
Tests for snapshot module
"""
import os
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.config import Config
from datmo.snapshot import create, ls
from datmo.snapshot import Snapshot
from datmo.task import run
from datmo.core.entity.snapshot import Snapshot as CoreSnapshot
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import (
    GitCommitDoesNotExist, InvalidProjectPathException,
    SessionDoesNotExistException, SnapshotCreateFromTaskArgs)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestSnapshotModule():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)
        _ = ProjectController().init("test", "test description")

    def teardown_method(self):
        pass

    def test_snapshot_entity_instantiate(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "session_id": "my_session",
            "message": "my test snapshot",
            "code_id": "my_code",
            "environment_id": "my_environment",
            "file_collection_id": "my_files",
            "config": {},
            "stats": {}
        }
        core_snapshot_entity = CoreSnapshot(input_dict)
        snapshot_entity = Snapshot(core_snapshot_entity)

        for k, v in input_dict.items():
            assert getattr(snapshot_entity, k) == v
        assert snapshot_entity.task_id == None
        assert snapshot_entity.label == None
        assert snapshot_entity.created_at

    def test_create(self):
        # check project is not initialized if wrong home
        failed = False
        try:
            create(message="test")
        except InvalidProjectPathException:
            failed = True
        assert failed

        # Create a snapshot with default params
        # (fails w/ no commit)
        failed = False
        try:
            _ = create(message="test")
        except GitCommitDoesNotExist:
            failed = True
        assert failed

        # Create a snapshot with default params and files to commit
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))

        snapshot_obj_1 = create(message="test")

        assert snapshot_obj_1
        assert isinstance(snapshot_obj_1, Snapshot)
        assert snapshot_obj_1.message == "test"
        assert snapshot_obj_1.code_id
        assert snapshot_obj_1.environment_id
        assert snapshot_obj_1.file_collection_id
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))
        snapshot_obj_2 = create(message="test")

        assert snapshot_obj_2
        assert isinstance(snapshot_obj_2, Snapshot)
        assert snapshot_obj_2.message == "test"
        assert snapshot_obj_2.code_id
        assert snapshot_obj_2.environment_id
        assert snapshot_obj_2.file_collection_id
        assert snapshot_obj_2.config == {}
        assert snapshot_obj_2.stats == {}
        assert snapshot_obj_2 != snapshot_obj_1

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_create_from_task(self):
        # 1) Test if success with task files, results, and message
        # 2) Test if success with user given config and stats
        # TODO: test for failure case where tasks is not complete

        # Setup task

        # Create environment definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        task_obj = run("sh -c echo accuracy:0.45")

        # 1) Test option 1
        snapshot_obj = create(
            message="my test snapshot",
            task_id=task_obj.id,
            label="best",
            config={"foo": "bar"})

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.label == "best"
        assert snapshot_obj.config == {"foo": "bar"}
        assert snapshot_obj.stats == task_obj.results

        # Test option 2
        snapshot_obj_2 = create(
            message="my test snapshot",
            task_id=task_obj.id,
            label="best",
            config={"foo": "bar"},
            stats={"foo": "bar"})

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj_2.message == "my test snapshot"
        assert snapshot_obj_2.label == "best"
        assert snapshot_obj_2.config == {"foo": "bar"}
        assert snapshot_obj_2.stats == {"foo": "bar"}

    def test_create_from_task_fail_user_inputs(self):
        # Setup task

        # Create environment definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        task_obj = run("sh -c echo accuracy:0.45")

        # Test if failure if user gives other parameters
        failed = False
        try:
            _ = create(
                message="my test snapshot",
                task_id=task_obj.id,
                label="best",
                config={"foo": "bar"},
                stats={"foo": "bar"},
                commit_id="test_id")
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            _ = create(
                message="my test snapshot",
                task_id=task_obj.id,
                label="best",
                config={"foo": "bar"},
                stats={"foo": "bar"},
                environment_id="test_id")
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

        failed = False
        try:
            _ = create(
                message="my test snapshot",
                task_id=task_obj.id,
                label="best",
                config={"foo": "bar"},
                stats={"foo": "bar"},
                filepaths=["mypath"])
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

    def test_ls(self):

        # check session does not exist if wrong session
        failed = False
        try:
            ls(session_id="does_not_exist")
        except SessionDoesNotExistException:
            failed = True
        assert failed

        # create with default params and files to commit
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))

        create(message="test1")

        # list all snapshots with no filters
        snapshot_list_1 = ls()

        assert snapshot_list_1
        assert len(list(snapshot_list_1)) == 1
        assert isinstance(snapshot_list_1[0], Snapshot)

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))
        create(message="test2")

        # list all snapshots with no filters (works when more than 1 snapshot)
        snapshot_list_2 = ls()

        assert snapshot_list_2
        assert len(list(snapshot_list_2)) == 2
        assert isinstance(snapshot_list_2[0], Snapshot)
        assert isinstance(snapshot_list_2[1], Snapshot)

        # list snapshots with specific filter
        snapshot_list_3 = ls(filter='test2')

        assert snapshot_list_3
        assert len(list(snapshot_list_3)) == 1
        assert isinstance(snapshot_list_3[0], Snapshot)

        # list snapshots with filter of none
        snapshot_list_4 = ls(filter='test3')

        assert len(list(snapshot_list_4)) == 0
