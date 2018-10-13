import time
import json
import psutil
from datmo.core.util.misc_functions import bytes2human
from datmo.core.util.remote_api import RemoteAPI
from datmo.core.controller.base import BaseController


class Monitoring():
    """Class for monitoring Datmo services

    Parameters
    ----------
    api_key : str
        credentials to access remote
    home : str, optional
        directory for the project, default is to pull from config

    Attributes
    ----------
    api_key : str
        the api key used for accessing the datmo service
    model_id : str
        the parent model id for the entity
    model_version : str
        the version of the model which is deployed
    deployment_id : str
        the id or type of deployment

    Examples
    --------
    You can use this function within a project repository to track predicitons
    or inferences. Once you have created this, you will be able to view them on
    the monitoring dashboard

    >>> from datmo.monitoring import Monitoring
    >>> datmo_client = Monitoring(api_key='my_data_api_key')
    >>> datmo_client.set_model_version('v3')
    >>> datmo_client.set_model_id('model_id')
    >>> datmo_client.set_deployment_id('microservice')
    >>> def predict(x):
    >>>     datmo_client.set_start()
    >>>     y_predict = model_predict(x) # using a machine learning model for inference
    >>>     datmo_model.set_end()
    >>>     datmo_id = datmo_client.track(input=x, prediction=y_predict) # Track predictions
    >>>     response = {'y': y, 'datmo_id': datmo_id}
    >>>     return response
    ...
    >>> response = predict(x)
    ...
    >>> # For feedback
    >>> datmo_client.track_actual(id=response['datmo_id'], actual=y_actual)
    """

    def __init__(self, api_key, home=None):
        self._api_key = api_key
        self._base_controller = BaseController(home=home)
        self.remote_api = RemoteAPI(self._api_key)
        self._start_time, self._end_time, self._model_id, \
        self._model_version, self._deployment_id = None, None, None, None, None

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    @property
    def set_start(self):
        """
        Set the start time
        :return: start time in milliseconds
        """
        self._start_time = int(round(time.time() * 1000))
        return self._start_time

    @property
    def set_end(self):
        """
        Set the end time
        :return: end time in milliseconds
        """
        self._end_time = int(round(time.time() * 1000))
        return self._end_time

    def set_model_id(self, id):
        """
        Set the model id
        :param id: the id representing the model
        """
        self._model_id = id

    def set_model_version(self, id):
        # TODO change for model to deployment version
        """
        Set the model version
        :param id: id for the model version
        """
        self._model_version = id

    def set_deployment_id(self, id):
        """
        Set the deployment id
        :param id: id for the deployment
        """
        self._deployment_id = id

    def track(self, input, prediction):
        """
        To track the prediction of during the inference stage
        :param input: input dictionary with features being used for the prediction
        :param prediction: The output prediction from the model from the prediction being made
        :return: the id of the tracked prediction
        """
        if not (isinstance(input, dict) and isinstance(prediction, dict)):
            return None

        latency = self._end_time - self._start_time \
            if (self._end_time is not None and self._start_time is not None) else None
        cpu_percent = psutil.cpu_percent()
        memory_dict = {}
        memory_object = psutil.virtual_memory()
        for name in memory_object._fields:
            value = getattr(memory_object, name)
            if name != 'percent':
                value = bytes2human(value)
            memory_dict[name] = value

        input_data = {
            'cpu_percent': cpu_percent,
            'memory_dict': memory_dict,
            'input': json.dumps(input),
            'prediction': json.dumps(prediction),
            'model_id': self._model_id
        }
        if latency is not None:
            input_data['latency'] = latency
        if self._model_version is not None:
            input_data['model_version'] = self._model_version
        if self._deployment_id is not None:
            input_data['deployment_id'] = self._deployment_id

        response = self.remote_api.post_data(input_data)

        return response['body']['id']

    def track_actual(self, id, actual):
        """
        Return bool as True if it was a successful update
        :param actual: dictionary with actual data
        :return: bool
        """

        if not isinstance(actual, dict):
            return False
        response = self.remote_api.update_actual(id, json.dumps(actual))
        if response['body']['updated'] > 0:
            return True

    def get_meta_data(self, model_id, model_version=None, deployment_id=None, id=None):
        """
        Get and search for meta data from the remote storage
        :param model_id: id for the model
        :param model_version: version of the model
        :param deployment_id: id or type of deployment
        :param id: the id of the tracked prediction
        :return: list of all results for predictions which were tracked
        """
        filter = {'model_id': model_id}
        if model_version:
            filter['model_version'] = model_version
        if deployment_id:
            filter['deployment_id'] = deployment_id
        if id:
            filter['id'] = id
        response = self.remote_api.get_data(filter)
        body = response['body']
        meta_data_list = []
        for meta_data in body:
            input = meta_data.get("input")
            prediction = meta_data.get("prediction")
            actual = meta_data.get("actual")
            meta_data["input"] = json.loads(input) if input is not None else None
            meta_data["prediction"] = json.loads(prediction) if prediction is not None else None
            meta_data["actual"] = json.loads(actual) if actual is not None else None
            meta_data_list.append(meta_data)
        return meta_data_list

    def get_deployment_master_info(self):
        """
        To extract the master server of the deployment
        :return: dictionary containing the master server ip, grafana and kibana dashboard information
        """
        response = self.remote_api.get_deployment_info()
        master_system_info = response['body']['master_system_info']
        return master_system_info

    def get_deployment_cluster_info(self):
        """
        To extract the information about the deployments and services
        :return: dictionary containing the cluster information
        """
        response = self.remote_api.get_deployment_info()
        cluster_info = response['body']['cluster_info']
        return cluster_info