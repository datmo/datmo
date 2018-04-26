"""
Tests for SnapshotController
"""
import os
import shutil
import tempfile
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.controller.project import ProjectController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.util.exceptions import EntityNotFound, \
    DoesNotExistException, GitCommitDoesNotExist, \
    SessionDoesNotExistException


class TestSnapshotController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.snapshot = SnapshotController(self.temp_dir)

    def teardown_method(self):
        pass

    def test_create(self):
        # Test default values for snapshot, fail due to code
        failed = False
        try:
            self.snapshot.create({})
        except GitCommitDoesNotExist:
            failed = True
        assert failed

        # Test default values for snapshot, fail due to environment with other than default
        self.snapshot.file_driver.create("filepath1")
        failed = False
        try:
            self.snapshot.create({"language": "java"})
        except DoesNotExistException:
            failed = True
        assert failed

        # Test default values when there is not environment
        snapshot_obj_1 = self.snapshot.create({})

        assert snapshot_obj_1
        assert snapshot_obj_1.code_id
        assert snapshot_obj_1.environment_id
        assert snapshot_obj_1.file_collection_id
        assert snapshot_obj_1.config == {}
        assert snapshot_obj_1.stats == {}

        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Test default values for snapshot, success
        snapshot_obj_2 = self.snapshot.create({})

        assert snapshot_obj_2
        assert snapshot_obj_2.code_id
        assert snapshot_obj_2.environment_id
        assert snapshot_obj_2.file_collection_id
        assert snapshot_obj_2.config == {}
        assert snapshot_obj_2.stats == {}

        # Test 2 snapshots with same parameters
        # Should return the same object back
        snapshot_obj_3 = self.snapshot.create({})

        assert snapshot_obj_3 == snapshot_obj_2
        assert snapshot_obj_3.code_id == snapshot_obj_2.code_id
        assert snapshot_obj_3.environment_id == \
               snapshot_obj_2.environment_id
        assert snapshot_obj_3.file_collection_id == \
               snapshot_obj_2.file_collection_id
        assert snapshot_obj_3.config == \
               snapshot_obj_2.config
        assert snapshot_obj_3.stats == \
               snapshot_obj_2.stats

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                     "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str('{"foo":"bar"}')))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                       "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str('{"foo":"bar"}')))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "environment_definition_filepath": env_def_path,
            "config_filepath": config_filepath,
            "stats_filepath": stats_filepath,
        }
        # Create snapshot in the project
        snapshot_obj_4 = self.snapshot.create(input_dict)

        assert snapshot_obj_4 != snapshot_obj_2
        assert snapshot_obj_4.code_id != snapshot_obj_2.code_id
        assert snapshot_obj_4.environment_id == \
               snapshot_obj_2.environment_id
        assert snapshot_obj_4.file_collection_id != \
               snapshot_obj_2.file_collection_id
        assert snapshot_obj_4.config == {"foo": "bar"}
        assert snapshot_obj_4.stats == {"foo": "bar"}

        # Test different config and stats inputs
        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "environment_definition_filepath": env_def_path,
            "config_filename": "different_name",
            "stats_filename": "different_name",
        }

        # Create snapshot in the project
        snapshot_obj_5 = self.snapshot.create(input_dict)

        assert snapshot_obj_5 != snapshot_obj_2
        assert snapshot_obj_5.config == {}
        assert snapshot_obj_5.stats == {}

        # Test different config and stats inputs
        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "environment_definition_filepath": env_def_path,
            "config": {"foo": "bar"},
            "stats": {"foo": "bar"},
        }

        # Create snapshot in the project
        snapshot_obj_6 = self.snapshot.create(input_dict)

        assert snapshot_obj_6 != snapshot_obj_5
        assert snapshot_obj_6.config == {"foo": "bar"}
        assert snapshot_obj_6.stats == {"foo": "bar"}

    def test_checkout(self):
        # Create snapshot

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "environment_definition_filepath": env_def_path,
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
        }

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot.create(input_dict)
        code_obj_1 = self.snapshot.dal.code.get_by_id(snapshot_obj_1.code_id)

        # Create duplicate snapshot in project
        _ = self.snapshot.create(input_dict)

        # Checkout to snapshot 1 using snapshot id
        result = self.snapshot.checkout(snapshot_obj_1.id)

        # SnapshotCommand directory in user directory
        snapshot_obj_1_path = os.path.join(self.snapshot.home, "datmo_snapshots",
                                           snapshot_obj_1.id)

        assert result == True and \
               self.snapshot.code_driver.latest_commit() == code_obj_1.commit_id and \
               os.path.isdir(snapshot_obj_1_path)

    def test_list(self):
        # Check for error if incorrect session given
        failed = False
        try:
            self.snapshot.list(session_id="does_not_exist")
        except SessionDoesNotExistException:
            failed = True
        assert failed

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "environment_definition_filepath": env_def_path,
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
        }

        # Create file to add to snapshot
        test_filepath_1 = os.path.join(self.snapshot.home,
                                     "test.txt")
        with open(test_filepath_1, "w") as f:
            f.write(to_unicode(str("test")))

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot.create(input_dict)

        # Create file to add to second snapshot
        test_filepath_2 = os.path.join(self.snapshot.home,
                                     "test2.txt")
        with open(test_filepath_2, "w") as f:
            f.write(to_unicode(str("test2")))

        # Create second snapshot in the project
        snapshot_obj_2 = self.snapshot.create(input_dict)

        # List all snapshots and ensure they exist
        result = self.snapshot.list()

        assert len(result) == 2 and \
            snapshot_obj_1 in result and \
            snapshot_obj_2 in result

        # List all snapshots with session filter
        result = self.snapshot.list(session_id=
                                    self.project.current_session.id)

        assert len(result) == 2 and \
               snapshot_obj_1 in result and \
               snapshot_obj_2 in result

    def test_delete(self):
        # Create files to add
        self.snapshot.file_driver.create("dirpath1", directory=True)
        self.snapshot.file_driver.create("dirpath2", directory=True)
        self.snapshot.file_driver.create("filepath1")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(to_unicode(str("FROM datmo/xgboost:cpu")))

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(to_unicode(str("{}")))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "environment_definition_filepath": env_def_path,
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
        }

        # Create snapshot in the project
        snapshot_obj = self.snapshot.create(input_dict)

        # Delete snapshot in the project
        result = self.snapshot.delete(snapshot_obj.id)

        # Check if snapshot retrieval throws error
        thrown = False
        try:
            self.snapshot.dal.snapshot.get_by_id(snapshot_obj.id)
        except EntityNotFound:
            thrown = True

        assert result == True and \
            thrown == True