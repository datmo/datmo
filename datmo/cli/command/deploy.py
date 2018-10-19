from __future__ import print_function

# https://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility/11301392?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
import os
import sys
import prettytable
from datetime import datetime
try:
    basestring
except NameError:
    basestring = str

from datmo.core.util.i18n import get as __
from datmo.cli.driver.helper import Helper
from datmo.core.util.misc_functions import bcolors
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.deploy.deploy import DeployController


class DeployCommand(ProjectCommand):
    def __init__(self, cli_helper):
        super(DeployCommand, self).__init__(cli_helper)
        self.deploy_controller = DeployController()

    def deploy(self):
        self.parse(["deploy", "--help"])
        return True

    @Helper.notify_no_project_found
    def service(self, **kwargs):
        """
        Creates the FaaS service with the specified server type in a cluster
        """
        self.cli_helper.echo(__("info", "cli.deploy.service"))
        cluster_name = kwargs.get("cluster_name", None)
        server_type = kwargs.get("server_type", None)
        size = kwargs.get("size", None)

        while not cluster_name:
            cluster_name = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.service.name"))

        # Get all cluster name, server type and count
        response = self.deploy_controller.cluster_ls()
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        current_cluster_information = response.result
        cluster_names = []
        cluster_server_types = []
        cluster_server_counts = []
        for cluster in current_cluster_information['clusters']:
            cluster_names.append(cluster['name'])
            cluster_server_types.append(cluster['server_type'])
            cluster_server_counts.append(cluster['count'])
        if cluster_name in cluster_names:
            cluster_server_type = cluster_server_types[cluster_names.index(
                cluster_name)]
            self.cli_helper.echo(
                __("warn", "cli.deploy.service.deployment_exists",
                   cluster_server_type))
            if server_type and server_type != cluster_server_type:
                self.cli_helper.echo(
                    __("info", "cli.deploy.service.update_server",
                       (cluster_name, server_type)))
            else:
                self.cli_helper.echo(
                    __("info", "cli.deploy.service.update_deploy"))
            return

        while not server_type:
            server_type = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.service.server_type"))
            if server_type is None: server_type = 't2.small'

        while not size:
            size = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.service.size"))
            size = 1 if size is None else int(size)

        # Deploy the servers onto the cluster
        response = self.deploy_controller.cluster_deploy(
            cluster_name, server_type, size=size)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        # deploy the model onto the cluster
        response = self.deploy_controller.model_deploy(
            cluster_name=cluster_name)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        self.cli_helper.echo(
            __("info", "cli.deploy.service.success", cluster_name))

    @Helper.notify_no_project_found
    def update(self, **kwargs):
        """
        Updates and scales the service with the already specified server type in a cluster
        """

        cluster_name = kwargs.get("cluster_name", None)
        size = kwargs.get("size", None)
        path = kwargs.get("path", None)

        while not cluster_name:
            cluster_name = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.update.name"))

        # Get all cluster name, server type and count
        response = self.deploy_controller.cluster_ls()
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        current_cluster_information = response.result
        cluster_names = []
        cluster_server_types = []
        cluster_server_counts = []
        for cluster in current_cluster_information['clusters']:
            cluster_names.append(cluster['name'])
            cluster_server_types.append(cluster['server_type'])
            cluster_server_counts.append(cluster['count'])

        # check if the given cluster name exists
        if cluster_name in cluster_names:
            cluster_server_type = cluster_server_types[cluster_names.index(
                cluster_name)]
            cluster_server_count = cluster_server_counts[cluster_names.index(
                cluster_name)]
            self.cli_helper.echo(
                __("warn", "cli.deploy.update.deployment_exists",
                   cluster_server_type))
            while not size:
                size = self.cli_helper.prompt(
                    __("prompt", "cli.project.deploy.update.size"))
                size = 1 if size is None else int(size)

            if size and size != cluster_server_count:
                # Scale the servers based on requirement
                response = self.deploy_controller.cluster_update(
                    cluster_name, size)
                if response.status:
                    self.cli_helper.echo(response.message)
                    sys.exit(response.status)
        else:
            self.cli_helper.echo(
                __("error", "cli.deploy.update.deployment_dne", cluster_name))
            self.cli_helper.echo(
                __("info", "cli.deploy.update.create_deployment"))
            return

        # deploy the model code onto the cluster
        response = self.deploy_controller.model_deploy(
            cluster_name=cluster_name)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        self.cli_helper.echo(__("info", "cli.deploy.update.success"))

    @Helper.notify_no_project_found
    def ls(self, **kwargs):
        """
        List all the information of the Datmo Cluster and Services
        """
        print_format = kwargs.get('format', "table")
        download = kwargs.get('download', None)
        download_path = kwargs.get('download_path', None)

        # Get all cluster name, server type and count
        response = self.deploy_controller.cluster_ls()
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        current_cluster_information = response.result
        header_list = [
            'cluster name', 'server type', 'count', 'service path',
            'service url'
        ]
        table_header_list = []
        for i in header_list:
            table_header_list.append(bcolors.HEADER + i + bcolors.ENDC)
        t = prettytable.PrettyTable(table_header_list)
        displayed_cluster_names = []
        item_dict_list = []
        if current_cluster_information['clusters']:
            for cluster in current_cluster_information['clusters']:
                cluster_name = cluster['name']
                cluster_server_type = cluster['server_type']
                cluster_server_count = cluster['count']
                if not cluster['services']:
                    t.add_row([
                        cluster_name, cluster_server_type,
                        cluster_server_count, '', ''
                    ])
                    deploy_item = {
                        "cluster name": cluster_name,
                        "server type": cluster_server_type,
                        "count": cluster_server_count,
                        "service path": "",
                        "service url": ""
                    }
                    item_dict_list.append(deploy_item)
                for cluster_service in cluster['services']:
                    service_route = cluster_service['route']
                    service_url = cluster_service['url']
                    if cluster_name not in displayed_cluster_names:
                        t.add_row([
                            cluster_name, cluster_server_type,
                            cluster_server_count, service_route, service_url
                        ])
                        displayed_cluster_names.append(cluster_name)
                        deploy_item = {
                            "cluster name": cluster_name,
                            "server type": cluster_server_type,
                            "count": cluster_server_count,
                            "service path": service_route,
                            "service url": service_url
                        }
                    else:
                        t.add_row(['', '', '', service_route, service_url])
                        deploy_item = {
                            "cluster name": "",
                            "server type": "",
                            "count": "",
                            "service path": service_route,
                            "service url": service_url
                        }
                    item_dict_list.append(deploy_item)
        if download:
            if not download_path:
                # download to current working directory with timestamp
                current_time = datetime.utcnow()
                epoch_time = datetime.utcfromtimestamp(0)
                current_time_unix_time_ms = (
                    current_time - epoch_time).total_seconds() * 1000.0
                download_path = os.path.join(
                    os.getcwd(), "deploy_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
        self.cli_helper.echo(t)

    @Helper.notify_no_project_found
    def logs(self, **kwargs):
        """
        To extract logs for a service route for a particular date
        """
        service_path = kwargs.get("service_path", None)
        date = kwargs.get("date", None)

        while not service_path:
            service_path = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.logs.service_path"))

        try:
            self.cli_helper.echo(
                __("info", "cli.deploy.logs.download", (service_path, date)))
            response = self.deploy_controller.service_iologs(
                service_path, date)
            if response.status:
                self.cli_helper.echo(response.message)
                sys.exit(response.status)
        except Exception as e:
            self.cli_helper.echo(
                __("error", "cli.deploy.logs.download_error", e))

    @Helper.notify_no_project_found
    def rm(self, **kwargs):
        """
            Stop and remove the cluster
            """
        cluster_name = kwargs.get("cluster_name", None)
        while not cluster_name:
            cluster_name = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.rm.service_name"))

        self.cli_helper.echo(__("info", "cli.deploy.rm.removing"))
        response = self.deploy_controller.cluster_stop(cluster_name)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        self.cli_helper.echo(__("info", "cli.deploy.rm.success", cluster_name))
