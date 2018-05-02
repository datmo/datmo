import ast
import os
import shutil
import subprocess
import platform
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from docker import DockerClient

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import PathDoesNotExist, \
    EnvironmentDoesNotExist, EnvironmentInitFailed, \
    EnvironmentExecutionException, FileAlreadyExistsException, \
    EnvironmentRequirementsCreateException
from datmo.core.controller.environment.driver import EnvironmentDriver


class DockerEnvironmentDriver(EnvironmentDriver):
    """
    This EnvironmentDriver handles environment management in the project using docker

    Parameters
    ----------
    filepath : str, optional
        home filepath for project
        (default is empty)
    docker_execpath : str, optional
        execution path for docker
        (default is "docker" which defers to system)
    docker_socket : str, optional
        socket path to docker daemon to connect
        (default is None, this takes the default path for the system)

    Attributes
    ----------
    filepath : str
        home filepath for project
    docker_execpath : str
        docker execution path for the system
    docker_socket : str
        specific socket for docker
        (default is None, which means system default is used by docker)
    client : DockerClient
        docker python api client
    cpu_prefix : list
        list of strings for the prefix command for all docker commands
    info : dict
        information about the docker daemon connection
    is_connected : bool
        True if connected to daemon else False
    type : str
        type of EnvironmentDriver
    """

    def __init__(self,
                 filepath="",
                 docker_execpath="docker",
                 docker_socket=None):
        if not docker_socket:
            if platform.system() != "Windows":
                docker_socket = "unix:///var/run/docker.sock"

        super(DockerEnvironmentDriver, self).__init__()
        self.filepath = filepath
        # Check if filepath exists
        if not os.path.exists(self.filepath):
            raise PathDoesNotExist(
                __("error",
                   "controller.environment.driver.docker.__init__.dne",
                   filepath))

        # TODO: separate methods for instantiation into init function below

        # Initiate Docker execution
        self.docker_execpath = docker_execpath
        try:
            self.docker_socket = docker_socket
            if self.docker_socket:
                self.client = DockerClient(base_url=self.docker_socket)
                self.cpu_prefix = [
                    self.docker_execpath, "-H", self.docker_socket
                ]
            else:
                self.client = DockerClient()
                self.cpu_prefix = [self.docker_execpath]
            self.info = self.client.info()
        except Exception:
            raise EnvironmentInitFailed(
                __("error", "controller.environment.driver.docker.__init__",
                   platform.system()))

        self.is_connected = True if self.info["Images"] != None else False

        self._is_initialized = self.is_initialized
        self.type = "docker"

        # execute a docker info command
        # make sure it passed
        # if gpu_requested == True:
        #     pass
        # if gpu is requested then
        # make sure docker info confirms that it"s available

    @property
    def is_initialized(self):
        # TODO: Check if Docker is up and running
        if self.is_connected:
            self._is_initialized = True
            return self._is_initialized
        self._is_initialized = False
        return self._is_initialized

    def create(self, path=None, output_path=None, language=None):
        if not path:
            path = os.path.join(self.filepath, "Dockerfile")
        if not output_path:
            directory, filename = os.path.split(path)
            output_path = os.path.join(directory, "datmo" + filename)
        if not language:
            language = "python3"

        requirements_filepath = None
        if not os.path.isfile(path):
            if language == "python3":
                # Create requirements txt file for python
                requirements_filepath = self.create_requirements_file()
                # Create Dockerfile for ubuntu
                path = self.create_default_dockerfile(
                    requirements_filepath=requirements_filepath,
                    language=language)
            else:
                raise EnvironmentDoesNotExist(
                    __("error",
                       "controller.environment.driver.docker.create.dne",
                       path))
        if os.path.isfile(output_path):
            raise FileAlreadyExistsException(
                __("error",
                   "controller.environment.driver.docker.create.exists",
                   output_path))
        success = self.form_datmo_definition_file(
            input_definition_path=path, output_definition_path=output_path)

        return success, path, output_path, requirements_filepath

    def build(self, name, path):

        return self.build_image(name, path)

    def run(self, name, options, log_filepath):
        run_return_code, run_id = \
            self.run_container(image_name=name, **options)
        log_return_code, logs = self.log_container(
            run_id, filepath=log_filepath)
        final_return_code = run_return_code and log_return_code

        return final_return_code, run_id, logs

    def stop(self, run_id, force=False):
        stop_result = self.stop_container(run_id)
        remove_run_result = self.remove_container(run_id, force=force)
        return stop_result and remove_run_result

    def remove(self, name, force=False):
        stop_and_remove_containers_result = \
            self.stop_remove_containers_by_term(name, force=force)
        remove_image_result = self.remove_image(name, force=force)
        return stop_and_remove_containers_result and \
               remove_image_result

    def init(self):
        # TODO: Fill in to start up Docker
        try:
            # Startup Docker
            pass
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error", "controller.environment.driver.docker.init",
                   str(e)))
        return True

    def get_tags_for_docker_repository(self, repo_name):
        # TODO: Use more common CLI command (e.g. curl instead of wget)
        """Method to get tags for docker repositories

        Parameters
        ----------
        repo_name: str
            Docker repository name

        Returns
        -------
        list
            List of tags available for that docker repo
        """
        docker_repository_tag_cmd = "wget -q https://registry.hub.docker.com/v1/repositories/" + repo_name + "/tags -O -"
        string_repository_tags = subprocess.check_output(
            docker_repository_tag_cmd, shell=True)
        string_repository_tags = string_repository_tags.decode().strip()
        repository_tags = ast.literal_eval(string_repository_tags)
        list_tag_names = []
        for repository_tag in repository_tags:
            list_tag_names.append(repository_tag["name"])
        return list_tag_names

    def build_image(self, tag, definition_path="Dockerfile"):
        """Builds docker image

        Parameters
        ----------
        tag : str
            name to tag image with
        definition_path : str
            absolute file path to the definition

        Returns
        -------
        bool
            True if success

        Raises
        ------
        EnvironmentExecutionException

        """
        try:
            docker_shell_cmd_list = list(self.cpu_prefix)
            docker_shell_cmd_list.append("build")

            # Passing tag name for the image
            docker_shell_cmd_list.append("-t")
            docker_shell_cmd_list.append(tag)

            # Passing path of Dockerfile
            docker_shell_cmd_list.append("-f")
            docker_shell_cmd_list.append(definition_path)
            dockerfile_dirpath = os.path.split(definition_path)[0]
            docker_shell_cmd_list.append(str(dockerfile_dirpath))

            # Remove intermediate containers after a successful build
            docker_shell_cmd_list.append("--rm")
            process_returncode = subprocess.Popen(docker_shell_cmd_list).wait()
            if process_returncode == 0:
                return True
            elif process_returncode == 1:
                raise EnvironmentExecutionException(
                    __("error",
                       "controller.environment.driver.docker.build_image",
                       "Docker subprocess failed"))
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error", "controller.environment.driver.docker.build_image",
                   str(e)))

    def get_image(self, image_name):
        return self.client.images.get(image_name)

    def list_images(self, name=None, all_images=False, filters=None):
        return self.client.images.list(
            name=name, all=all_images, filters=filters)

    def search_images(self, term):
        return self.client.images.search(term=term)

    def remove_image(self, image_id_or_name, force=False):
        try:
            if force:
                docker_image_remove_cmd = list(self.cpu_prefix)
                docker_image_remove_cmd.extend(["rmi", "-f", image_id_or_name])
            else:
                docker_image_remove_cmd = list(self.cpu_prefix)
                docker_image_remove_cmd.extend(["rmi", image_id_or_name])
            subprocess.check_output(docker_image_remove_cmd).decode().strip()
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error",
                   "controller.environment.driver.docker.remove_image",
                   str(e)))
        return True

    def remove_images(self, name=None, all=False, filters=None, force=False):
        """Remove multiple images
        """
        try:
            images = self.list_images(
                name=name, all_images=all, filters=filters)
            for image in images:
                self.remove_image(image.id, force=force)
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error",
                   "controller.environment.driver.docker.remove_images",
                   str(e)))
        return True

    def run_container(self,
                      image_name,
                      command=None,
                      ports=None,
                      name=None,
                      volumes=None,
                      detach=False,
                      stdin_open=False,
                      tty=False,
                      gpu=False,
                      api=False):
        """Run Docker container with parameters given as defined below

        Parameters
        ----------
        image_name : str
            Docker image name
        command : list, optional
            List with complete user-given command (e.g. ["python3", "cool.py"])
        ports : list, optional
            Here are some example ports used for common applications.
               *  "jupyter notebook" - 8888
               *  flask API - 5000
               *  tensorboard - 6006
            An example input for the above would be ["8888:8888", "5000:5000", "6006:6006"]
            which maps the running host port (right) to that of the environment (left)
        name : str, optional
            User given name for container
        volumes : dict, optional
            Includes storage volumes for docker
            (e.g. { outsidepath1 : {"bind", containerpath2, "mode", MODE} })
        detach : bool, optional
            True if container is to be detached else False
        stdin_open : bool, optional
            True if stdin is open else False
        tty : bool, optional
            True to connect pseudo-terminal with stdin / stdout else False
        gpu : bool, optional
            True if GPU should be enabled else False
        api : bool, optional
            True if Docker python client should be used else use subprocess

        Returns
        -------
        if api=False:

        return_code: int
            integer success code of command
        container_id: str
            output container id


        if api=True & if detach=True:

        container_obj: Container
            object from Docker python api with details about container

        if api=True & if detach=False:

        logs: str
            output logs for the run function

        Raises
        ------
        EnvironmentExecutionException
             error in running the environment command
        """
        try:
            container_id = None
            if api:  # calling the docker client via the API
                # TODO: Test this out for the API (need to verify ports work)
                if detach:
                    command = " ".join(command) if command else command
                    container = \
                        self.client.containers.run(image_name, command, ports=ports,
                                                   name=name, volumes=volumes,
                                                   detach=detach, stdin_open=stdin_open)
                    return container
                else:
                    command = " ".join(command) if command else command
                    logs = self.client.containers.run(
                        image_name,
                        command,
                        ports=ports,
                        name=name,
                        volumes=volumes,
                        detach=detach,
                        stdin_open=stdin_open)
                    return logs.decode()
            else:  # if calling run function with the shell commands
                if gpu:
                    docker_shell_cmd_list = list(self.cpu_prefix)
                else:
                    docker_shell_cmd_list = list(self.cpu_prefix)
                docker_shell_cmd_list.append("run")

                if name:
                    docker_shell_cmd_list.append("--name")
                    docker_shell_cmd_list.append(name)

                if stdin_open:
                    docker_shell_cmd_list.append("-i")

                if tty:
                    docker_shell_cmd_list.append("-t")

                if detach:
                    docker_shell_cmd_list.append("-d")

                # Volume
                if volumes:
                    # Mounting volumes
                    for key in list(volumes):
                        docker_shell_cmd_list.append("-v")
                        volume_mount = key + ":" + volumes[key]["bind"] + ":" + \
                                       volumes[key]["mode"]
                        docker_shell_cmd_list.append(volume_mount)

                if ports:
                    # Mapping ports
                    for mapping in ports:
                        docker_shell_cmd_list.append("-p")
                        docker_shell_cmd_list.append(mapping)

                docker_shell_cmd_list.append(image_name)
                if command:
                    docker_shell_cmd_list.extend(command)
                return_code = subprocess.call(docker_shell_cmd_list)
                if return_code != 0:
                    raise EnvironmentExecutionException(
                        __("error",
                           "controller.environment.driver.docker.run_container",
                           docker_shell_cmd_list))
                list_process_cmd = list(self.cpu_prefix)
                list_process_cmd.extend(["ps", "-q", "-l"])
                container_id = subprocess.check_output(list_process_cmd)
                container_id = container_id.decode().strip()

        except Exception as e:
            raise EnvironmentExecutionException(
                __("error",
                   "controller.environment.driver.docker.run_container",
                   str(e)))
        return return_code, container_id

    def get_container(self, container_id):
        return self.client.containers.get(container_id)

    def list_containers(self,
                        all=False,
                        before=None,
                        filters=None,
                        limit=-1,
                        since=None):
        return self.client.containers.list(
            all=all, before=before, filters=filters, limit=limit, since=since)

    def stop_container(self, container_id):
        try:
            docker_container_stop_cmd = list(self.cpu_prefix)
            docker_container_stop_cmd.extend(["stop", container_id])
            subprocess.check_output(docker_container_stop_cmd).decode().strip()
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error",
                   "controller.environment.driver.docker.stop_container",
                   str(e)))
        return True

    def remove_container(self, container_id, force=False):
        try:
            docker_container_remove_cmd_list = list(self.cpu_prefix)
            if force:
                docker_container_remove_cmd_list.extend(
                    ["rm", "-f", container_id])
            else:
                docker_container_remove_cmd_list.extend(["rm", container_id])
            subprocess.check_output(
                docker_container_remove_cmd_list).decode().strip()
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error",
                   "controller.environment.driver.docker.remove_container",
                   str(e)))
        return True

    def log_container(self, container_id, filepath, api=False, follow=True):
        """Log capture at a particular point `docker logs`. Can also use `--follow` for real time logs

        Parameters
        ----------
        container_id : str
            Docker container id
        filepath : str
            Filepath to store log file
        api : bool
            True to use the docker python api
        follow : bool
            Tail the output

        Returns
        -------
        return_code : str
            Process return code for the container
        logs : str
            Output logs read into a string format
        """
        # TODO: Fix function to better accomodate all logs in the same way
        if api:  # calling the docker client via the API
            with open(filepath, "w") as log_file:
                for line in self.client.containers.get(container_id).logs(
                        stream=True):
                    log_file.write(to_unicode(line.strip() + "\n"))
        else:
            command = list(self.cpu_prefix)
            if follow:
                command.extend(["logs", "--follow", str(container_id)])
            else:
                command.extend(["logs", str(container_id)])
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, universal_newlines=True)
            with open(filepath, "w") as log_file:
                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        printable_output = output.strip().replace("\x08", " ")
                        log_file.write(to_unicode(printable_output + "\n"))
            return_code = process.poll()
            with open(filepath, "r") as log_file:
                logs = log_file.read()
            return return_code, logs

    def stop_remove_containers_by_term(self, term, force=False):
        """Stops and removes containers by term
        """
        try:
            running_docker_container_cmd_list = list(self.cpu_prefix)
            running_docker_container_cmd_list.extend([
                "ps", "-a", "|", "grep", "'", term, "'", "|",
                "awk '{print $1}'"
            ])
            running_docker_container_cmd_str = str(
                " ".join(running_docker_container_cmd_list))
            output = subprocess.Popen(
                running_docker_container_cmd_str,
                shell=True,
                stdout=subprocess.PIPE)
            out_list_cmd, err_list_cmd = output.communicate()

            # checking for running container id before stopping any
            if out_list_cmd:
                docker_container_stop_cmd_list = list(self.cpu_prefix)
                docker_container_stop_cmd_list = docker_container_stop_cmd_list + \
                                                 ["stop", "$("] + running_docker_container_cmd_list + \
                                                 [")"]
                docker_container_stop_cmd_str = str(
                    " ".join(docker_container_stop_cmd_list))
                output = subprocess.Popen(
                    docker_container_stop_cmd_str,
                    shell=True,
                    stdout=subprocess.PIPE)
                _, _ = output.communicate()
                # rechecking for container id after stopping them to ensure no errors
                output = subprocess.Popen(
                    running_docker_container_cmd_str,
                    shell=True,
                    stdout=subprocess.PIPE)
                out_list_cmd, _ = output.communicate()
                if out_list_cmd:
                    docker_container_remove_cmd_list = list(self.cpu_prefix)
                    if force:
                        docker_container_remove_cmd_list = docker_container_remove_cmd_list + \
                                                           ["rm", "-f", "$("] + running_docker_container_cmd_list + \
                                                           [")"]
                    else:
                        docker_container_remove_cmd_list = docker_container_remove_cmd_list + \
                                                           ["rm", "$("] + running_docker_container_cmd_list + \
                                                           [")"]
                    docker_container_remove_cmd_str = str(
                        " ".join(docker_container_remove_cmd_list))
                    output = subprocess.Popen(
                        docker_container_remove_cmd_str,
                        shell=True,
                        stdout=subprocess.PIPE)
                    _, _ = output.communicate()
        except Exception as e:
            raise EnvironmentExecutionException(
                __("error",
                   "controller.environment.driver.docker.stop_remove_containers_by_term",
                   str(e)))
        return True

    def create_requirements_file(self, execpath="pipreqs"):
        """Create python requirements txt file for the project

        Parameters
        ----------
        execpath : str, optional
            execpath for the pipreqs command to form requirements.txt file
            (default is "pipreqs")

        Returns
        -------
        str
            absolute filepath for requirements file

        Raises
        ------
        EnvironmentDoesNotExist
            no python requirements found for environment
        EnvironmentRequirementsCreateException
            error in running pipreqs command to extract python requirements
        """
        try:
            subprocess.check_output(
                [execpath, self.filepath, "--force"],
                cwd=self.filepath).strip()
            requirements_filepath = os.path.join(self.filepath,
                                                 "requirements.txt")
        except Exception as e:
            raise EnvironmentRequirementsCreateException(
                __("error", "controller.environment.requirements.create",
                   str(e)))
        if open(requirements_filepath, "r").read() == "\n":
            raise EnvironmentDoesNotExist()
        return requirements_filepath

    def create_default_dockerfile(self, requirements_filepath, language):
        """Create a default Dockerfile for a given language

        Parameters
        ----------
        requirements_filepath : str
            path for the requirements txt file
        language : str
            programming language used ("python2" and "python3" currently supported)

        Returns
        -------
        str
            absolute path for the new Dockerfile using requirements txt file
        """
        language_dockerfile = "%sDockerfile" % language
        base_dockerfile_filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates",
            language_dockerfile)

        # Combine dockerfile
        destination_dockerfile = os.path.join(self.filepath, "Dockerfile")
        destination = open(destination_dockerfile, "w")
        shutil.copyfileobj(open(base_dockerfile_filepath, "r"), destination)
        destination.write(
            to_unicode(
                str("COPY %s /tmp/requirements.txt\n") %
                os.path.split(requirements_filepath)[-1]))
        destination.write(
            to_unicode(
                str("RUN pip install --no-cache-dir -r /tmp/requirements.txt\n"
                    )))
        destination.close()

        return destination_dockerfile

    def form_datmo_definition_file(self,
                                   input_definition_path="Dockerfile",
                                   output_definition_path="datmoDockerfile"):
        """
        In order to create intermediate dockerfile to run
        """
        base_dockerfile_filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates",
            "baseDockerfile")

        # Combine dockerfiles
        destination = open(
            os.path.join(self.filepath, output_definition_path), "w")
        shutil.copyfileobj(open(input_definition_path, "r"), destination)
        shutil.copyfileobj(open(base_dockerfile_filepath, "r"), destination)
        destination.close()

        return True
