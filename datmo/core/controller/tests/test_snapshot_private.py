"""
Tests for SnapshotController
"""
import os
import tempfile
import platform

from datmo.core.controller.project import ProjectController
from datmo.core.controller.snapshot import SnapshotController


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

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir,
                                         "Dockerfile")
        with open(self.env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        # Create config
        self.config_filepath = os.path.join(self.snapshot.home,
                                       "config.json")
        with open(self.config_filepath, "w") as f:
            f.write(str('{"foo":1}'))

        # Create stats
        self.stats_filepath = os.path.join(self.snapshot.home,
                                      "stats.json")
        with open(self.stats_filepath, "w") as f:
            f.write(str('{"bar":1}'))

        # Create test file
        self.filepath = os.path.join(self.snapshot.home,
                                           "file.txt")
        with open(self.filepath, "w") as f:
            f.write(str("test"))

    def teardown_method(self):
        pass

    def test_code_setup_with_code_id(self):
        val = 1
        incoming_data = {"code_id": val}
        final_data = {}
        self.snapshot._code_setup(incoming_data, final_data)
        assert final_data['code_id'] == val

    def test_code_setup_with_commit_id(self):
        val = "f38a8ace"
        incoming_data = {"commit_id": val}
        final_data = {}
        self.snapshot._code_setup(incoming_data, final_data)
        assert final_data['code_id']

    def test_code_setup_with_none(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._code_setup(incoming_data, final_data)
        assert final_data['code_id']

    def test_env_setup_with_none(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._env_setup(incoming_data, final_data)
        assert final_data['environment_id']

    def test_file_setup_with_none(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        assert final_data['file_collection_id']

    def test_file_setup_with_filepaths(self):
        incoming_data = {"filepaths": [self.filepath]}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        assert final_data['file_collection_id']

    def test_config_setup_with_json(self):
        incoming_data = {"config":{"foo":1}}
        final_data = {}
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config']["foo"] == 1

    def test_config_setup_with_filepath(self):
        incoming_data = {"config_filepath": self.config_filepath }
        final_data = {}
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config']["foo"] == 1

    def test_config_setup_with_filename(self):
        incoming_data = {"config_filename": "config.json" }
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config']["foo"] == 1

    def test_config_setup_with_empty(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config'] == {}

    def test_stats_setup_with_json(self):
        incoming_data = {"stats":{"bar":1}}
        final_data = {}
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1

    def test_stats_setup_with_filepath(self):
        incoming_data = {"stats_filepath": self.stats_filepath }
        final_data = {}
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1

    def test_stats_setup_with_empty(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats'] == {}

    def test_stats_setup_with_filename(self):
        incoming_data = {"stats_filename": "stats.json" }
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1