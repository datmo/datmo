import os
import tempfile
import platform
import subprocess

try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestMain():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.execpath = "datmo"
        os.chdir(self.temp_dir)

        # Create environment_driver definition
        self.env_def_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.env_def_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine"))

        # Create config file
        self.config_filepath = os.path.join(self.temp_dir, "config.json")
        with open(self.config_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create stats file
        self.stats_filepath = os.path.join(self.temp_dir, "stats.json")
        with open(self.stats_filepath, "wb") as f:
            f.write(to_bytes(str("{}")))

        # Create test file
        self.filepath = os.path.join(self.temp_dir, "file.txt")
        with open(self.filepath, "wb") as f:
            f.write(to_bytes(str("test")))

        # Create script file
        self.script_filepath = os.path.join(self.temp_dir, "script.py")
        with open(self.script_filepath, "wb") as f:
            f.write(to_bytes(str('print("hello")')))

    def command_run(self, command):
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.temp_dir)
        return p

    def teardown_class(self):
        pass

    def test_version(self):
        try:
            success = True
            p = subprocess.Popen(
                [self.execpath, "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.temp_dir)
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err:
                success = False
            elif "datmo version:" not in out:
                success = False
        except Exception:
            success = False
        assert success

    def test_init(self):
        try:
            success = True
            p = self.command_run([
                self.execpath, "init", "--name", '"test"', "--description",
                '"test"'
            ])
            out, err = p.communicate(to_bytes("\n"))
            out, err = out.decode(), err.decode()
            if err:
                success = False
            elif "Initializing project" not in out:
                success = False
        except Exception:
            success = False
        assert success

    # @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    # def test_run(self):
    #     try:
    #         success = True
    #         p = self.command_run([self.execpath, "run", "python script.py"])
    #         out, err = p.communicate()
    #         out, err = out.decode(), err.decode()
    #         if err:
    #             success = False
    #         elif 'hello' not in out:
    #             success = False
    #     except Exception:
    #         success = False
    #     assert success

    def test_run_ls(self):
        try:
            success = True
            p = self.command_run([self.execpath, "ls"])
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err:
                success = False
            elif 'id' not in out:
                success = False
        except Exception:
            success = False
        assert success

    def test_snapshot_create(self):
        try:
            success = True
            p = self.command_run(
                [self.execpath, "snapshot", "create", "-m", "message"])
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err:
                success = False
            elif 'Created snapshot with id' not in out:
                success = False
        except Exception:
            success = False
        assert success

    def test_snapshot_ls(self):
        try:
            success = True
            p = self.command_run([self.execpath, "snapshot", "ls"])
            out, err = p.communicate()
            out, err = out.decode(), err.decode()
            if err:
                success = False
            elif 'id' not in out:
                success = False
        except Exception:
            success = False
        assert success
