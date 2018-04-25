"""
Tests for snapshot module
"""
import os
import shutil
import tempfile

from datmo.task import run
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import GitCommitDoesNotExist


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
            _ = run(command="test", home=self.temp_dir)
        except GitCommitDoesNotExist:
            failed = True
        assert failed

        # Create a snapshot with default params and files to commit
        # (fails w/ no environment)
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write("import numpy\n")
            f.write("import sklearn\n")
            f.write("print 'hello'\n")

        # Create a snapshot with default params, files, and environment
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write("FROM datmo/xgboost:cpu")

        task_obj = run(command="python script.py", env=test_filepath, home=self.temp_dir)
        assert task_obj.id
        assert 'hello' in task_obj.logs
