"""
Tests for snapshot module
"""
import os
import shutil
import tempfile

from datmo.snapshot import create
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
        # (fails w/ no environment)
        test_filepath = os.path.join(self.temp_dir, "test.txt")
        with open(test_filepath, "w") as f:
            f.write("test")
        failed = False
        try:
            _ = create(message="test", home=self.temp_dir)
        except DoesNotExistException:
            failed = True
        assert failed

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write("FROM datmo/xgboost:cpu")
        snapshot_obj = create(message="test", home=self.temp_dir)

        assert snapshot_obj
        assert snapshot_obj.message == "test"
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}