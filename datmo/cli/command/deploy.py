from __future__ import print_function

# https://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility/11301392?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
try:
    basestring
except NameError:
    basestring = str

import sys
import prettytable
from prettytable import ALL as ALL
from datmo.cli.driver.helper import Helper
from datmo.core.util.misc_functions import bcolors
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.deploy.deploy import DeployController


class DeployCommand(ProjectCommand):
    def __init__(self, cli_helper):
        super(DeployCommand, self).__init__(cli_helper)
        self.deploy_controller = DeployController()

    @Helper.notify_environment_active(DeployController)
    @Helper.notify_no_project_found
    def setup(self):
        """
        Creates the service with the specified server type in a cluster
        """
        self.deploy_controller.system_setup()

    @Helper.notify_environment_active(DeployController)
    @Helper.notify_no_project_found
    def service(self, **kwargs):
        """
        Creates the service with the specified server type in a cluster
        """
        self.cli_helper.echo(__("info", "cli.deploy.service"))
        cluster_name = kwargs.get("cluster_name", None)
        server_type = kwargs.get("server_type", None)
        size = kwargs.get("size", None)
        path = kwargs.get("path", None)

        while not cluster_name:
            cluster_name = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.service.cluster_name"))

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
            cluster_server_type = cluster_server_types[cluster_names.index(cluster_name)]
            if server_type and server_type != cluster_server_type:
                self.cli_helper.echo(bcolors.OKBLUE + "---> Cluster already exists with server type: %s" % (cluster_server_type) +
                           bcolors.ENDC)
                self.cli_helper.echo(bcolors.FAIL + "Please remove the cluster to start a cluster %s with server"
                                          " type: %s" % (cluster_name, server_type) + bcolors.ENDC)
            else:
                self.cli_helper.echo(
                    bcolors.WARNING + "---> Cluster exists with server type: %s" % (cluster_server_type) + bcolors.ENDC)
                self.cli_helper.echo(
                    bcolors.WARNING + "---> Use the update command to re-deploy new code or to scale the size of already"
                                      " deployed services" + bcolors.ENDC)
            return

        while not server_type:
            server_type = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.service.server_type"))
            if server_type is None: server_type = 't2.small'

        while not size:
            size = int(self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.service.size")))
            if size is None: size = 1

        # Deploy the servers onto the cluster
        response = self.deploy_controller.cluster_deploy(cluster_name, server_type, size=size)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        # deploy the model onto the cluster
        response = self.deploy_controller.model_deploy(cluster_name=cluster_name, model_path=path)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        self.cli_helper.echo(
            bcolors.OKGREEN + u'\u2713' + " Successfully deployed on the cluster: %s" % cluster_name + bcolors.ENDC)


    @Helper.notify_environment_active(DeployController)
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
                __("prompt", "cli.project.deploy.update.cluster_name"))

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
            cluster_server_type = cluster_server_types[cluster_names.index(cluster_name)]
            cluster_server_count = cluster_server_counts[cluster_names.index(cluster_name)]
            self.cli_helper.echo(
                bcolors.OKBLUE + "---> Cluster exists with server type: %s" % (cluster_server_type) + bcolors.ENDC)
            while not size:
                size = int(self.cli_helper.prompt(
                    __("prompt", "cli.project.deploy.update.size")))

            if size and size != cluster_server_count:
                # Scale the servers based on requirement
                response = self.deploy_controller.cluster_update(cluster_name, size)
                if response.status:
                    self.cli_helper.echo(response.message)
                    sys.exit(response.status)
        else:
            self.cli_helper.echo(bcolors.WARNING + "---> No cluster exist with this name %s" % cluster_name + bcolors.ENDC)
            self.cli_helper.echo(bcolors.WARNING + "---> Create cluster using the service command" + bcolors.ENDC)
            return

        # deploy the model code onto the cluster
        response = self.deploy_controller.model_deploy(cluster_name=cluster_name, model_path=path)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        self.cli_helper.echo(
            bcolors.OKGREEN + u'\u2713' + " Successfully deployed on the cluster: %s" % cluster_name + bcolors.ENDC)

    @Helper.notify_environment_active(DeployController)
    @Helper.notify_no_project_found
    def ls(self, **kwargs):
        """
        List all the information of the Datmo Cluster and Services
        """
        # Get all cluster name, server type and count
        response = self.deploy_controller.cluster_ls()
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        current_cluster_information = response.result
        header_list = ['cluster name', 'server type', 'count', 'service path', 'service url']
        table_header_list = []
        for i in header_list:
            table_header_list.append(bcolors.HEADER + i + bcolors.ENDC)
        t = prettytable.PrettyTable(table_header_list)
        displayed_cluster_names = []
        if current_cluster_information['clusters']:
            for cluster in current_cluster_information['clusters']:
                cluster_name = cluster['name']
                cluster_server_type = cluster['server_type']
                cluster_server_count = cluster['count']
                if not cluster['services']:
                    t.add_row([cluster_name, cluster_server_type, cluster_server_count, '', ''])
                for cluster_service in cluster['services']:
                    service_route = cluster_service['route']
                    service_url = cluster_service['url']
                    if cluster_name not in displayed_cluster_names:
                        t.add_row([cluster_name, cluster_server_type, cluster_server_count, service_route, service_url])
                        displayed_cluster_names.append(cluster_name)
                    else:
                        t.add_row(['', '', '', service_route, service_url])
        self.cli_helper.echo(t)


    @Helper.notify_environment_active(DeployController)
    @Helper.notify_no_project_found
    def dashboard(self, **kwargs):
        """
            Information regarding the system performance and logging system
            """
        response = self.deploy_controller.system_info()
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        current_system_information = response.result
        header_list = ['service', 'endpoint', 'credentials']
        table_header_list = []
        for i in header_list:
            table_header_list.append(bcolors.HEADER + i + bcolors.ENDC)
        t = prettytable.PrettyTable(table_header_list)
        if current_system_information:
            for key, value in current_system_information.iteritems():
                if key == 'kibana':
                    service = 'logging system'
                    endpoint = value["endpoint"]
                    t.add_row([service, endpoint, ''])
                elif key == 'grafana':
                    service = 'system performance'
                    endpoint = value["endpoint"]
                    password = value["password"]
                    username = 'admin'
                    credentials = 'username: %s password: %s' % (username, password)
                    t.add_row([service, endpoint, credentials])
        self.cli_helper.echo(t)


    @Helper.notify_environment_active(DeployController)
    @Helper.notify_no_project_found
    def cost(self, **kwargs):
        """
            Information about the cost from cloud systems with deployment service
            """
        response = self.deploy_controller.system_cost()
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        current_servers_cost = response.result
        header_list = ['cloud service type', 'datmo name', 'instance', 'daily cost', 'weekly cost', 'monthly cost']
        total_daily_cost = 0
        total_weekly_cost = 0
        total_monthly_cost = 0
        table_header_list = []
        for i in header_list:
            table_header_list.append(bcolors.HEADER + i + bcolors.ENDC)
        t = prettytable.PrettyTable(table_header_list, hrules=ALL)
        if current_servers_cost:
            servers = current_servers_cost.get("servers", None)
            if servers:
                cluster_names_info = {}
                for server in servers:
                    instance_type = server.get("InstanceType", None)
                    costs = server.get("Costs", None)
                    if costs:
                        daily_cost = float("{0:.2f}".format(costs.get("daily", None)))
                        weekly_cost = float("{0:.2f}".format(costs.get("weekly", None)))
                        monthly_cost = float("{0:.2f}".format(costs.get("monthly", None)))
                        total_daily_cost += daily_cost
                        total_weekly_cost += weekly_cost
                        total_monthly_cost += monthly_cost
                        costs_dict = {'daily_cost': daily_cost, 'weekly_cost': weekly_cost,
                                      'monthly_cost': monthly_cost}
                        tags = server.get("Tags", None)
                        if tags:
                            for tag in tags:
                                key = tag["Key"]
                                value = tag["Value"]
                                if key == "cluster" and value not in cluster_names_info:
                                    cluster_names_info[value] = {"count": 1, "cost": costs_dict,
                                                                 "instance_type": instance_type}
                                elif key == "cluster" and value in cluster_names_info:
                                    count = cluster_names_info[value].get("count", None)
                                    cluster_names_info[value]["count"] = count + 1
                                elif key == "datmo" and value == "cluster-master":
                                    t.add_row(["ec2", "master", "Type:%s Count:%s" % (instance_type, 1),
                                               '$%s' % daily_cost, '$%s' % weekly_cost, '$%s' % monthly_cost])
                        elif 'elasticsearch' in instance_type:
                            t.add_row(["elasticsearch", "Logging", "Type: %s Count: %s" % (instance_type, 1),
                                       '$%s' % daily_cost, '$%s' % weekly_cost, '$%s' % monthly_cost])
                        else:
                            t.add_row(["", "", "Type: %s Count: %s" % (instance_type, 1),
                                       '$%s' % daily_cost, '$%s' % weekly_cost, '$%s' % monthly_cost])
                for key, value in cluster_names_info.iteritems():
                    cluster_daily_cost = value["cost"]["daily_cost"] * value["count"]
                    cluster_weekly_cost = value["cost"]["weekly_cost"] * value["count"]
                    cluster_monthly_cost = value["cost"]["monthly_cost"] * value["count"]
                    t.add_row(["ec2", "cluster: %s" % key,
                               'Type: %s Count: %s' % (value["instance_type"],
                                                       value["count"]), '$%s' % cluster_daily_cost,
                               '$%s' % cluster_weekly_cost, '$%s' % cluster_monthly_cost])
        total_cost_row = ['', '', '', 'total: $%s' % total_daily_cost, 'total: $%s' % total_weekly_cost,
                          'total: $%s' % total_monthly_cost]
        table_total_cost_row = []
        for i in total_cost_row:
            table_total_cost_row.append(bcolors.HEADER + i + bcolors.ENDC)
        t.add_row(table_total_cost_row)
        self.cli_helper.echo(t)

    @Helper.notify_environment_active(DeployController)
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
            self.cli_helper.echo(bcolors.BOLD + "Downloading compressed io logs for service route %s for date %s..."
                       % (service_path, date) + bcolors.ENDC)
            response = self.deploy_controller.service_iologs(service_path, date)
            if response.status:
                self.cli_helper.echo(response.message)
                sys.exit(response.status)
        except Exception as e:
            self.cli_helper.echo(bcolors.FAIL + "error: while extracting logs."
                                                " error due to following,\n %s" % e + bcolors.ENDC)


    @Helper.notify_environment_active(DeployController)
    @Helper.notify_no_project_found
    def rm(self, **kwargs):
        """
            Stop and remove the cluster
            """
        cluster_name = kwargs.get("cluster_name", None)
        while not cluster_name:
            cluster_name = self.cli_helper.prompt(
                __("prompt", "cli.project.deploy.rm.service_name"))

        self.cli_helper.echo(bcolors.BOLD + "     Removing all the services and servers in the cluster" + bcolors.ENDC)
        response = self.deploy_controller.cluster_stop(cluster_name)
        if response.status:
            self.cli_helper.echo(response.message)
            sys.exit(response.status)
        self.cli_helper.echo(bcolors.OKGREEN + u'\u2713' + " Successfully removed Cluster: %s" % cluster_name +
                             bcolors.ENDC)