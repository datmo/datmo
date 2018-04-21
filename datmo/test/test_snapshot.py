"""
Tests for snapshot module
"""
import os
import shutil
import tempfile

from datmo.snapshot import create, ls
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import GitCommitDoesNotExist, \
    DoesNotExistException


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
            f.write("import numpy\n")
            f.write("import sklean\n")

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
            f.write("FROM datmo/xgboost:cpu")
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

        # create with default params and files to commit
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write("import numpy\n")
            f.write("import sklean\n")

        create(message="test", home=self.temp_dir)

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write("FROM datmo/xgboost:cpu")
        create(message="test", home=self.temp_dir)

        # list all snapshots with no filters
        snapshot_ls_1 = ls(home=self.temp_dir)
        # list snapshots with specific filter
        snapshot_ls_2 = ls(filter='test', home=self.temp_dir)
        assert snapshot_ls_1
        assert len(snapshot_ls_1) == 2
        assert len(snapshot_ls_2) == 2
