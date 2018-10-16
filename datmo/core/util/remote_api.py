import json
import requests


class RemoteAPI():
    """API for Accessing Datmo Services

    Parameters
    ----------
    api_key : str
        credentials to access remote
    home : str, optional
        directory for the project, default is to pull from config

    Attributes
    ----------


    Methods
    -------


    """

    # TODO: move url into configurations (to be setup `datmo configure`
    def __init__(self, api_key):
        self._api_key = api_key
        self.post_meta_data_endpoint = \
            "https://s8l9gg1li9.execute-api.eu-west-1.amazonaws.com/production/datmo_monitoring"
        self.get_meta_data_endpoint = \
            "https://mgwf6kjso7.execute-api.eu-west-1.amazonaws.com/production/datmo_monitoring"
        self.put_meta_data_endpoint = \
            "https://6xav2qlolf.execute-api.eu-west-1.amazonaws.com/production/datmo_monitoring"
        self.get_deployment_info_endpoint = \
            "https://hb0c2py3sh.execute-api.eu-west-1.amazonaws.com/production/datmo_deployments"

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    def post_data(self, input_data):
        # Run post request and gather result and return to user
        response = {"status_code": 200}
        try:
            headers = {"content-type": "application/json"}
            input_data['api_key'] = self._api_key
            r = requests.post(
                self.post_meta_data_endpoint,
                data=json.dumps(input_data),
                headers=headers)
            response = {"status_code": r.status_code, "body": r.json()}
        except:
            response['status_code'] = 500
        return response

    def get_data(self, filter):
        # run get request with the filters (using requests) and gather and return results
        response = {"status_code": 200}
        try:
            headers = {"content-type": "application/json"}
            filter['api_key'] = self._api_key
            r = requests.get(
                self.get_meta_data_endpoint, params=filter, headers=headers)
            response = {"status_code": r.status_code, "body": r.json()}
        except:
            response['status_code'] = 500
        return response

    def update_actual(self, id, actual):
        response = {"status_code": 200}
        try:
            headers = {"content-type": "application/json"}
            update_dict = dict()
            update_dict['api_key'] = self._api_key
            update_dict['id'] = id
            update_dict['actual'] = actual
            r = requests.put(
                self.put_meta_data_endpoint,
                data=json.dumps(update_dict),
                headers=headers)
            response = {"status_code": r.status_code, "body": r.json()}
        except:
            response['status_code'] = 500
        return response

    def get_deployment_info(self):
        # run get request with the filters (using requests) and gather and return results
        response = {"status_code": 200}
        try:
            headers = {"content-type": "application/json"}
            params = {"api_key": self._api_key}
            r = requests.get(
                self.get_deployment_info_endpoint,
                params=params,
                headers=headers)
            response = {"status_code": r.status_code, "body": r.json()}
        except:
            response['status_code'] = 500
        return response
