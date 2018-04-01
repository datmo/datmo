import ast
import os
import shutil
import subprocess

from docker import DockerClient

from datmo.util.exceptions import DoesNotExistException, \
    EnvironmentInitFailed, EnvironmentExecutionException


class DockerEnvironmentManager(object):
    """
    This Environment Manager handles Environment management in the Datmo Project using Docker
    """

    def __init__(self, filepath="", docker_execpath="docker", docker_socket="unix:///var/run/docker.sock"):
        self.filepath = filepath
        # Check if filepath exists
        if not os.path.exists(self.filepath):
            raise DoesNotExistException("exception.environment_driver.docker", {
                "filepath": filepath,
                "exception": "File path does not exist"
            })

        # TODO: separate methods for instantiation into init function below

        # Initiate Docker execution
        self.docker_execpath = docker_execpath
        self.docker_socket = docker_socket
        try:
            self.client = DockerClient(base_url=self.docker_socket)
            self.info = self.client.info()
        except Exception:
            raise EnvironmentInitFailed(self.docker_socket)

        self.is_connected = True if self.info["Images"] != None else False
        self.cpu_prefix = [self.docker_execpath, '-H', self.docker_socket]

        self._is_initialized = self.is_initialized

        # execute a docker info command
        # make sure it passed
        # if gpu_requested == True:
        #     pass
        # if gpu is requested then
        # make sure docker info confirms that it's available

    @property
    def is_initialized(self):
        # TODO: Check if Docker is up and running
        if self.is_connected:
            self._is_initialized = True
            return self._is_initialized
        self._is_initialized = False
        return self._is_initialized

    def init(self):
        # TODO: Fill in code_driver to start up Docker
        try:
            # Startup Docker
            pass
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.init", {
                "exception": e
            })
        return True


    def get_tags_for_docker_repository(self, repo_name):
        """
        Method to get tags for docker repositories
        :param repo_name: the docker repository name
        :return: list of tags available for that docker repo
        """
        docker_repository_tag_cmd = 'wget -q https://registry.hub.docker.com/v1/repositories/' + repo_name + '/tags -O -'
        string_repository_tags = subprocess.check_output(docker_repository_tag_cmd, shell=True).strip()
        repository_tags = ast.literal_eval(string_repository_tags)
        list_tag_names = []
        for repository_tag in repository_tags:
            list_tag_names.append(repository_tag['name'])
        return list_tag_names

    def build_image(self, tag, definition_path='Dockerfile'):
        try:
            docker_shell_cmd_list = list(self.cpu_prefix)
            docker_shell_cmd_list.append('build')

            # Passing tag name for the image
            docker_shell_cmd_list.append('-t')
            docker_shell_cmd_list.append(tag)

            # Passing path of Dockerfile
            docker_shell_cmd_list.append('-f')
            docker_shell_cmd_list.append(definition_path)
            docker_shell_cmd_list.append(str(self.filepath))

            # Remove intermediate containers after a successful build
            docker_shell_cmd_list.append('--rm')
            process_returncode = subprocess.Popen(docker_shell_cmd_list).wait()
            if process_returncode == 0:
                return True
            elif process_returncode == 1:
                raise EnvironmentExecutionException("exception.environment_driver.docker.build_image", {
                    "exception": "Build subprocess failed"
                })
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.build_image", {
                "exception": e
            })

    def get_image(self, image_name):
        return self.client.images.get(image_name)

    def list_images(self, name=None, all=False, filters=None):
        return self.client.images.list(name=name, all=all, filters=filters)

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
            subprocess.check_output(docker_image_remove_cmd).strip()
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.remove_image", {
                "exception": e
            })
        return True

    def remove_images(self, name=None, all=False, filters=None,
                          force=False):
        """
        Remove multiple images
        """
        try:
            images = self.list_images(name=name, all=all, filters=filters)
            for image in images:
                self.remove_image(image.id, force=force)
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.remove_images", {
                "exception": e
            })
        return True

    def run_container(self, image_name, command=None, ports=None, name=None, volumes=None,
                   detach=False, stdin_open=False, tty=False, gpu=False, api=False):
        """
        Run Docker container with parameters given as defined below

        :param image_name: Docker image name
        :param command: list with complete user-given command
        :param ports: dict w/ format { "port/tcp": int(port), ... }
        :param name: string to name container
        :param volumes: dict with format { outsidepath1 : {'bind', containerpath2, 'mode', MODE} }
        :param detach: bool to specify if container is to be detached
        :param stdin_open: bool to specify if stdin is open
        :param tty: bool connect pseudo-terminal with stdin / stdout
        :param gpu: bool if GPU should be enabled
        :param api: bool if Docker python client should be used
        :return:
            if api=False: (return_code, container_id)
            if api=True:
                if detach=True: container_obj
                if detach=False: container logs as string
        """
        try:
            container_id = None
            if api: # calling the docker client via the API
                if detach:
                    command = " ".join(command) if command else command
                    container = \
                        self.client.containers.run(image_name, command, ports=ports,
                                                   name=name, volumes=volumes,
                                                   detach=detach, stdin_open=stdin_open)
                    return container
                else:
                    command = " ".join(command) if command else command
                    logs = self.client.containers.run(image_name, command, ports=ports,
                                                      name=name, volumes=volumes,
                                                      detach=detach, stdin_open=stdin_open)
                    return logs
            else: # if calling run function with the shell commands
                if gpu:
                    docker_shell_cmd_list = list(self.cpu_prefix)
                else:
                    docker_shell_cmd_list = list(self.cpu_prefix)
                docker_shell_cmd_list.append('run')

                if name:
                    docker_shell_cmd_list.append('--name')
                    docker_shell_cmd_list.append(name)

                if stdin_open:
                    docker_shell_cmd_list.append('-i')

                if tty:
                    docker_shell_cmd_list.append('-t')

                if detach:
                    docker_shell_cmd_list.append('-d')

                # Volume
                if volumes:
                    # Mounting volumes
                    for key in volumes.keys():
                        docker_shell_cmd_list.append('-v')
                        volume_mount = key + ':' + volumes[key]['bind'] + ':' + \
                                       volumes[key]['mode']
                        docker_shell_cmd_list.append(volume_mount)

                if ports:
                    # Mapping ports
                    for key in ports.keys():
                        docker_shell_cmd_list.append('-p')
                        port_mapping = str(ports[key]) + ':' + key
                        docker_shell_cmd_list.append(port_mapping)


                docker_shell_cmd_list.append(image_name)

                if command:
                    docker_shell_cmd_list.extend(command)
                return_code = subprocess.call(docker_shell_cmd_list)
                if return_code != 0:
                    raise EnvironmentExecutionException("exception.environment_driver.docker.run_container", {
                        "exception": "Docker command failed: %s" % docker_shell_cmd_list
                    })
                list_process_cmd = list(self.cpu_prefix)
                list_process_cmd.extend(['ps','-q', '-l'])
                container_id = subprocess.check_output(list_process_cmd).strip()

        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.run_container", {
                "exception": e
            })
        return return_code, container_id

    def get_container(self, container_id):
        return self.client.containers.get(container_id)

    def list_containers(self, all=False, before=None, filters=None,
                        limit=-1, since=None):
        return self.client.containers.list(all=all, before=before, filters=filters,
                                           limit=limit, since=since)

    def stop_container(self, container_id):
        try:
            docker_container_stop_cmd = list(self.cpu_prefix)
            docker_container_stop_cmd.extend(["stop", container_id])
            subprocess.check_output(docker_container_stop_cmd).strip()
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.stop_container", {
                "exception": e
            })
        return True

    def remove_container(self, container_id, force=False):
        try:
            docker_container_remove_cmd_list = list(self.cpu_prefix)
            if force:
                docker_container_remove_cmd_list.extend(["rm", "-f", container_id])
            else:
                docker_container_remove_cmd_list.extend(["rm", container_id])
            subprocess.check_output(docker_container_remove_cmd_list).strip()
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.remove_container", {
                "exception": e
            })
        return True

    def log_container(self, container_id, filepath, api=False,
                      follow=True):
        """
        Log capture at a particular point `docker logs`. Can also use `--follow` for real time logs

        :param container_id: docker container id
        :param filepath: filepath to store log file
        :param api: use the docker python api
        :param follow: tail the output
        :return: return code_driver of the docker log command
        """
        # TODO: Fix function to better accomodate all logs in the same way
        if api: # calling the docker client via the API
            with open(filepath, 'wb') as log_file:
                for line in self.client.containers.get(container_id).logs(stream=True):
                    log_file.write(line.strip() + "\n")
        else:
            command = list(self.cpu_prefix)
            if follow:
                command.extend(['logs', '--follow', str(container_id)])
            else:
                command.extend(['logs', str(container_id)])
            process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                       universal_newlines=True)
            with open(filepath, 'wb') as log_file:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        printable_output = output.strip().replace('\x08', ' ')
                        log_file.write(printable_output + "\n")
            return_code = process.poll()
            with open(filepath, 'rb') as log_file:
                logs = log_file.read()
            return return_code, logs

    def stop_remove_containers_by_term(self, term, force=False):
        """
        Stops and removes containers by term
        """
        try:
            running_docker_container_cmd_list = list(self.cpu_prefix)
            running_docker_container_cmd_list.extend(["ps", "-a", "|", "grep", "'", term ,"'", "|", "awk '{print $1}'"])
            running_docker_container_cmd_str = str(" ".join(running_docker_container_cmd_list))
            output = subprocess.Popen(running_docker_container_cmd_str,
                                      shell=True, stdout=subprocess.PIPE)
            output_running_docker_container_cmd = output.communicate()[0]

            # checking for running container id before stopping any
            if output_running_docker_container_cmd:
                docker_container_stop_cmd_list = list(self.cpu_prefix)
                docker_container_stop_cmd_list = docker_container_stop_cmd_list + \
                                                 ["stop", "$("] + running_docker_container_cmd_list + \
                                                 [")"]
                docker_container_stop_cmd_str = str(" ".join(docker_container_stop_cmd_list))
                output = subprocess.Popen(docker_container_stop_cmd_str,
                                  shell=True, stdout=subprocess.PIPE)
                output_docker_container_stop_cmd = output.communicate()[0]
                # rechecking for container id after stopping them to ensure no errors
                output = subprocess.Popen(running_docker_container_cmd_str,
                                          shell=True, stdout=subprocess.PIPE)
                output_running_docker_container_cmd = output.communicate()[0]
                if output_running_docker_container_cmd:
                    docker_container_remove_cmd_list = list(self.cpu_prefix)
                    if force:
                        docker_container_remove_cmd_list = docker_container_remove_cmd_list + \
                                                           ["rm", "-f", "$("] + running_docker_container_cmd_list + \
                                                           [")"]
                    else:
                        docker_container_remove_cmd_list = docker_container_remove_cmd_list + \
                                                           ["rm", "$("] + running_docker_container_cmd_list + \
                                                           [")"]
                    docker_container_remove_cmd_str = str(" ".join(docker_container_remove_cmd_list))
                    output = subprocess.Popen(docker_container_remove_cmd_str,
                                              shell=True, stdout=subprocess.PIPE)
                    output_docker_container_remove_cmd = output.communicate()[0]
        except Exception as e:
            raise EnvironmentExecutionException("exception.environment_driver.docker.stop_remove_containers_by_term", {
                "exception": e
            })
        return True

    def form_datmo_definition_file(self, input_definition_path="Dockerfile",
                                   output_definition_path="datmoDockerfile"):
        """
        in order to create intermediate dockerfile to run
        """
        base_dockerfile_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "templates", "baseDockerfile")

        # Combine dockerfiles
        destination = open(os.path.join(self.filepath, output_definition_path), 'wb')
        shutil.copyfileobj(open(input_definition_path, 'rb'), destination)
        shutil.copyfileobj(open(base_dockerfile_filepath, 'rb'), destination)
        destination.close()

        return True