from datmo.core.util.misc_functions import Commands, \
    bcolors, authenticated_get_call, Response, Status


class DatmoMicroserviceDeployDriver(object):
    """
    Datmo Microservice deployment driver
    """

    def __init__(self, end_point, api_key):
        self.end_point = end_point
        self.api_key = api_key
        self.commands = Commands()
        self.status = Status

    def check_setup(self, response):
        # in case of no proper setup
        if self.end_point is not None:
            return True, response
        response.message = bcolors.FAIL + "Setup for remote datmo isn't done. " \
                                          "Run `datmo setup` and setup your remote credentials " + bcolors.ENDC
        response.status = self.status.FAILURE
        return False, response

    def create_cluster(self, cluster_name=None, server_type=None, count=None):
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        if cluster_name:
            self.cluster_name = cluster_name
        if server_type:
            self.server_type = server_type
        if count:
            self.count = str(count)

        shell_cmd = 'curl -d \'{"cluster_name": "%s", "server_type": "%s", "count": %s}\' -H "Content-Type: application/json" -H "authorization:%s" -X POST %s/cluster' % (
            self.cluster_name, self.server_type, self.count, self.api_key,
            self.end_point)
        command_run = self.commands.run_cmd(shell_cmd)
        if not command_run['status']:
            response.message = bcolors.FAIL + "error while creating the cluster" + bcolors.ENDC
            response.status = self.status.FAILURE
        return response

    def update_cluster(self, count, cluster_name=None):
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        self.count = count
        if cluster_name:
            self.cluster_name = cluster_name
        shell_cmd = 'curl -d \'{"count": %s}\' -H "Content-Type: application/json"  -H "authorization:%s" -X PUT %s/cluster/%s'\
                    % (self.count, self.api_key, self.end_point, self.cluster_name)
        command_run = self.commands.run_cmd(shell_cmd)
        if not command_run['status']:
            response.message = bcolors.FAIL + "error while updating the cluster" + bcolors.ENDC
            response.status = self.status.FAILURE
        return response

    def get_cluster_info(self, cluster_name):
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        self.cluster_name = cluster_name
        url = '%s/cluster/%s' % (self.end_point, self.cluster_name)
        res = authenticated_get_call(url, access_key=self.api_key)
        if res.status_code != 200:
            response.message = bcolors.FAIL + "error while getting the information about the cluster" + bcolors.ENDC
            response.status = self.status.FAILURE
            return response
        response.result = res.json()
        return response

    def get_system_info(self):
        """

        Returns
        -------
        To return the Kibana and Grafana links and credentials for it
        """
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        url = '%s/info' % self.end_point
        res = authenticated_get_call(url, access_key=self.api_key)
        if res.status_code != 200:
            response.message = bcolors.FAIL + "error while getting the information about the cluster" + bcolors.ENDC
            response.status = self.status.FAILURE
            return response
        response.result = res.json()
        return response

    def get_system_cost(self):
        """

        Returns
        -------
        cost of the current system from the cloud service
        """
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        url = '%s/cost_estimate' % self.end_point
        res = authenticated_get_call(url, access_key=self.api_key)
        if res.status_code != 200:
            response.message = bcolors.FAIL + "error while getting the information about the cluster" + bcolors.ENDC
            response.status = self.status.FAILURE
            return response
        response.result = res.json()
        return response

    def model_deploy(self, cluster_name, file=None):
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        self.cluster_name = cluster_name
        shell_cmd = 'curl  -H "authorization:%s" -F \'service=@%s\' %s/cluster/%s/deploy' % (
            self.api_key, file, self.end_point, self.cluster_name)
        command_run = self.commands.run_cmd(shell_cmd)
        if not command_run['status']:
            response.message = bcolors.FAIL + "error while deploying the model onto the cluster" + bcolors.ENDC
            response.status = self.status.FAILURE
        return response

    def get_service_iologs(self, service_path, date):
        response = Response()
        bool_setup, response = self.check_setup(response)
        if not bool_setup:
            return response
        # get the proper service path
        service_path = service_path.strip()
        if service_path[0] == '/':
            service_path = service_path[1:]
        url = '%s/iologs/%s?date=%s' % (self.end_point, service_path, date)
        res = authenticated_get_call(url, access_key=self.api_key)
        if res.status_code not in [200, 201]:
            response.message = bcolors.FAIL + 'DOWNLOAD io logs failed: ' + res.text + bcolors.ENDC
            response.status = self.status.FAILURE
        path = service_path.replace('/', '.') + '-' + date.replace(
            '/', '.') + '.tar.gz'
        with open(path, 'wb') as f:
            for chunk in res:
                f.write(chunk)
        return response
