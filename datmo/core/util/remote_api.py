import json
import requests


class RemoteAPI():
    """API for Accessing Datmo Services

    Parameters
    ----------
    api_key : str
        credentials to access remote

    Attributes
    ----------


    Methods
    -------
    post_data(input_data)
        post single data point to Datmo scoped by model
    get_data(filter)
        get data information from Datmo scoped by filter
    update_actual(id, actual)
        update the data id with actual values (y_hat)
    get_deployment_info()
        returns deployment info from Datmo deployed models
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
        self.delete_meta_data_endpoint = \
            "https://ynpas9m577.execute-api.eu-west-1.amazonaws.com/production/datmo_monitoring"

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

    def delete_data(self, filter):
        # Run post request and gather result and return to user
        response = {"status_code": 200}
        try:
            headers = {"content-type": "application/json"}
            filter['api_key'] = self._api_key
            r = requests.delete(
                self.delete_meta_data_endpoint,
                data=json.dumps(filter),
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

    def update_actual(self, id, update_dict):
        response = {"status_code": 200}
        try:
            headers = {"content-type": "application/json"}
            if not isinstance(update_dict, dict):
                raise Exception
            update_dict['api_key'] = self._api_key
            update_dict['id'] = id
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
