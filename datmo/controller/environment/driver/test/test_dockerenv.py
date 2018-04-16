"""
Tests for dockerenv.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
import shutil
import uuid

from datmo.controller.environment.driver.dockerenv import DockerEnvironmentDriver
from datmo.util.exceptions import EnvironmentInitFailed, \
    DoesNotExistException, FileAlreadyExistsException


class TestDockerEnv():
    # TODO: Add more cases for each test
    """
    Checks all functions of the DockerEnvironmentDriver
    """
    def setup_method(self):
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        self.docker_environment_manager = \
            DockerEnvironmentDriver(self.temp_dir, 'docker',
                                     'unix:///var/run/docker.sock')
        self.init_result = self.docker_environment_manager.init()
        random_text = str(uuid.uuid1())
        with open(os.path.join(self.temp_dir, "Dockerfile"),
                  "a+") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_instantiation_and_connected(self):
        assert self.docker_environment_manager.is_connected
        assert self.docker_environment_manager != None

    def test_instantiation_not_connected(self):
        thrown = False
        try:
            DockerEnvironmentDriver(self.temp_dir, 'docker', 'unix:///var/run/fooo')
        except EnvironmentInitFailed:
            thrown = True
        assert thrown

    def test_create(self):
        input_dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                             "Dockerfile")
        output_dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                              "datmoDockerfile")
        # Test both default values
        success, path, output_path = \
            self.docker_environment_manager.create()

        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        os.remove(output_dockerfile_path)

        # Test default values for output
        success, path, output_path = \
            self.docker_environment_manager.create(input_dockerfile_path)

        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path
        os.remove(output_dockerfile_path)

        # Test both values given
        success, path, output_path = \
            self.docker_environment_manager.create(input_dockerfile_path,
                                                        output_dockerfile_path)
        assert success and \
               os.path.isfile(output_dockerfile_path) and \
               "datmo" in open(output_dockerfile_path, "r").read()
        assert path == input_dockerfile_path
        assert output_path == output_dockerfile_path

        # Test exception for path does not exist
        try:
            self.docker_environment_manager.create("nonexistant_path")
        except DoesNotExistException:
            assert True

        # Test exception for output path already exists
        try:
            self.docker_environment_manager.create(
                output_path=output_dockerfile_path)
        except FileAlreadyExistsException:
            assert True

    def test_build(self):
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        result = self.docker_environment_manager.build(name, path)
        assert result == True
        # teardown
        self.docker_environment_manager.remove(name, force=True)

    def test_run(self):
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build(name, path)

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:9999", "5000:5001"],
            "name": None,
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "gpu": False,
            "api": False
        }
        return_code, run_id, logs = \
            self.docker_environment_manager.run(name, run_options, log_filepath)

        assert return_code == 0
        assert run_id
        assert logs
        # teardown
        self.docker_environment_manager.stop(run_id, force=True)
        self.docker_environment_manager.remove(name, force=True)

    def test_stop(self):
        name = str(uuid.uuid1())
        path = os.path.join(self.docker_environment_manager.filepath,
                            "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build(name, path)

        run_options = {
            "command": ["sh", "-c", "echo yo"],
            "ports": ["8888:9999", "5000:5001"],
            "name": "my_container_name_2",
            "volumes": None,
            "detach": False,
            "stdin_open": False,
            "tty": False,
            "gpu": False,
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
        path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
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
        result = self.docker_environment_manager.get_tags_for_docker_repository("hello-world")
        assert 'latest' in result

    def test_build_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        result = self.docker_environment_manager.build_image(image_name, dockerfile_path)
        assert result == True
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_get_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)

        result = self.docker_environment_manager.get_image(image_name)
        tags  = result.__dict__['attrs']['RepoTags']
        assert image_name + ":latest" in tags
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_list_images(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        # List images without all flag
        result = self.docker_environment_manager.list_images()
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert image_name + ":latest" in group_flat
        # List images with all flag
        result = self.docker_environment_manager.list_images(all=True)
        group = [item.__dict__['attrs']['RepoTags'] for item in result]
        list_of_lists = [sublist for sublist in group if sublist]
        group_flat = [item for sublist in list_of_lists for item in sublist]
        assert image_name + ":latest" in group_flat
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_search_images(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        result  = self.docker_environment_manager.search_images(image_name)
        assert len(result) > 0
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_remove_image(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        # Without force
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        result = self.docker_environment_manager.remove_image(image_name)
        assert result == True
        # With force
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        result = self.docker_environment_manager.remove_image(image_name, force=True)
        assert result == True

    def test_remove_images(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        # Without force
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        result = self.docker_environment_manager.remove_images(name=image_name)
        assert result == True
        # With force
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        result = self.docker_environment_manager.remove_images(name=image_name, force=True)
        assert result == True

    def test_run_container(self):
        # TODO: test with all variables provided
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        # With default parameters
        return_code, container_id = \
            self.docker_environment_manager.run_container(image_name)
        assert return_code == 0 and \
            container_id
        # With api=True, detach=False
        logs = self.docker_environment_manager.run_container(image_name, api=True)
        assert logs == ""
        # With api=True, detach=True
        container_obj = self.docker_environment_manager.run_container(image_name, api=True,
                                                                      detach=True)
        assert container_obj
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_get_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.get_container(container_id)
        assert result
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_list_containers(self):
        # TODO: Test out all input permutations
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(image_name,
                                                                     detach=True)
        result = self.docker_environment_manager.list_containers()
        assert container_id and len(result) > 0
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_stop_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.stop_container(container_id)
        assert result == True
        result = self.docker_environment_manager.get_container(container_id)
        assert result.__dict__['attrs']['State']['Status'] == "exited"
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_remove_container(self):
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        # Without force
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        _, container_id = self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.remove_container(container_id)
        assert result == True
        # With force
        _, container_id = self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.remove_container(container_id, force=True)
        assert result == True
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_log_container(self):
        # TODO: Do a more comprehensive test, test out optional variables
        # TODO: Test out more commands at the system level
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        log_filepath = os.path.join(self.docker_environment_manager.filepath,
                                    "test.log")
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        _, container_id = \
            self.docker_environment_manager.run_container(image_name,
                                                          command=["sh", "-c", "echo yo"])
        self.docker_environment_manager.stop_container(container_id)
        return_code, logs = self.docker_environment_manager.log_container(container_id,
                                                               log_filepath)
        assert return_code == 0
        assert logs and \
               os.path.exists(log_filepath)

        with open(log_filepath, "r") as f:
            assert f.readline() != ""

        self.docker_environment_manager.stop_container(container_id)
        self.docker_environment_manager.remove_container(container_id, force=True)
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_stop_remove_containers_by_term(self):
        # TODO: add more robust tests
        image_name = str(uuid.uuid1())
        dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        random_text = str(uuid.uuid1())
        with open(dockerfile_path, "w") as f:
            f.write("FROM datmo/xgboost:cpu" + "\n")
            f.write(str("RUN echo " + random_text))
        self.docker_environment_manager.build_image(image_name, dockerfile_path)
        # Test without force
        self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.stop_remove_containers_by_term(image_name)
        assert result == True
        # Test with force
        self.docker_environment_manager.run_container(image_name)
        result = self.docker_environment_manager.stop_remove_containers_by_term(image_name,
                                                                                force=True)
        assert result == True
        self.docker_environment_manager.remove_image(image_name, force=True)

    def test_form_datmo_dockerfile(self):
        input_dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                       "Dockerfile")
        output_dockerfile_path = os.path.join(self.docker_environment_manager.filepath,
                                              "datmoDockerfile")
        result = self.docker_environment_manager.form_datmo_definition_file(input_dockerfile_path,
                                                                            output_dockerfile_path)
        assert result and \
            os.path.isfile(output_dockerfile_path) and \
            "datmo" in open(output_dockerfile_path, "r").read()
