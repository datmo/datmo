"""
Tests for dockerenv.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import platform
import uuid
import timeout_decorator
from io import open
try:
    to_unicode = unicode
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
    EnvironmentInitFailed, FileAlreadyExistsError,
    EnvironmentRequirementsCreateError, EnvironmentImageNotFound,
    EnvironmentContainerNotFound)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

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
        # Test the default parameters
        self.docker_environment_driver = \
            DockerEnvironmentDriver(self.temp_dir)

        random_text = str(uuid.uuid1())
        with open(os.path.join(self.temp_dir, "Dockerfile"), "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))

    def teardown_method(self):
        self.docker_environment_driver.stop_remove_containers_by_term(
            term='cooltest', force=True)

    def test_instantiation(self):
        assert self.docker_environment_driver != None
        assert self.docker_environment_driver.docker_socket == None or "unix:///var/run/docker.sock"
        assert self.docker_environment_driver.docker_execpath == "docker"
        assert self.docker_environment_driver.client
        assert self.docker_environment_driver.prefix
        assert self.docker_environment_driver.type

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_init_success(self):
        init_result = self.docker_environment_driver.init()
        assert init_result and \
               self.docker_environment_driver.is_initialized == True

    def test_init_failed(self):
        thrown = False
        try:
            test = DockerEnvironmentDriver(
                self.temp_dir, docker_socket="unix:///var/run/fooo")
            test.init()
        except EnvironmentInitFailed:
            thrown = True
        assert thrown

    def test_create(self):
        input_dockerfile_path = os.path.join(
            self.docker_environment_driver.filepath, "Dockerfile")
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.filepath, "datmoDockerfile")
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
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_driver.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        result = self.docker_environment_driver.build(name, path)
        assert result == True
        # teardown
        self.docker_environment_driver.remove(name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # TODO: add more options for run w/ volumes etc
        # Keeping stdin_open and tty as either (True, True) or (False, False).
        # other combination are not used
        image_name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_driver.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_driver.filepath,
                                    "test.log")
        self.docker_environment_driver.build(image_name, path)
        # keeping stdin_open and tty as False
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:9999", "5000:5001"],
            "name": str(uuid.uuid1()),
            "volumes": {
                self.docker_environment_driver.filepath: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            },
            "detach": True,
            "stdin_open": False,
            "tty": False,
            "api": False
        }
        return_code, run_id, logs = \
            self.docker_environment_driver.run(image_name, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs
        assert isinstance(logs, str)

        # teardown
        self.docker_environment_driver.stop(run_id, force=True)

        # Test default values for run options
        run_options = {"command": ["sh", "-c", "echo yo"]}
        return_code, run_id, logs = \
            self.docker_environment_driver.run(image_name, run_options, log_filepath)
        assert return_code == 0
        assert run_id
        assert logs
        assert isinstance(logs, str)
        # teardown container
        self.docker_environment_driver.stop(run_id, force=True)

        # teardown image
        self.docker_environment_driver.remove(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_interactive_run(self):
        # keeping stdin_open, tty as True
        # build image
        image_name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_driver.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "wb") as f:
            f.write(to_bytes("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_driver.filepath,
                                    "test.log")
        self.docker_environment_driver.build(image_name, path)

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run_result):
            run_options = {
                "command": [],
                "ports": ["8888:9999", "5000:5001"],
                "name": container_name,
                "volumes": {
                    self.docker_environment_driver.filepath: {
                        'bind': '/home/',
                        'mode': 'rw'
                    }
                },
                "detach": True,
                "stdin_open": True,
                "tty": True,
                "api": False
            }

            self.docker_environment_driver.run(image_name, run_options,
                                               log_filepath)
            return timed_run_result

        container_name = str(uuid.uuid1())
        timed_run_result = False
        try:
            timed_run_result = timed_run(container_name, timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True

        assert timed_run_result

        # teardown container
        self.docker_environment_driver.stop(container_name, force=True)

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run_result):
            run_options = {
                "command": ["jupyter", "notebook"],
                "ports": ["8888:8888"],
                "name": container_name,
                "volumes": {
                    self.docker_environment_driver.filepath: {
                        'bind': '/home/',
                        'mode': 'rw'
                    }
                },
                "detach": True,
                "stdin_open": False,
                "tty": False,
                "api": False
            }

            self.docker_environment_driver.run(image_name, run_options,
                                               log_filepath)
            return timed_run_result

        container_name = str(uuid.uuid1())
        timed_run_result = False
        try:
            timed_run_result = timed_run(container_name, timed_run_result)
        except timeout_decorator.timeout_decorator.TimeoutError:
            timed_run_result = True
        assert timed_run_result

        # teardown container
        self.docker_environment_driver.stop(container_name, force=True)

        # teardown image
        self.docker_environment_driver.remove(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop(self):
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_driver.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_driver.filepath,
                                    "test.log")
        self.docker_environment_driver.build(name, path)

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
            self.docker_environment_driver.run(name, run_options, log_filepath)
        result = self.docker_environment_driver.stop(run_id, force=True)
        assert result
        # teardown
        self.docker_environment_driver.remove(name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove(self):
        name = str(uuid.uuid1())
        # Test if no image present and no containers
        result = self.docker_environment_driver.remove(name)
        assert result == True

        path = os.path.join(self.docker_environment_driver.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_driver.build(name, path)
        result = self.docker_environment_driver.remove(name)
        assert result == True

        # With force
        self.docker_environment_driver.build(name, path)
        # teardown
        result = self.docker_environment_driver.remove(name, force=True)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_tags_for_docker_repository(self):
        result = self.docker_environment_driver.get_tags_for_docker_repository(
            "hello-world")
        assert 'latest' in result

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_build_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        result = self.docker_environment_driver.build_image(
            image_name, dockerfile_path)
        assert result == True
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_image(self):
        failed = False
        try:
            self.docker_environment_driver.get_image("random")
        except EnvironmentImageNotFound:
            failed = True
        assert failed

        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)

        result = self.docker_environment_driver.get_image(image_name)
        tags = result.__dict__['attrs']['RepoTags']
        assert image_name + ":latest" in tags
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_list_images(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        # List images without all flag
        result = self.docker_environment_driver.list_images()
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert image_name + ":latest" in group_flat
        # List images with all flag
        result = self.docker_environment_driver.list_images(all_images=True)
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert image_name + ":latest" in group_flat
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_search_images(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        result = self.docker_environment_driver.search_images(image_name)
        assert len(result) > 0
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        result = self.docker_environment_driver.remove_image(image_name)
        assert result == True
        # With force
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        result = self.docker_environment_driver.remove_image(
            image_name, force=True)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove_images(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        result = self.docker_environment_driver.remove_images(name=image_name)
        assert result == True
        # With force
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        result = self.docker_environment_driver.remove_images(
            name=image_name, force=True)
        assert result == True

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run_container(self):
        # TODO: test with all variables provided
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        # With default parameters
        return_code, container_id = \
            self.docker_environment_driver.run_container(image_name)
        assert return_code == 0 and \
            container_id
        # teardown container
        self.docker_environment_driver.stop(container_id, force=True)
        # With api=True, detach=False
        logs = self.docker_environment_driver.run_container(
            image_name, api=True)
        assert logs == ""
        # With api=True, detach=True
        container_obj = self.docker_environment_driver.run_container(
            image_name, api=True, detach=True)
        assert container_obj
        self.docker_environment_driver.stop_remove_containers_by_term(
            image_name, force=True)
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_get_container(self):
        failed = False
        try:
            self.docker_environment_driver.get_container("random")
        except EnvironmentContainerNotFound:
            failed = True
        assert failed

        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            image_name)
        result = self.docker_environment_driver.get_container(container_id)
        assert result
        self.docker_environment_driver.stop_remove_containers_by_term(
            image_name, force=True)
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_list_containers(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            image_name, detach=True)
        result = self.docker_environment_driver.list_containers()
        assert container_id and len(result) > 0
        self.docker_environment_driver.stop_remove_containers_by_term(
            image_name, force=True)
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            image_name)
        result = self.docker_environment_driver.stop_container(container_id)
        assert result == True
        result = self.docker_environment_driver.get_container(container_id)
        assert result.__dict__['attrs']['State']['Status'] == "exited"
        self.docker_environment_driver.stop_remove_containers_by_term(
            image_name, force=True)
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_remove_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_driver.run_container(
            image_name)
        result = self.docker_environment_driver.remove_container(container_id)
        assert result == True
        # With force
        _, container_id = self.docker_environment_driver.run_container(
            image_name)
        result = self.docker_environment_driver.remove_container(
            container_id, force=True)
        assert result == True
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_log_container(self):
        # TODO: Do a more comprehensive test, test out optional variables
        # TODO: Test out more commands at the system level
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_driver.filepath,
                                    "test.log")
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        _, container_id = \
            self.docker_environment_driver.run_container(image_name,
                                                          command=["sh", "-c", "echo yo"])
        return_code, logs = self.docker_environment_driver.log_container(
            container_id, log_filepath)
        assert return_code == 0
        assert logs and \
               os.path.exists(log_filepath)

        with open(log_filepath, "r") as f:
            assert f.readline() != ""

        self.docker_environment_driver.stop_remove_containers_by_term(
            image_name, force=True)
        self.docker_environment_driver.remove_image(image_name, force=True)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_stop_remove_containers_by_term(self):
        # 1) Test with image_name (random container name), match with image_name
        # 2) Test with image_name and name given, match with name
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_driver.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "wb") as f:
            f.write(to_bytes("FROM python:3.5-alpine" + "\n"))
            f.write(to_bytes(str("RUN echo " + random_text)))
        self.docker_environment_driver.build_image(image_name, dockerfile_path)
        # 1) Test option 1

        # Test without force
        self.docker_environment_driver.run_container(image_name)
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            image_name)
        assert result == True
        # Test with force
        self.docker_environment_driver.run_container(image_name)
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            image_name, force=True)
        assert result == True

        # 2) Test option 2
        self.docker_environment_driver.run_container(
            image_name, name="datmo_test")
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            "datmo_test")
        assert result == True
        # Test with force
        self.docker_environment_driver.run_container(
            image_name, name="datmo_test")
        result = self.docker_environment_driver.stop_remove_containers_by_term(
            "datmo_test", force=True)
        assert result == True
        self.docker_environment_driver.remove_image(image_name, force=True)

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
        script_path = os.path.join(self.docker_environment_driver.filepath,
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
        script_path = os.path.join(self.docker_environment_driver.filepath,
                                   "script.py")
        with open(script_path, "wb") as f:
            f.write(to_bytes("import numpy\n"))
            f.write(to_bytes("import sklearn\n"))

        result = self.docker_environment_driver.\
            create_default_definition(directory=self.docker_environment_driver.filepath)

        assert result
        assert os.path.isfile(result)
        output = open(result, "r").read()
        print(repr(output))
        assert "python" in output

    def test_create_datmo_definition(self):
        input_dockerfile_path = os.path.join(
            self.docker_environment_driver.filepath, "Dockerfile")
        output_dockerfile_path = os.path.join(
            self.docker_environment_driver.filepath, "datmoDockerfile")
        result = self.docker_environment_driver.create_datmo_definition(
            input_dockerfile_path, output_dockerfile_path)
        assert result
        assert os.path.isfile(output_dockerfile_path)
        output = open(output_dockerfile_path, "r").read()
        print(repr(output))
        assert "datmo essential" in output

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_gpu_enabled(self):
        if not self.docker_environment_driver.gpu_enabled():
            print("GPU not available")
        else:
            log_filepath = os.path.join(
                self.docker_environment_driver.filepath, "test.log")
            return_code, run_id, logs = self.docker_environment_driver.run(
                "nvidia/cuda", {
                    "command": ["nvidia-smi"],
                    "name": str(uuid.uuid1()),
                    "detach": True,
                    "gpu": True
                }, log_filepath)
            assert return_code == 0
