"""
Tests for SnapshotController
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile

from datmo.controller.project import ProjectController
from datmo.controller.environment.environment import EnvironmentController
from datmo.controller.snapshot import SnapshotController
from datmo.util.exceptions import EntityNotFound


class TestSnapshotController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        self.temp_dir = tempfile.mkdtemp('project')
        self.project = ProjectController(self.temp_dir)
        self.environment = EnvironmentController(self.temp_dir)
        self.snapshot = SnapshotController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_create(self):
        self.project.init("test3", "test description")

        # Create environment definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        environment_obj = self.environment.create({
            "driver_type": "docker",
            "definition_filepath": env_def_path
        })

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", dir=True)
        self.snapshot.file_driver.create("dirpath2", dir=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                     "config.json")
        with open(config_filepath, "w") as f:
            f.write(str("{}"))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                       "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(str("{}"))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
            "environment_id": environment_obj.id
        }

        # Create snapshot in the project
        snapshot_obj = self.snapshot.create(input_dict)

        assert snapshot_obj
        assert snapshot_obj.code_id
        assert snapshot_obj.environment_id
        assert snapshot_obj.file_collection_id
        assert snapshot_obj.config == {}
        assert snapshot_obj.stats == {}

    def test_checkout(self):
        self.project.init("test4", "test description")

        # Create snapshot

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        environment_obj = self.environment.create({
            "driver_type": "docker",
            "definition_filepath": env_def_path
        })

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", dir=True)
        self.snapshot.file_driver.create("dirpath2", dir=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(str("{}"))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(str("{}"))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
            "environment_id": environment_obj.id
        }

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot.create(input_dict)

        # Create duplicate snapshot in project
        _ = self.snapshot.create(input_dict)

        # Checkout to latest snapshot
        result = self.snapshot.checkout(snapshot_obj_1.id)

        # SnapshotCommand directory in user directory
        snapshot_obj_1_path = os.path.join(self.snapshot.home, "datmo_snapshots",
                                           snapshot_obj_1.id)

        assert result == True and \
               self.snapshot.code_driver.latest_commit() == snapshot_obj_1.code_id and \
               os.path.isdir(snapshot_obj_1_path)


    def test_list(self):
        self.project.init("test4", "test description")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        environment_obj = self.environment.create({
            "driver_type": "docker",
            "definition_filepath": env_def_path
        })

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", dir=True)
        self.snapshot.file_driver.create("dirpath2", dir=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(str("{}"))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(str("{}"))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
            "environment_id": environment_obj.id
        }

        # Create file to add to snapshot
        test_filepath_1 = os.path.join(self.snapshot.home,
                                     "test.txt")
        with open(test_filepath_1, "w") as f:
            f.write(str("test"))

        # Create snapshot in the project
        snapshot_obj_1 = self.snapshot.create(input_dict)

        # Create file to add to second snapshot
        test_filepath_2 = os.path.join(self.snapshot.home,
                                     "test.txt")
        with open(test_filepath_2, "w") as f:
            f.write(str("test"))

        # Create second snapshot in the project
        snapshot_obj_2 = self.snapshot.create(input_dict)

        # List all snapshots and ensure they exist
        result = self.snapshot.list()

        assert len(result) == 2 and \
            snapshot_obj_1 in result and \
            snapshot_obj_2 in result

    def test_delete(self):
        self.project.init("test5", "test description")

        # Create environment_driver definition
        env_def_path = os.path.join(self.snapshot.home,
                                    "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        environment_obj = self.environment.create({
            "driver_type": "docker",
            "definition_filepath": env_def_path
        })

        # Create files to add
        self.snapshot.file_driver.create("dirpath1", dir=True)
        self.snapshot.file_driver.create("dirpath2", dir=True)
        self.snapshot.file_driver.create("filepath1")

        # Create config
        config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(str("{}"))

        # Create stats
        stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(str("{}"))

        input_dict = {
            "filepaths": [os.path.join(self.snapshot.home, "dirpath1"),
                          os.path.join(self.snapshot.home, "dirpath2"),
                          os.path.join(self.snapshot.home, "filepath1")],
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
            "environment_id": environment_obj.id
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