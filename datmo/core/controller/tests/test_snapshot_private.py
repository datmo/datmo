"""
Tests for SnapshotController
"""
import os
import tempfile
import platform
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
from datmo.core.util.exceptions import CommitDoesNotExist

class TestSnapshotController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        Config().set_home(self.temp_dir)

        self.project = ProjectController()
        self.project.init("test", "test description")
        self.snapshot = SnapshotController()

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create config
        self.config_filepath = os.path.join(self.snapshot.home, "config.json")
        with open(self.config_filepath, "wb") as f:
            f.write(to_bytes(str('{"foo":1}')))

        # Create stats
        self.stats_filepath = os.path.join(self.snapshot.home, "stats.json")
        with open(self.stats_filepath, "wb") as f:
            f.write(to_bytes(str('{"bar":1}')))

        # Create test file
        self.filepath = os.path.join(self.snapshot.home, "file.txt")
        with open(self.filepath, "wb") as f:
            f.write(to_bytes(str("test")))

    def teardown_method(self):
        pass

    def test_code_setup_with_code_id(self):
        val = 1
        incoming_data = {"code_id": val}
        final_data = {}
        self.snapshot._code_setup(incoming_data, final_data)
        assert final_data['code_id'] == val

    def test_code_setup_with_commit_id(self):
        # Test failure
        non_existant_commit_id = "f38a8ace"
        incoming_data = {"commit_id": non_existant_commit_id}
        final_data = {}
        failed = False
        try:
            self.snapshot._code_setup(incoming_data, final_data)
        except CommitDoesNotExist:
            failed = True
        assert failed
        # Test success
        commit_id = self.snapshot.code_driver.create_ref()
        incoming_data = {"commit_id": commit_id}
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

    def test_file_setup_with_paths(self):
        incoming_data = {"paths": [self.filepath]}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        assert final_data['file_collection_id']

    def test_config_setup_with_json(self):
        incoming_data = {"config": {"foo": 1}}
        final_data = {}
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config']["foo"] == 1

    def test_config_setup_with_filepath(self):
        incoming_data = {"config_filepath": self.config_filepath}
        final_data = {}
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config']["foo"] == 1

    def test_config_setup_with_filename(self):
        incoming_data = {"config_filename": "config.json"}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data['config']["foo"] == 1

    def test_config_setup_with_empty_and_file(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data["config"]["foo"] == 1

    def test_config_setup_with_empty_no_file(self):
        os.remove(os.path.join(self.snapshot.home, "config.json"))
        incoming_data = {}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._config_setup(incoming_data, final_data)
        assert final_data["config"] == {}

    def test_stats_setup_with_json(self):
        incoming_data = {"stats": {"bar": 1}}
        final_data = {}
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1

    def test_stats_setup_with_filepath(self):
        incoming_data = {"stats_filepath": self.stats_filepath}
        final_data = {}
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1

    def test_stats_setup_with_filename(self):
        incoming_data = {"stats_filename": "stats.json"}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1

    def test_stats_setup_with_empty_with_file(self):
        incoming_data = {}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data['stats']["bar"] == 1

    def test_stats_setup_with_empty_no_file(self):
        os.remove(os.path.join(self.snapshot.home, "stats.json"))
        incoming_data = {}
        final_data = {}
        self.snapshot._file_setup(incoming_data, final_data)
        self.snapshot._stats_setup(incoming_data, final_data)
        assert final_data["stats"] == {}
