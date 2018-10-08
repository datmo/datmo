import os
import tempfile
import shutil
from datmo.core.util.misc_functions import Commands
from datmo.core.controller.deploy.driver.microservice import DatmoDriver
from datmo.config import Config


class DeployController(object):
    """
    A orchestrator tool which works with AWS ECS and Datmo Orchestrators

    Attributes:
        service: A string representing the cloud service provider
        service_container_management: Bool representing to use service's container management system
    """

    def __init__(self, service_container_management=False):
        """Initialize the Orchestrator service"""
        self.commands = Commands()
        self.config = Config()
        self.master_server_ip, self.datmo_access_key, self.datmo_end_point = self.config.deployment_setup
        self.service_container_management = service_container_management
        self.manager = None
        # src folder from CLI folder
        self.src_file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src_files')
        self.manager = DatmoDriver(end_point=self.datmo_end_point, access_key=self.datmo_access_key)

    def system_setup(self):
        """
        Setup the system with provider and their key and secret token
        :return:
        """
        response = self.manager.setup()
        return response

    def cluster_deploy(self, cluster_name=None, server_type=None, size=None):
        """
        Deploy the Servers in the cluster with the defined setup
        :return:
        """
        response = self.manager.create_cluster(cluster_name, server_type, count=size)
        return response

    def cluster_update(self, cluster_name, size):
        """
        Scale up/down the number of servers in the cluster
        :param cluster_name: Name of cluster
        :param size:  Number of servers
        :return:
        """
        response = self.manager.update_cluster(count=size, cluster_name=cluster_name)
        return response

    def cluster_stop(self, cluster_name):
        """
        Stop and remove the cluster
        :param cluster_name: name of the cluster
        :return:
        """
        response = self.manager.update_cluster(count=0, cluster_name=cluster_name)
        return response

    def cluster_ls(self, cluster_name='*'):
        """
        List all containers in the cluster
        :param cluster_name: name of the cluster
        :return:
        """
        response = self.manager.get_cluster_info(cluster_name)
        return response

    def system_info(self):
        """
        To return the information about the System and Logging portal
        :return:
        """
        response = self.manager.get_system_info()
        return response

    def system_cost(self):
        """
        To return the information about the cost due to datmo deploy from cloud systems
        :return:
        """
        response = self.manager.get_system_cost()
        return response

    def model_deploy(self, cluster_name, model_path=os.getcwd()):
        """
        Deploy the model after building it from the docker compose file
        :param model_path: name of the model to be deployed
        :param docker_compose_filepath: path of the docker compose file
        :param file: The file path to compress and send
        :param model_path: The path for model folder
        :return:
        """
        # Specific for datmoservice logic
        tmp_dirpath = tempfile.mkdtemp()
        # copy the content for project directory to tmp folder and the environment to root location in tmp folder
        try:
            self.commands.copy(model_path, tmp_dirpath)
            environment_dirpath = os.path.join(tmp_dirpath, 'datmo_environment')
            if os.path.exists(environment_dirpath):
                self.commands.copy(environment_dirpath, tmp_dirpath)
                shutil.rmtree(os.path.join(tmp_dirpath, 'datmo_environment'))
                shutil.rmtree(os.path.join(tmp_dirpath, '.datmo'))
                shutil.rmtree(os.path.join(tmp_dirpath, 'datmo_files'))
        except Exception as e:
            print e

        model_zipfile_path = os.path.join(tmp_dirpath, 'datmo_model.zip')
        self.commands.zip_folder(tmp_dirpath, model_zipfile_path)
        response = self.manager.model_deploy(cluster_name, model_zipfile_path)
        # remove the temp directory
        shutil.rmtree(tmp_dirpath)
        return response

    def service_iologs(self, service_path, date):
        """
        Extract io logs for a particular service
        :param service_path: service route for the algorithm
        :param date: Date for which you want to get the logs
        :return:
        """
        response = self.manager.get_service_iologs(service_path, date)
        return response