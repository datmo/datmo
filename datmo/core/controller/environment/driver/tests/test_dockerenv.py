"""
Tests for dockerenv.py
"""

import os
import shutil
import tempfile
import platform
import threading
import sys
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue
import uuid
import timeout_decorator
from io import open
try:
    to_unicode = str
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.controller.environment.driver.dockerenv import DockerEnvironmentDriver
from datmo.core.util.exceptions import (
    EnvironmentInitFailed, EnvironmentConnectFailed, FileAlreadyExistsError,
    EnvironmentRequirementsCreateError, EnvironmentImageNotFound,
    EnvironmentContainerNotFound, PathDoesNotExist, EnvironmentDoesNotExist,
    EnvironmentExecutionError)
from datmo.core.util.misc_functions import check_docker_inactive, pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())

class TestDockerEnv():
    # TODO: Add more cases for each test
    """
    Checks all functions of the DockerEnvironmentDriver
    """

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # Ensure the ".datmo" directory is there (this is ensured by higher level functions
        # in practice
        os.makedirs(os.path.join(self.temp_dir, ".datmo"))
        # Test the default parameters
        self.docker_environment_driver = \
            DockerEnvironmentDriver(self.temp_dir, ".datmo")
        self.image_name = str(uuid.uuid1())
        self.random_text = str(uuid.uuid1())
        self.dockerfile_path = os.path.join(self.temp_dir, "Dockerfile")
        with open(self.dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + os.linesep))
            f.write(to_bytes(str("RUN echo " + self.random_text)))

    def teardown_method(self):
        # TODO: abstract the datmo_directory_name
        if not check_docker_inactive(test_datmo_dir, ".datmo"):
            self.docker_environment_driver.remove(self.image_name, force=True)

    def test_instantiation(self):
        assert self.docker_environment_driver != None
        assert self.docker_environment_driver.docker_socket == None or "unix:///var/run/docker.sock"
        assert self.docker_environment_driver.docker_execpath == "docker"
        
        # Check if Docker tests are skipped
        skip_docker_tests = os.environ.get("DATMO_SKIP_DOCKER_TESTS", "0").lower() in ["1", "true", "yes"]
        
        if not skip_docker_tests:
            assert self.docker_environment_driver.client is not None
        
        assert self.docker_environment_driver.prefix
        assert self.docker_environment_driver.type

    def test_init_success(self):
        result = self.docker_environment_driver.init()
        assert result and \
               self.docker_environment_driver.is_initialized == True

    def test_init_failed(self):
        thrown = False
        shutil.rmtree(os.path.join(self.temp_dir, ".datmo"))
        try:
            self.docker_environment_driver.init()
        except EnvironmentInitFailed:
            thrown = True
        assert thrown

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_connect_success(self):
        result = self.docker_environment_driver.connect()
        assert result and \
            self.docker_environment_driver.is_connected

    def test_connect_failed(self):
        thrown = False
        try:
            test = DockerEnvironmentDriver(
                self.temp_dir, ".datmo", docker_socket="unix:///var/run/fooo")
            test.connect()
        except EnvironmentConnectFailed:
            thrown = True
        assert thrown

    # Test environment directory functions
    def test_create_environment_dir(self):
        assert not os.path.isdir(
            self.docker_environment_driver.environment_directory_path)
        result = self.docker_environment_driver.create_environment_dir()
        assert result == True and \
               os.path.isdir(self.docker_environment_driver.environment_directory_path)

    def test_exists_environment_dir(self):
        result = self.docker_environment_driver.exists_environment_dir()
        assert result == False and \
               not os.path.isdir(self.docker_environment_driver.environment_directory_path)
        self.docker_environment_driver.init()
        self.docker_environment_driver.create_environment_dir()
        result = self.docker_environment_driver.exists_environment_dir()
        assert result == True and \
               os.path.isdir(self.docker_environment_driver.environment_directory_path)

    def test_ensure_environment_dir(self):
        result = self.docker_environment_driver.ensure_environment_dir()
        assert result == True and \
               os.path.isdir(self.docker_environment_driver.environment_directory_path)

    def test_delete_environment_dir(self):
        self.docker_environment_driver.init()
        self.docker_environment_driver.create_environment_dir()
        result = self.docker_environment_driver.delete_environment_dir()
        assert result == True and \
               not os.path.isdir(self.docker_environment_driver.environment_directory_path)

    # Other tests
    def test_get_current_type(self):
        result = self.docker_environment_driver.get_environment_types()
        assert result

    def test_get_current_name(self):
        environment_type = "cpu"
        result = self.docker_environment_driver.get_supported_frameworks(
            environment_type)
        assert result

    def test_get_supported_languages(self):
        environment_type = "cpu"
        environment_framework = "data-analytics"
        result = self.docker_environment_driver.get_supported_languages(
            environment_type, environment_framework)
        assert result

    def test_setup(self):
        save_definition_path = os.path.join(
            self.docker_environment_driver.root, "test")

        # Test setup failure if name it not present
        failed = False
        try:
            _ = self.docker_environment_driver.setup(
                options={}, definition_path=save_definition_path)
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        # Test setup failure if name is not a valid name
        failed = False
        try:
            _ = self.docker_environment_driver.setup(
                options={"name": "random"},
                definition_path=save_definition_path)
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        options = {
            "environment_framework": "data-analytics",
            "environment_type": "cpu",
            "environment_language": "py27"
        }

        # Test if failure if the path does not exist
        failed = False
        try:
            _ = self.docker_environment_driver.setup(
                options=options, definition_path=save_definition_path)
        except PathDoesNotExist:
            failed = True
        assert failed

        # Create definition path
        os.makedirs(save_definition_path)

        # Test by passing definition filepath and options
        result = self.docker_environment_driver.setup(
            options=options, definition_path=save_definition_path)
        definition_filepath = os.path.join(save_definition_path, "Dockerfile")
        assert result and os.path.isfile(definition_filepath) and \
               "datmo" in open(definition_filepath, "r").read()

    def test_create(self):
        input_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "Dockerfile")
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "datmoDockerfile")
        # Test both default values
        success, path, output_path = \
            self.docker_environment_driver.create()

        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path

        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)

        # Test default values for output
        success, path, output_path = \
            self.docker_environment_driver.create(input_dockerfile_path)

        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path

        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)

        # Test both values given
        success, path, output_path = \
            self.docker_environment_driver.create(input_dockerfile_path,
                                                        output_dockerfile_path)
        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path

        # Test exception for output path already exists
        failed = False
        try:
            self.docker_environment_driver.create(
                output_path=output_dockerfile_path)
        except FileAlreadyExistsError:
            failed = True
        assert failed

        # Test exception for path does not exist
        os.remove(input_dockerfile_path)
        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_build(self):
        # connect to daemon
        result = self.docker_environment_driver.build(self.image_name,
                                                      self.dockerfile_path)
        assert result == True
        # teardown
        self.docker_environment_driver.remove(self.image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # TODO: add more options for run w/ volumes etc
        # Keeping stdin_open and tty as either (True, True) or (False, False).
        # other combination are not used
        log_filepath = os.path.join(self.docker_environment_driver.root,
                                    "test.log")
        self.docker_environment_driver.build(self.image_name,
                                             self.dockerfile_path)
        # keeping stdin_open and tty as False
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:9999", "5000:5001"],
            "name": str(uuid.uuid1()),
            "volumes": {
                self.docker_environment_driver.root: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            },
            "mem_limit": "4g",
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": False
        }
        return_code, run_id, logs = \
            self.docker_environment_driver.run(self.image_name, run_options, log_filepath)
        assert return_code == 0
        assert run_id
        assert logs
        assert isinstance(logs, str)

        # teardown
        self.docker_environment_driver.stop(run_id, force=True)

        # Test default values for run options
        run_options = {"command": ["sh", "-c", "echo yo"]}
        return_code, run_id, logs = \
            self.docker_environment_driver.run(self.image_name, run_options, log_filepath)
        assert return_code == 0
        assert run_id
        assert logs
        assert isinstance(logs, str)
        # teardown container
        self.docker_environment_driver.stop(run_id, force=True)

    # commenting due to test being unreliable
    # @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    # def test_interactive_run(self):
    #     # keeping stdin_open, tty as True
    #     log_filepath = os.path.join(self.docker_environment_driver.root,
    #                                 "test.log")
    #     self.docker_environment_driver.build(self.image_name,
    #                                          self.dockerfile_path)
    #
    #     @timeout_decorator.timeout(10, use_signals=False)
    #     def timed_run(container_name, timed_run_result):
    #         run_options = {
    #             "command": [],
    #             "ports": ["8888:9999", "5000:5001"],
    #             "name": container_name,
    #             "volumes": {
    #                 self.docker_environment_driver.root: {
    #                     'bind': '/home/',
    #                     'mode': 'rw'
    #                 }
    #             },
    #             "detach": True,
    #             "stdin_open": True,
    #             "tty": True,
    #             "api": False
    #         }
    #
    #         self.docker_environment_driver.run(self.image_name, run_options,
    #                                            log_filepath)
    #         return timed_run_result
    #
    #     container_name = str(uuid.uuid1())
    #     timed_run_result = False
    #     try:
    #         timed_run_result = timed_run(container_name, timed_run_result)
    #     except timeout_decorator.timeout_decorator.TimeoutError:
    #         timed_run_result = True
    #
    #     assert timed_run_result
    #
    #     # teardown
    #     self.docker_environment_driver.remove(self.image_name, force=True)
    #     # remove datmoDockerfile
    #     output_dockerfile_path = os.path.join(self.docker_environment_driver.root,
    #                                           "datmoDockerfile")
    #     os.remove(output_dockerfile_path)
    #
    #     # new jupyter dockerfile
    #     new_docker_filepath = os.path.join(
    #         self.docker_environment_driver.root, "Dockerfile")
    #     random_text = str(uuid.uuid1())
    #     with open(new_docker_filepath, "wb") as f:
    #         f.write(to_bytes("FROM nbgallery/jupyter-alpine:latest\n"))
    #         f.write(to_bytes(str("RUN echo " + random_text)))
    #     self.docker_environment_driver.build(self.image_name,
    #                                          new_docker_filepath)
    #
    #     @timeout_decorator.timeout(10, use_signals=False)
    #     def timed_run(container_name, timed_run_result):
    #         run_options = {
    #             "command": ["jupyter", "notebook", "--allow-root"],
    #             "ports": ["8888:8888"],
    #             "name": container_name,
    #             "volumes": {
    #                 self.docker_environment_driver.root: {
    #                     'bind': '/home/',
    #                     'mode': 'rw'
    #                 }
    #             },
    #             "detach": True,
    #             "stdin_open": False,
    #             "tty": False,
    #             "api": False
    #         }
    #
    #         self.docker_environment_driver.run(self.image_name, run_options,
    #                                            log_filepath)
    #         return timed_run_result
    #
    #     # teardown
    #     self.docker_environment_driver.remove(self.image_name, force=True)
    #     # remove datmoDockerfile
    #     output_dockerfile_path = os.path.join(self.docker_environment_driver.root,
    #                                           "datmoDockerfile")
    #     os.remove(output_dockerfile_path)
    #
    #     # new dockerfile
    #     new_docker_filepath = os.path.join(
    #         self.docker_environment_driver.root, "Dockerfile")
    #     random_text = str(uuid.uuid1())
    #     with open(new_docker_filepath, "wb") as f:
    #         f.write(to_bytes("FROM datmo/python-base:cpu-py27" + os.linesep))
    #         f.write(to_bytes(str("RUN echo " + random_text)))
    #     self.docker_environment_driver.build(self.image_name,
    #                                          new_docker_filepath,
    #                                          workspace='notebook')
    #
    #     @timeout_decorator.timeout(10, use_signals=False)
    #     def timed_run(container_name, timed_run_result):
    #         run_options = {
    #             "command": ["jupyter", "notebook", "--allow-root"],
    #             "ports": ["8888:8888"],
    #             "name": container_name,
    #             "volumes": {
    #                 self.docker_environment_driver.root: {
    #                     'bind': '/home/',
    #                     'mode': 'rw'
    #                 }
    #             },
    #             "detach": True,
    #             "stdin_open": False,
    #             "tty": False,
    #             "api": False
    #         }
    #
    #         self.docker_environment_driver.run(self.image_name, run_options,
    #                                            log_filepath)
    #         return timed_run_result
    #
    #     container_name = str(uuid.uuid1())
    #     timed_run_result = False
    #     try:
    #         timed_run_result = timed_run(container_name, timed_run_result)
    #     except timeout_decorator.timeout_decorator.TimeoutError:
    #         timed_run_result = True
    #     assert timed_run_result
    #
    #     # teardown container
    #     self.docker_environment_driver.stop(container_name, force=True)
    #
    #     # remove datmoDockerfile
    #     output_dockerfile_path = os.path.join(self.docker_environment_driver.root,
    #                                           "datmoDockerfile")
    #     os.remove(output_dockerfile_path)
    #
    #     # new dockerfile
    #     new_docker_filepath = os.path.join(
    #         self.docker_environment_driver.root, "Dockerfile")
    #     random_text = str(uuid.uuid1())
    #     with open(new_docker_filepath, "wb") as f:
    #         f.write(to_bytes("FROM datmo/python-base:cpu-py27" + os.linesep))
    #         f.write(to_bytes(str("RUN echo " + random_text)))
    #     self.docker_environment_driver.build(self.image_name,
    #                                          new_docker_filepath,
    #                                          workspace='notebook')
    #
    #     @timeout_decorator.timeout(10, use_signals=False)
    #     def timed_run(container_name, timed_run_result):
    #         run_options = {
    #             "command": ["jupyter", "notebook", "--allow-root"],
    #             "ports": ["8888:8888"],
    #             "name": container_name,
    #             "volumes": {
    #                 self.docker_environment_driver.root: {
    #                     'bind': '/home/',
    #                     'mode': 'rw'
    #                 }
    #             },
    #             "detach": True,
    #             "stdin_open": False,
    #             "tty": False,
    #             "api": False
    #         }
    #
    #         self.docker_environment_driver.run(self.image_name, run_options,
    #                                            log_filepath)
    #         return timed_run_result
    #
    #     container_name = str(uuid.uuid1())
    #     timed_run_result = False
    #     try:
    #         timed_run_result = timed_run(container_name, timed_run_result)
    #     except timeout_decorator.timeout_decorator.TimeoutError:
    #         timed_run_result = True
    #     assert timed_run_result
    #
    #     # teardown container
    #     self.docker_environment_driver.stop(container_name, force=True)
    #
    #     # remove datmoDockerfile
    #     output_dockerfile_path = os.path.join(self.docker_environment_driver.root,
    #                                           "datmoDockerfile")
    #     os.remove(output_dockerfile_path)
    #
    #     # new dockerfile
    #     new_docker_filepath = os.path.join(
    #         self.docker_environment_driver.root, "Dockerfile")
    #     random_text = str(uuid.uuid1())
    #     with open(new_docker_filepath, "wb") as f:
    #         f.write(to_bytes("FROM datmo/python-base:cpu-py27" + os.linesep))
    #         f.write(to_bytes(str("RUN echo " + random_text)))
    #     self.docker_environment_driver.build(self.image_name,
    #                                          new_docker_filepath,
    #                                          workspace='jupyterlab')
    #
    #     @timeout_decorator.timeout(10, use_signals=False)
    #     def timed_run(container_name, timed_run_result):
    #         run_options = {
    #             "command": ["jupyter", "lab", "--allow-root"],
    #             "ports": ["8888:8888"],
    #             "name": container_name,
    #             "volumes": {
    #                 self.docker_environment_driver.root: {
    #                     'bind': '/home/',
    #                     'mode': 'rw'
    #                 }
    #             },
    #             "detach": True,
    #             "stdin_open": False,
    #             "tty": False,
    #             "api": False
    #         }
    #
    #         self.docker_environment_driver.run(self.image_name, run_options,
    #                                            log_filepath)
    #         return timed_run_result
    #
    #     container_name = str(uuid.uuid1())
    #     timed_run_result = False
    #     try:
    #         timed_run_result = timed_run(container_name, timed_run_result)
    #     except timeout_decorator.timeout_decorator.TimeoutError:
    #         timed_run_result = True
    #     assert timed_run_result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop(self):
        log_filepath = os.path.join(self.docker_environment_driver.root,
                                    "test.log")
        self.docker_environment_driver.build(self.image_name,
                                             self.dockerfile_path)

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:9999", "5000:5001"],
            "name": str(uuid.uuid1()),
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "api": False
        }
        _, run_id, _ = \
            self.docker_environment_driver.run(self.image_name, run_options, log_filepath)
        result = self.docker_environment_driver.stop(run_id, force=True)
        assert result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove(self):
        # Test if no image present and no containers
        result = self.docker_environment_driver.remove(self.image_name)
        assert result == True

        # Without force
        self.docker_environment_driver.build(self.image_name,
                                             self.dockerfile_path)
        result = self.docker_environment_driver.remove(self.image_name)
        assert result == True
        # remove datmoDockerfile
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "datmoDockerfile")
        os.remove(output_dockerfile_path)

        # With force
        self.docker_environment_driver.build(self.image_name,
                                             self.dockerfile_path)
        result = self.docker_environment_driver.remove(
            self.image_name, force=True)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_tags_for_docker_repository(self):
        result = self.docker_environment_driver.get_tags_for_docker_repository(
            "hello-world")
        assert 'latest' in result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_build_image(self):
        result = self.docker_environment_driver.build_image(
            self.image_name, self.dockerfile_path)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_image(self):
        failed = False
        try:
            self.docker_environment_driver.get_image("random")
        except EnvironmentImageNotFound:
            failed = True
        assert failed

        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)

        result = self.docker_environment_driver.get_image(self.image_name)
        tags = result.__dict__['attrs']['RepoTags']
        assert self.image_name + ":latest" in tags

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_list_images(self):
        # TODO: Test out all input permutations
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        # List images without all flag
        result = self.docker_environment_driver.list_images()
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert self.image_name + ":latest" in group_flat
        # List images with all flag
        result = self.docker_environment_driver.list_images(all_images=True)
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert self.image_name + ":latest" in group_flat

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_search_images(self):
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        result = self.docker_environment_driver.search_images(self.image_name)
        assert len(result) > 0

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove_image(self):
        # Failure without force
        failure = False
        try:
            _ = self.docker_environment_driver.remove_image("random")
        except EnvironmentExecutionError:
            failure = True
        assert failure == True
        # Failure with force
        failure = False
        try:
            _ = self.docker_environment_driver.remove_image(
                "random", force=True)
        except EnvironmentExecutionError:
            failure = True
        assert failure == True
        # Without force
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        result = self.docker_environment_driver.remove_image(self.image_name)
        assert result == True
        # remove datmoDockerfile
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "datmoDockerfile")
        os.remove(output_dockerfile_path)
        # With force
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        result = self.docker_environment_driver.remove_image(
            self.image_name, force=True)
        assert result == True
        # remove datmoDockerfile
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "datmoDockerfile")
        os.remove(output_dockerfile_path)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove_images(self):
        # TODO: Test out all input permutations
        # Without force
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        result = self.docker_environment_driver.remove_images(
            name=self.image_name)
        assert result == True
        # remove datmoDockerfile
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "datmoDockerfile")
        os.remove(output_dockerfile_path)
        # With force
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        result = self.docker_environment_driver.remove_images(
            name=self.image_name, force=True)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_container(self):
        # TODO: test with all variables provided
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        # With default parameters
        return_code, container_id = \
            self.docker_environment_driver.run_container(self.image_name)
        assert return_code == 0 and \
            container_id
        # teardown container
        self.docker_environment_driver.stop(container_id, force=True)
        # With api=True, detach=False
        logs = self.docker_environment_driver.run_container(
            self.image_name, api=True)
        assert logs == ""
        # With api=True, detach=True
        container_obj = self.docker_environment_driver.run_container(
            self.image_name, api=True, detach=True)
        assert container_obj

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_extract_workspace_url(self):
        # TODO: test with all variables provided
        with open(self.dockerfile_path, "wb") as f:
            f.write(
                to_bytes(
                    "FROM datmo/python-base:cpu-py27-notebook" + os.linesep))
            f.write(to_bytes(str("RUN echo " + self.random_text)))
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)

        random_container_id = str(uuid.uuid1())
        my_queue = queue.Queue()

        def dummy(self, name, workspace, out_queue):
            workspace_url = self.docker_environment_driver.extract_workspace_url(
                name, workspace)
            out_queue.put(workspace_url)

        @timeout_decorator.timeout(20, use_signals=False)
        def timed_run(self):
            return_code, container_id = \
                self.docker_environment_driver.run_container(self.image_name,
                                                             name=random_container_id,
                                                             command=['jupyter', 'notebook', '--allow-root'])
            return return_code, container_id

        thread = threading.Thread(
            target=dummy,
            args=(self, random_container_id, "notebook", my_queue))
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

        timed_run_result = False
        try:
            _, _ = timed_run(self)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True
        thread.join()
        assert timed_run_result
        # asserting the workspace url to be passed
        workspace_url = my_queue.get()  # get the workspace url
        assert 'http' in workspace_url

        # Test when there is no container being run
        workspace_url = self.docker_environment_driver.extract_workspace_url(
            self.image_name, "notebook")
        assert workspace_url == None

        # teardown container
        self.docker_environment_driver.stop(random_container_id, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_container(self):
        failed = False
        try:
            self.docker_environment_driver.get_container("random")
        except EnvironmentContainerNotFound:
            failed = True
        assert failed

        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            self.image_name)
        result = self.docker_environment_driver.get_container(container_id)
        assert result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_list_containers(self):
        # TODO: Test out all input permutations
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            self.image_name, detach=True)
        result = self.docker_environment_driver.list_containers()
        assert container_id and len(result) > 0
        # teardown
        self.docker_environment_driver.remove(self.image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_container(self):
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            self.image_name)
        result = self.docker_environment_driver.stop_container(container_id)
        assert result == True
        result = self.docker_environment_driver.get_container(container_id)
        assert result.__dict__['attrs']['State']['Status'] == "exited"

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove_container(self):
        # Failure random container id (no force)
        failure = False
        try:
            _ = self.docker_environment_driver.remove_container("random")
        except EnvironmentExecutionError:
            failure = True
        assert failure == True
        # Failure random container id (force)
        failure = False
        try:
            _ = self.docker_environment_driver.remove_container(
                "random", force=True)
        except EnvironmentExecutionError:
            failure = True
        assert failure == True
        # Without force
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            self.image_name)
        result = self.docker_environment_driver.remove_container(container_id)
        assert result == True
        # With force
        _, container_id = self.docker_environment_driver.run_container(
            self.image_name)
        result = self.docker_environment_driver.remove_container(
            container_id, force=True)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_log_container(self):
        # TODO: Do a more comprehensive test, test out optional variables
        # TODO: Test out more commands at the system level
        log_filepath = os.path.join(self.docker_environment_driver.root,
                                    "test.log")
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        _, container_id = \
            self.docker_environment_driver.run_container(self.image_name,
                                                          command=["sh", "-c", "echo yo"])
        return_code, logs = self.docker_environment_driver.log_container(
            container_id, log_filepath)
        assert return_code == 0
        assert logs and \
               os.path.exists(log_filepath)

        with open(log_filepath, "r") as f:
            assert f.readline() != ""

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_remove_containers_by_term(self):
        # 1) Test with image_name (random container name), match with image_name
        # 2) Test with image_name and name given, match with name
        self.docker_environment_driver.build_image(self.image_name,
                                                   self.dockerfile_path)
        # 1) Test option 1

        # Test without force
        self.docker_environment_driver.run_container(self.image_name)
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            self.image_name)
        assert result == True
        # Test with force
        self.docker_environment_driver.run_container(self.image_name)
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            self.image_name, force=True)
        assert result == True

        # 2) Test option 2
        self.docker_environment_driver.run_container(
            self.image_name, name="datmo_test")
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            "datmo_test")
        assert result == True
        # Test with force
        self.docker_environment_driver.run_container(
            self.image_name, name="datmo_test")
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            "datmo_test", force=True)
        assert result == True

    def test_create_requirements_file(self):
        # 1) Test failure EnvironmentDoesNotExist
        # 2) Test success
        # 3) Test failure EnvironmentRequirementsCreateError
        # 1) Test option 1
        result = self.docker_environment_driver.create_requirements_file()
        assert os.path.isfile(result) and \
               "datmo" in open(result, "r").read()

        # 2) Test option 2
        # Since it uses pip as package manager, it doesn't extract any other package than what
        # has already been installed in local
        script_path = os.path.join(self.docker_environment_driver.root,
                                   "script.py")
        with open(script_path, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))
        # Test default
        result = self.docker_environment_driver.create_requirements_file()
        assert result
        assert os.path.isfile(result) and \
               "datmo" in open(result, "r").read()

        # 3) Test option 3
        exception_thrown = False
        try:
            _ = self.docker_environment_driver.\
                create_requirements_file(package_manager="does_not_work")
        except EnvironmentRequirementsCreateError:
            exception_thrown = True

        assert exception_thrown

    def test_create_default_dockerfile(self):
        # 1) Create default dockerfile for default script present

        # 1) Test option 1
        script_path = os.path.join(self.docker_environment_driver.root,
                                   "script.py")
        with open(script_path, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))

        result = self.docker_environment_driver.\
            create_default_definition(directory=self.docker_environment_driver.root)

        assert result
        assert os.path.isfile(result)
        output = open(result, "r").read()
        print(repr(output))
        assert "python" in output

    def test_create_datmo_definition(self):
        # Test 1
        input_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "Dockerfile")
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.root, "datmoDockerfile")
        result = self.docker_environment_driver.create_datmo_definition(
            input_dockerfile_path, output_dockerfile_path)
        assert result
        assert os.path.isfile(output_dockerfile_path)
        output = open(output_dockerfile_path, "r").read()
        print(repr(output))
        assert "datmo essential" in output

        # Test 2: With workspaces on datmo base image
        os.remove(output_dockerfile_path)
        with open(input_dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM datmo/python-base:cpu-py27" + os.linesep))
            f.write(to_bytes(str("RUN echo " + self.random_text)))
        result = self.docker_environment_driver.create_datmo_definition(
            input_dockerfile_path,
            output_dockerfile_path,
            workspace="notebook")
        assert result
        assert os.path.isfile(output_dockerfile_path)
        output = open(output_dockerfile_path, "r").read()
        print(repr(output))
        assert "FROM datmo/python-base:cpu-py27-notebook" in output
        assert "datmo essential" in output

        # Test 3: With workspaces on datmo base image with jupyterlab
        os.remove(output_dockerfile_path)
        with open(input_dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM datmo/python-base:cpu-py27" + "\n"))
            f.write(to_bytes(str("RUN echo " + self.random_text)))
        result = self.docker_environment_driver.create_datmo_definition(
            input_dockerfile_path,
            output_dockerfile_path,
            workspace="jupyterlab")
        assert result
        assert os.path.isfile(output_dockerfile_path)
        output = open(output_dockerfile_path, "r").read()
        print(repr(output))
        assert "FROM datmo/python-base:cpu-py27-jupyterlab" in output
        assert "datmo essential" in output

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_gpu_enabled(self):
        if not self.docker_environment_driver.gpu_enabled():
            print("GPU not available")
        else:
            log_filepath = os.path.join(self.docker_environment_driver.root,
                                        "test.log")
            return_code, run_id, logs = self.docker_environment_driver.run(
                "nvidia/cuda", {
                    "command": ["nvidia-smi"],
                    "name": str(uuid.uuid1()),
                    "detach": True,
                    "gpu": True
                }, log_filepath)
            assert return_code == 0
