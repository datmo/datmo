"""
Tests for snapshot module
"""
import os
import tempfile
import platform
from io import open, TextIOWrapper
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.snapshot import create, ls
from datmo.snapshot import Snapshot
from datmo.task import run
from datmo.core.entity.snapshot import Snapshot as CoreSnapshot
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import (
    GitCommitDoesNotExist, InvalidProjectPath, SessionDoesNotExist,
    SnapshotCreateFromTaskArgs, DoesNotExist)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestSnapshotModule():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        _ = ProjectController(self.temp_dir).\
            init("test", "test description")

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
            "file_collection_id": "my_file_collection",
            "config": {},
            "stats": {}
        }
        core_snapshot_entity = CoreSnapshot(input_dict)
        snapshot_entity = Snapshot(core_snapshot_entity, home=self.temp_dir)

        for k, v in input_dict.items():
            if k != "file_collection_id":
                assert getattr(snapshot_entity, k) == v
        assert snapshot_entity.task_id == None
        assert snapshot_entity.label == None
        assert snapshot_entity.created_at

    def test_create(self):
        # check project is not initialized if wrong home
        failed = False
        try:
            create(message="test", home=os.path.join("does", "not", "exist"))
        except InvalidProjectPath:
            failed = True
        assert failed

        # Create a snapshot with default params
        # (fails w/ no commit)
        failed = False
        try:
            _ = create(message="test", home=self.temp_dir)
        except GitCommitDoesNotExist:
            failed = True
        assert failed

        # Create a snapshot with default params and files to commit
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))

        snapshot_obj_1 = create(message="test", home=self.temp_dir)

        assert snapshot_obj_1
        assert isinstance(snapshot_obj_1, Snapshot)
        assert snapshot_obj_1.message == "test"
        assert snapshot_obj_1.code_id
        assert snapshot_obj_1.environment_id
        assert snapshot_obj_1.files == []
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))
        snapshot_obj_2 = create(message="test", home=self.temp_dir)

        assert snapshot_obj_2
        assert isinstance(snapshot_obj_2, Snapshot)
        assert snapshot_obj_2.message == "test"
        assert snapshot_obj_2.code_id
        assert snapshot_obj_2.environment_id
        assert snapshot_obj_2.files == []
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

        task_obj = run("sh -c echo accuracy:0.45", home=self.temp_dir)

        # 1) Test option 1
        snapshot_obj = create(
            message="my test snapshot",
            task_id=task_obj.id,
            home=self.temp_dir,
            label="best",
            config={"foo": "bar"})

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj.message == "my test snapshot"
        assert snapshot_obj.label == "best"
        assert len(snapshot_obj.files) == 1
        assert "task.log" in snapshot_obj.files[0].name
        assert snapshot_obj.config == {"foo": "bar"}
        assert snapshot_obj.stats == task_obj.results

        # Test option 2
        snapshot_obj_2 = create(
            message="my test snapshot",
            task_id=task_obj.id,
            home=self.temp_dir,
            label="best",
            config={"foo": "bar"},
            stats={"foo": "bar"})

        assert isinstance(snapshot_obj, Snapshot)
        assert snapshot_obj_2.message == "my test snapshot"
        assert snapshot_obj_2.label == "best"
        assert len(snapshot_obj.files) == 1
        assert "task.log" in snapshot_obj.files[0].name
        assert snapshot_obj_2.config == {"foo": "bar"}
        assert snapshot_obj_2.stats == {"foo": "bar"}

    def test_create_from_task_fail_user_inputs(self):
        # Setup task

        # Create environment definition
        env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        task_obj = run("sh -c echo accuracy:0.45", home=self.temp_dir)

        # Test if failure if user gives other parameters
        failed = False
        try:
            _ = create(
                message="my test snapshot",
                task_id=task_obj.id,
                home=self.temp_dir,
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
                home=self.temp_dir,
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
                home=self.temp_dir,
                label="best",
                config={"foo": "bar"},
                stats={"foo": "bar"},
                filepaths=["mypath"])
        except SnapshotCreateFromTaskArgs:
            failed = True
        assert failed

    def test_ls(self):
        # check project is not initialized if wrong home
        failed = False
        try:
            ls(home=os.path.join("does", "not", "exist"))
        except InvalidProjectPath:
            failed = True
        assert failed

        # check session does not exist if wrong session
        failed = False
        try:
            ls(session_id="does_not_exist", home=self.temp_dir)
        except SessionDoesNotExist:
            failed = True
        assert failed

        # create with default params and files to commit
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))

        create(message="test1", home=self.temp_dir)

        # list all snapshots with no filters
        snapshot_list_1 = ls(home=self.temp_dir)

        assert snapshot_list_1
        assert len(list(snapshot_list_1)) == 1
        assert isinstance(snapshot_list_1[0], Snapshot)

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))
        create(message="test2", home=self.temp_dir)

        # list all snapshots with no filters (works when more than 1 snapshot)
        snapshot_list_2 = ls(home=self.temp_dir)

        assert snapshot_list_2
        assert len(list(snapshot_list_2)) == 2
        assert isinstance(snapshot_list_2[0], Snapshot)
        assert isinstance(snapshot_list_2[1], Snapshot)

        # list snapshots with specific filter
        snapshot_list_3 = ls(filter='test2', home=self.temp_dir)

        assert snapshot_list_3
        assert len(list(snapshot_list_3)) == 1
        assert isinstance(snapshot_list_3[0], Snapshot)

        # list snapshots with filter of none
        snapshot_list_4 = ls(filter='test3', home=self.temp_dir)

        assert len(list(snapshot_list_4)) == 0

    def __setup(self):
        # Create a snapshot with default params and files to commit
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))

        return create(
            message="test", home=self.temp_dir, filepaths=[test_filepath])

    def test_snapshot_entity_files(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "session_id": "my_session",
            "message": "my message",
            "code_id": "my_code_id",
            "environment_id": "my_environment_id",
            "file_collection_id": "my file collection",
            "config": {
                "test": 0.56
            },
            "stats": {
                "test": 0.34
            }
        }
        core_snapshot_entity = CoreSnapshot(input_dict)
        snapshot_entity = Snapshot(core_snapshot_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            snapshot_entity.files
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        snapshot_entity = self.__setup()
        result = snapshot_entity.files

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].mode == "r"
        assert "script.py" in result[0].name

    def test_task_entity_get_files(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "session_id": "my_session",
            "message": "my message",
            "code_id": "my_code_id",
            "environment_id": "my_environment_id",
            "file_collection_id": "my file collection",
            "config": {
                "test": 0.56
            },
            "stats": {
                "test": 0.34
            }
        }
        core_snapshot_entity = CoreSnapshot(input_dict)
        snapshot_entity = Snapshot(core_snapshot_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            snapshot_entity.get_files()
        except DoesNotExist:
            failed = True
        assert failed

        # Test success
        snapshot_entity = self.__setup()
        result = snapshot_entity.get_files()

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].mode == "r"
        assert "script.py" in result[0].name

        snapshot_entity = self.__setup()
        result = snapshot_entity.get_files(mode="a")

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].mode == "a"
        assert "script.py" in result[0].name
