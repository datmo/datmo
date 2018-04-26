"""
Tests for snapshot module
"""
import os
import shutil
import tempfile
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.snapshot import create, ls
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import GitCommitDoesNotExist, \
    InvalidProjectPathException, SessionDoesNotExistException


class TestSnapshotModule():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp"
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        _ = ProjectController(self.temp_dir).\
            init("test", "test description")

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        # check project is not initialized if wrong home
        failed = False
        try:
            create(message="test",
                   home=os.path.join("does","not", "exist"))
        except InvalidProjectPathException:
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
        snapshot_obj_2 = create(message="test", home=self.temp_dir)

        assert snapshot_obj_2
        assert snapshot_obj_2.message == "test"
        assert snapshot_obj_2.code_id
        assert snapshot_obj_2.environment_id
        assert snapshot_obj_2.file_collection_id
        assert snapshot_obj_2.config == {}
        assert snapshot_obj_2.stats == {}
        assert snapshot_obj_2 != snapshot_obj_1

    def test_ls(self):
        # check project is not initialized if wrong home
        failed = False
        try:
            ls(home=os.path.join("does","not", "exist"))
        except InvalidProjectPathException:
            failed = True
        assert failed

        # check session does not exist if wrong session
        failed = False
        try:
            ls(session_id="does_not_exist", home=self.temp_dir)
        except SessionDoesNotExistException:
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

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))
        create(message="test2", home=self.temp_dir)

        # list all snapshots with no filters (works when more than 1 snapshot)
        snapshot_list_2 = ls(home=self.temp_dir)

        assert snapshot_list_2
        assert len(list(snapshot_list_2)) == 2

        # list snapshots with specific filter
        snapshot_list_3 = ls(filter='test2', home=self.temp_dir)

        assert len(list(snapshot_list_3)) == 1

        # list snapshots with filter of none
        snapshot_list_4 = ls(filter='test3', home=self.temp_dir)

        assert len(list(snapshot_list_4)) == 0
