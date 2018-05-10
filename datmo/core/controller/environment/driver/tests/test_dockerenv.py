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

from datmo.core.controller.environment.driver.dockerenv import DockerEnvironmentDriver
from datmo.core.util.exceptions import (
    EnvironmentInitFailed, FileAlreadyExistsException,
    EnvironmentRequirementsCreateException, EnvironmentDoesNotExist,
    EnvironmentImageNotFound, EnvironmentContainerNotFound)


class TestDockerEnv():
    # TODO: Add more cases for each test
    """
    Checks all functions of the DockerEnvironmentDriver
    """

    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # Test the default parameters
        self.docker_environment_manager = \
            DockerEnvironmentDriver(self.temp_dir)
        self.init_result = self.docker_environment_manager.init()
        random_text = str(uuid.uuid1())
        with open(os.path.join(self.temp_dir, "Dockerfile"), "a+") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))

    def teardown_method(self):
        self.docker_environment_manager.stop_remove_containers_by_term(
            term='cooltest', force=True)

    def test_instantiation_and_connected(self):
        assert self.docker_environment_manager.is_connected
        assert self.docker_environment_manager != None

    def test_instantiation_not_connected(self):
        thrown = False
        try:
            DockerEnvironmentDriver(
                self.temp_dir, docker_socket="unix:///var/run/fooo")
        except EnvironmentInitFailed:
            thrown = True
        assert thrown

    def test_create(self):
        input_dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        output_dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "datmoDockerfile")
        # Test both default values
        success, path, output_path, requirements_filepath = \
            self.docker_environment_manager.create()

        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        assert requirements_filepath == None

        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)

        # Test default values for output
        success, path, output_path, requirements_filepath = \
            self.docker_environment_manager.create(input_dockerfile_path)

        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        assert requirements_filepath == None

        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)

        # Test both values given
        success, path, output_path, requirements_filepath = \
            self.docker_environment_manager.create(input_dockerfile_path,
                                                        output_dockerfile_path)
        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        assert requirements_filepath == None

        # Test for language being passed in
        os.remove(input_dockerfile_path)
        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)

        script_path = os.path.join(self.docker_environment_manager.filepath,
                                   "script.py")
        with open(script_path, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
        success, path, output_path, requirements_filepath = \
            self.docker_environment_manager.create(language="python3")
        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        assert requirements_filepath and os.path.isfile(requirements_filepath) and \
               "numpy" in open(requirements_filepath, "r").read()

        # Test exception for path does not exist
        os.remove(input_dockerfile_path)
        open(output_dockerfile_path, "r").close()
        os.remove(output_dockerfile_path)
        success, path, output_path, requirements_filepath =\
            self.docker_environment_manager.create()
        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        assert requirements_filepath

        # Test exception for output path already exists
        failed = False
        try:
            self.docker_environment_manager.create(
                output_path=output_dockerfile_path)
        except FileAlreadyExistsException:
            failed = True
        assert failed

    def test_build(self):
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        result = self.docker_environment_manager.build(name, path)
        assert result == True
        # teardown
        self.docker_environment_manager.remove(name, force=True)

        # test
        os.remove(path)
        script_path = os.path.join(self.docker_environment_manager.filepath,
                                   "script.py")

        with open(script_path, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))

        success, path, output_path, requirements_filepath = \
            self.docker_environment_manager.create(language="python3")

        assert success and \
               os.path.isfile(path) and \
               "datmo" in open(output_path, "r").read()
        assert requirements_filepath and os.path.isfile(requirements_filepath) and \
               "numpy" in open(requirements_filepath, "r").read()

        result = self.docker_environment_manager.build(name, path)
        assert result == True
        # teardown
        self.docker_environment_manager.remove(name, force=True)

    def test_run(self):
        # TODO: add more options for run w/ volumes etc
        # Keeping stdin_open and tty as either (True, True) or (False, False).
        # other combination are not used
        image_name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build(image_name, path)
        # keeping stdin_open and tty as False
        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:9999", "5000:5001"],
            "name": str(uuid.uuid1()),
            "volumes": {
                self.docker_environment_manager.filepath: {
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
            self.docker_environment_manager.run(image_name, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs

        # teardown
        self.docker_environment_manager.stop(run_id, force=True)

        # Test default values for run options
        run_options = {"command": ["sh", "-c", "echo yo"]}
        return_code, run_id, logs = \
            self.docker_environment_manager.run(image_name, run_options, log_filepath)
        assert return_code == 0
        assert run_id
        assert logs
        # teardown container
        self.docker_environment_manager.stop(run_id, force=True)

        # teardown image
        self.docker_environment_manager.remove(image_name, force=True)

    def test_interactive_run(self):
        # keeping stdin_open, tty as True
        # build image
        image_name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build(image_name, path)

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run_result):
            run_options = {
                "command": [],
                "ports": ["8888:9999", "5000:5001"],
                "name": container_name,
                "volumes": {
                    self.docker_environment_manager.filepath: {
                        'bind': '/home/',
                        'mode': 'rw'
                    }
                },
                "detach": True,
                "stdin_open": True,
                "tty": True,
                "api": False
            }

            self.docker_environment_manager.run(image_name, run_options,
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
        self.docker_environment_manager.stop(container_name, force=True)

        @timeout_decorator.timeout(10, use_signals=False)
        def timed_run(container_name, timed_run_result):
            run_options = {
                "command": ["jupyter", "notebook"],
                "ports": ["8888:8888"],
                "name": container_name,
                "volumes": {
                    self.docker_environment_manager.filepath: {
                        'bind': '/home/',
                        'mode': 'rw'
                    }
                },
                "detach": True,
                "stdin_open": False,
                "tty": False,
                "api": False
            }

            self.docker_environment_manager.run(image_name, run_options,
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
        self.docker_environment_manager.stop(container_name, force=True)

        # teardown image
        self.docker_environment_manager.remove(image_name, force=True)

    def test_stop(self):
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build(name, path)

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
            self.docker_environment_manager.run(name, run_options, log_filepath)
        result = self.docker_environment_manager.stop(run_id, force=True)
        assert result
        # teardown
        self.docker_environment_manager.remove(name, force=True)

    def test_remove(self):
        name = str(uuid.uuid1())
        # Test if no image present and no containers
        result = self.docker_environment_manager.remove(name)
        assert result == True

        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_manager.build(name, path)
        result = self.docker_environment_manager.remove(name)
        assert result == True

        # With force
        self.docker_environment_manager.build(name, path)
        # teardown
        result = self.docker_environment_manager.remove(name, force=True)
        assert result == True

    def test_init(self):
        assert self.init_result and \
               self.docker_environment_manager.is_initialized == True

    def test_get_tags_for_docker_repository(self):
        result = self.docker_environment_manager.get_tags_for_docker_repository(
            "hello-world")
        assert 'latest' in result

    def test_build_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        result = self.docker_environment_manager.build_image(
            image_name, dockerfile_path)
        assert result == True
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_get_image(self):
        failed = False
        try:
            self.docker_environment_manager.get_image("random")
        except EnvironmentImageNotFound:
            failed = True
        assert failed

        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)

        result = self.docker_environment_manager.get_image(image_name)
        tags = result.__dict__['attrs']['RepoTags']
        assert image_name + ":latest" in tags
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_list_images(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        # List images without all flag
        result = self.docker_environment_manager.list_images()
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert image_name + ":latest" in group_flat
        # List images with all flag
        result = self.docker_environment_manager.list_images(all_images=True)
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert image_name + ":latest" in group_flat
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_search_images(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        result = self.docker_environment_manager.search_images(image_name)
        assert len(result) > 0
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_remove_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        result = self.docker_environment_manager.remove_image(image_name)
        assert result == True
        # With force
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        result = self.docker_environment_manager.remove_image(
            image_name, force=True)
        assert result == True

    def test_remove_images(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        result = self.docker_environment_manager.remove_images(name=image_name)
        assert result == True
        # With force
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        result = self.docker_environment_manager.remove_images(
            name=image_name, force=True)
        assert result == True

    def test_run_container(self):
        # TODO: test with all variables provided
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        # With default parameters
        return_code, container_id = \
            self.docker_environment_manager.run_container(image_name)
        assert return_code == 0 and \
            container_id
        # teardown container
        self.docker_environment_manager.stop(container_id, force=True)
        # With api=True, detach=False
        logs = self.docker_environment_manager.run_container(
            image_name, api=True)
        assert logs == ""
        # With api=True, detach=True
        container_obj = self.docker_environment_manager.run_container(
            image_name, api=True, detach=True)
        assert container_obj
        self.docker_environment_manager.stop(container_obj.id, force=True)
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_get_container(self):
        failed = False
        try:
            self.docker_environment_manager.get_container("random")
        except EnvironmentContainerNotFound:
            failed = True
        assert failed

        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(
            image_name)
        result = self.docker_environment_manager.get_container(container_id)
        assert result
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_list_containers(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(
            image_name, detach=True)
        result = self.docker_environment_manager.list_containers()
        assert container_id and len(result) > 0
        self.docker_environment_manager.stop(container_id, force=True)
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_stop_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(
            image_name)
        result = self.docker_environment_manager.stop_container(container_id)
        assert result == True
        result = self.docker_environment_manager.get_container(container_id)
        assert result.__dict__['attrs']['State']['Status'] == "exited"
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_remove_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        # Without force
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(
            image_name)
        result = self.docker_environment_manager.remove_container(container_id)
        assert result == True
        # With force
        _, container_id = self.docker_environment_manager.run_container(
            image_name)
        result = self.docker_environment_manager.remove_container(
            container_id, force=True)
        assert result == True
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_log_container(self):
        # TODO: Do a more comprehensive test, test out optional variables
        # TODO: Test out more commands at the system level
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        _, container_id = \
            self.docker_environment_manager.run_container(image_name,
                                                          command=["sh", "-c", "echo yo"])
        return_code, logs = self.docker_environment_manager.log_container(
            container_id, log_filepath)
        assert return_code == 0
        assert logs and \
               os.path.exists(log_filepath)

        with open(log_filepath, "r") as f:
            assert f.readline() != ""

        self.docker_environment_manager.stop_container(container_id)
        self.docker_environment_manager.remove_container(
            container_id, force=True)
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_create_requirements_file(self):
        # 1) Test failure EnvironmentDoesNotExist
        # 2) Test success
        # 3) Test failure EnvironmentRequirementsCreateException

        # 1) Test option 1
        failed = False
        try:
            _ = self.docker_environment_manager.create_requirements_file()
        except EnvironmentDoesNotExist:
            failed = True
        assert failed

        # 2) Test option 2
        script_path = os.path.join(self.docker_environment_manager.filepath,
                                   "script.py")
        with open(script_path, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
        # Test default
        result = self.docker_environment_manager.create_requirements_file()
        assert result
        assert os.path.isfile(result) and \
               "numpy" in open(result, "r").read() and \
               "scikit_learn" in open(result, "r").read()

        # 3) Test option 3
        exception_thrown = False
        try:
            _ = self.docker_environment_manager.\
                create_requirements_file(execpath="does_not_work")
        except EnvironmentRequirementsCreateException:
            exception_thrown = True

        assert exception_thrown

    def test_create_default_dockerfile(self):
        script_path = os.path.join(self.docker_environment_manager.filepath,
                                   "script.py")
        with open(script_path, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
        requirements_filepath = \
            self.docker_environment_manager.create_requirements_file()
        result = self.docker_environment_manager.\
            create_default_dockerfile(requirements_filepath,
                                      language="python3")

        assert result
        assert os.path.isfile(result)
        assert "python" in open(result, "r").read()
        assert "requirements.txt" in open(result, "r").read()

    def test_stop_remove_containers_by_term(self):
        # TODO: add more robust tests
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu" + "\n"))
            f.write(to_unicode(str("RUN echo " + random_text)))
        self.docker_environment_manager.build_image(image_name,
                                                    dockerfile_path)
        # Test without force
        self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.stop_remove_containers_by_term(
            image_name)
        assert result == True
        # Test with force
        self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.stop_remove_containers_by_term(
            image_name, force=True)
        assert result == True
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_form_datmo_dockerfile(self):
        input_dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "Dockerfile")
        output_dockerfile_path = os.path.join(
            self.docker_environment_manager.filepath, "datmoDockerfile")
        result = self.docker_environment_manager.form_datmo_definition_file(
            input_dockerfile_path, output_dockerfile_path)
        assert result and \
            os.path.isfile(output_dockerfile_path) and \
            "datmo" in open(output_dockerfile_path, "r").read()
