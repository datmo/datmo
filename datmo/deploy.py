from celery import Celery

from datmo.core.util.remote_api import RemoteAPI


class Deploy():
    """Class for deployment Datmo services

    Parameters
    ----------
    api_key : str, optional
        credentials to access remote

    Attributes
    ----------
    api_key : str
        the api key used for accessing the datmo service
    celery_app : celery.app
        celery application to use

    Examples
    --------
    You can use this function within a project repository to track predicitons
    or inferences. Once you have created this, you will be able to view them on
    the monitoring dashboard

    >>> from datmo.deploy import Deploy
    >>> datmo_deploy = Deploy(api_key="my_data_api_key")
    >>>
    >>> @datmo_deploy.method()
    >>> def predict(x):
    >>>     y_predict = model_predict(x) # using a machine learning model for inference
    >>>     datmo_id = datmo_client.track(input=x, prediction=y_predict) # Track predictions
    >>>     response = {'y': y, 'datmo_id': datmo_id}
    >>>     return response
    ...
    $ datmo deploy
    """

    def __init__(self, api_key=None):
        self._api_key = api_key
        self._celery_app = Celery()
        self.remote_api = RemoteAPI(self._api_key)
        self._start_time, self._end_time, self._model_id, \
        self._model_version_id, self._deployment_version_id = None, None, None, None, None

    def method(self):
        """
        Wrapper for the celery decorator
        """
        return self._celery_app.task(bind=True, soft_time_limit=1000)
