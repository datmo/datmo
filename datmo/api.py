import os

from datmo.core.controller.base import BaseController


class API():
    """API for Datmo

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

    def __init__(self, api_key, home=None):
        self._api_key = api_key
        self._base_controller = BaseController(home=home)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    def post_data(self, input_data):
        # check for the right model id (based on home), model_version_id (snapshot_id), and deployment id
        # validate dictionary based on inputs
        # run post request (using requests)
        # gather result and return to user
        pass

    # Usage
    # of
    # POST
    # request:
    #
    # curl - H
    # "Content-Type: application/json" - X
    # POST
    # -d
    # '{"prediction_time_stamp": "timestamp", "model_id": "model_id", "model_version": "model_version", "cpu_utilization": "cpu utilization", "latency": "timestamp", "input": "check", "api_key": "d41d8cd98f00b204e9800998ecf8427e", "prediction": "check", "mem_utilization": "mem utilization"}'
    # https: // s8l9gg1li9.execute - api.eu - west - 1.
    # amazonaws.com / production / datmo_monitoring

    def get_data(self, filter):
        # check for the right model id (based on home), model_version_id (snapshot_id), and deployment id
        # validate the filters
        # run get request with the filters (using requests)
        # gather result and return to users
        pass

    # Usage
    # of
    # GET
    # request:
    #
    # curl - H
    # "Accept: application/json" - X
    # GET
    # https: // mgwf6kjso7.execute - api.eu - west - 1.
    # amazonaws.com / production / datmo_monitoring?model_id = model_id & api_key = d41d8cd98f00b204e9800998ecf8427e & model_version = model_version