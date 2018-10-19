import time
import json
import psutil
from datetime import datetime

from datmo.core.util.exceptions import InputError
from datmo.core.util.misc_functions import bytes2human
from datmo.core.util.remote_api import RemoteAPI


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
    >>> datmo_client = Monitoring(api_key="my_data_api_key")
    >>> datmo_client.set_model_version_id("v3")
    >>> datmo_client.set_model_id("model_id")
    >>> datmo_client.set_deployment_version_id("microservice")
    >>> def predict(x):
    >>>     datmo_client.set_start_time()
    >>>     y_predict = model_predict(x) # using a machine learning model for inference
    >>>     datmo_model.set_end_time()
    >>>     datmo_id = datmo_client.track(input=x, prediction=y_predict) # Track predictions
    >>>     response = {'y': y, 'datmo_id': datmo_id}
    >>>     return response
    ...
    >>> response = predict(x)
    ...
    >>> # For feedback
    >>> datmo_client.track_feedback(id=response['datmo_id'], actual=y_actual)
    """

    def __init__(self, api_key, home=None):
        self._api_key = api_key
        self.remote_api = RemoteAPI(self._api_key)
        self._start_time, self._end_time, self._model_id, \
        self._model_version_id, self._deployment_version_id = None, None, None, None, None

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        pass

    def __repr__(self):
        return self.__str__()

    @property
    def set_start_time(self):
        """
        Set the start time

        Returns
        -------
        start_time : int
            start time in milliseconds
        """
        self._start_time = int(round(time.time() * 1000))
        return self._start_time

    @property
    def set_end_time(self):
        """
        Set the end time

        Returns
        -------
        end_time : int
            end time in milliseconds
        """
        self._end_time = int(round(time.time() * 1000))
        return self._end_time

    def set_model_id(self, id):
        """
        Set the model id

        Parameters
        ----------
        id : str
            model id to track during monitoring
        """
        self._model_id = id

    def set_model_version_id(self, id):
        # TODO change for model to deployment version
        """
        Set the model version id

        Parameters
        ----------
        id : str
            model version id to track during monitoring
        """
        self._model_version_id = id

    def set_deployment_version_id(self, id):
        """
        Set the deployment version id

        Parameters
        ----------
        id : str
            deployment version id to track during monitoring
        """
        self._deployment_version_id = id

    def track(self, input, prediction):
        """
        To track the prediction of during the inference stage

        Parameters
        ----------
        input : dict
            input dictionary with features being used for the prediction
        prediction : dict
            The output prediction from the model from the prediction being made

        Returns
        -------
        id : str
            the id of the tracked prediction
        """
        if not (isinstance(input, dict) and isinstance(prediction, dict)):
            return None

        if self._start_time and self._end_time:
            latency = self._end_time - self._start_time
        elif self._start_time and not self._end_time:
            self._end_time = int(round(time.time() * 1000))
            latency = self._end_time - self._start_time
        else:
            latency = None
        self._start_time, self._end_time = None, None  # reset both for next data point
        created_at = int(round(time.time() * 1000))
        cpu_percent = psutil.cpu_percent()
        memory_dict = {}
        memory_object = psutil.virtual_memory()
        for name in memory_object._fields:
            value = getattr(memory_object, name)
            if name != "percent":
                value = bytes2human(value)
            memory_dict[name] = value

        input_data = {
            "cpu_percent": cpu_percent,
            "memory_dict": memory_dict,
            "input": json.dumps(input),
            "prediction": json.dumps(prediction),
            "model_id": self._model_id,
            "created_at": created_at
        }
        if latency is not None:
            input_data['latency'] = latency
        if self._model_version_id is not None:
            input_data['model_version_id'] = self._model_version_id
        if self._deployment_version_id is not None:
            input_data['deployment_version_id'] = self._deployment_version_id

        response = self.remote_api.post_data(input_data)

        return response['body']['id']

    def track_feedback(self, id, feedback):
        """
        Track feedback value (y) and other metrics after the prediction(y_hat)

        Parameters
        ----------
        id : str
            tracked prediction id as returned by "track" function above
        actual : dict
            dictionary with ground truth data for the actual prediction

        Returns
        -------
        bool
            True if successful update
        """
        if not isinstance(feedback, dict):
            return False
        updated_at = int(round(time.time() * 1000))
        update_dict = {
            'updated_at': updated_at,
            'feedback': json.dumps(feedback)
        }
        response = self.remote_api.update_actual(id, update_dict)
        body = response.get('body')
        updated_at = body.get('updated') if body else 0
        if updated_at > 0:
            return True
        else:
            return False

    def search_metadata(self, filter):
        """
        Search metadata from the remote storage

        Parameters
        ----------
        filter : dict
            dictionary to filter search results

            model_id : str, optional
                model id tracked for monitoring. default to self._model_id if present
            model_version_id : str, optional
                model version id tracked for monitoring. default to self._model_version_id if present
            deployment_version_id : str, optional
                deployment version id tracked for monitoring. default to self._deployment_version_id if present
            id  : str, optional
                tracked prediction id
            start : int, optional
                initial index of doc to get from storage for pagination purpose
            count : int, optional
                total number of docs to get from storage in single call from start
            sort_created_at : str, optional
                to sort the docs based on created at, by default it sorts on asc

        Returns
        -------
        list
            list of data dictionary for predictions which were tracked

        Raises
        ------
        IncorrectType
        """
        # Check if all input dictionary keys are valid
        if not all(key in [
                "model_id", "model_version_id", "deployment_version_id", "id",
                "start", "count", "sort_created_at"
        ] for key in filter.keys()):
            raise InputError
        filter['model_id'] = filter.get('model_id', self._model_id)
        if filter['model_id'] is None: del filter['model_id']
        filter['model_version_id'] = filter.get('model_version_id',
                                                self._model_version_id)
        if filter['model_version_id'] is None: del filter['model_version_id']
        filter['deployment_version_id'] = filter.get(
            'deployment_version_id', self._deployment_version_id)
        if filter['deployment_version_id'] is None:
            del filter['deployment_version_id']
        response = self.remote_api.get_data(filter)
        body = response['body']
        meta_data_list = []
        for meta_data in body:
            input = meta_data.get('input')
            prediction = meta_data.get('prediction')
            feedback = meta_data.get('feedback')
            updated_at = meta_data.get('updated_at')
            meta_data['input'] = json.loads(
                input) if input is not None else None
            meta_data['prediction'] = json.loads(
                prediction) if prediction is not None else None
            meta_data['feedback'] = json.loads(
                feedback) if feedback is not None else None
            meta_data['updated_at'] = int(
                updated_at) if updated_at is not None else None
            meta_data_list.append(meta_data)
        return meta_data_list

    def delete_metadata(self, filter):
        """
        Delete metadata from the remote storage

        Parameters
        ----------
        filter : dict
            dictionary to delete filtered search results

            model_id : str, optional
                model id tracked for monitoring
            model_version_id : str, optional
                model version id tracked for monitoring
            deployment_version_id : str, optional
                deployment version id tracked for monitoring
            id  : str, optional
                tracked prediction id

        Returns
        -------
        dict
            dictionary with response after deletion of docs in remote storage

        Raises
        ------
        IncorrectType
        """
        # Check if all input dictionary keys are valid
        if not all(
                key in
            ["model_id", "model_version_id", "deployment_version_id", "id"]
                for key in filter.keys()):
            raise InputError
        response = self.remote_api.delete_data(filter)
        body = response['body']

        return body

    # TODO: separate deployment into another file

    def get_deployment_info(self, type="datmo", deployment_version_id=None):
        """

        Parameters
        ----------
        type : str, optional
            type of deployment (e.g. "datmo", "sagemaker", etc)
        deployment_version_id : str, optional
            deployment version id for the deployment to get info
        model_version_Id : str, optional
            model version id for the deployment
        model_id : str, optional
            model id for the deployment

        Returns
        -------
        dict
            dictionary containing the information for the deployment

            type : str
                deployment type (e.g. "datmo", "sagemaker", etc)
            deployment_version_id : str
                deployment version id for the deployment
            model_version_id : str
                model version id for the deployment
            created_at : datetime.datetime
                launch time of deployment
            endpoints : list
                list of urls to access prediction for the deployment
            service_paths : list
                list of relative path and identifier for specific deployment
            system_monitoring : dict
                endpoint : str
                    url to access the grafana dashboard for system monitoring
                username : str
                    username for authentication
                password : str
                    password for authentication
            log_monitoring : str
                url to access the kibana dashboard for log monitoring
        """
        master_info = self._get_datmo_deployment_master_info()
        cluster_info = self._get_datmo_deployment_cluster_info()
        launch_time = datetime.strptime(
            cluster_info['clusters'][0]['instances'][0]['LaunchTime'],
            '%Y-%m-%dT%H:%M:%S.%fZ')
        endpoints = [
            service['url']
            for service in cluster_info['clusters'][0]['services']
        ]
        service_paths = [
            service['route']
            for service in cluster_info['clusters'][0]['services']
        ]
        deployment_info = {
            "type": type,
            "deployment_version_id": None,
            "model_version_id": None,
            "created_at": launch_time,
            "endpoints": endpoints,
            "service_paths": service_paths,
            "system_monitoring": {
                "endpoint": master_info['grafana_dashboard']['end_point'],
                "username": master_info['grafana_dashboard']['user_name'],
                "password": master_info['grafana_dashboard']['password']
            },
            "log_monitoring": master_info['kibana_dashboard']['end_point']
        }
        return deployment_info

    def _get_datmo_deployment_master_info(self):
        """
        Extract the master server of the deployment
    
        Returns
        -------
        dict
            dictionary containing the master server ip, grafana and kibana dashboard information

            datmo_master_ip : str
            kibana_dashboard : dict
                end_point : str
            grafana_dashboard : dict
                end_point : str
                user_name : str
                password : str
        """
        response = self.remote_api.get_deployment_info()
        master_system_info = response['body']['master_system_info']
        return master_system_info

    def _get_datmo_deployment_cluster_info(self):
        """
        To extract the information about the deployments and services

        Returns
        -------
        dict
            dictionary containing the cluster information

            Example
            -------
            {
               'clusters':[
                  {
                     'count':1,
                     'services':[
                        {
                           'url':'http://acme-company-deploy.datmo.com:2053/credit/shabazp/xgboost-model/v1/predict',
                           'route':'/credit/shabazp/xgboost-model/v1/predict'
                        },
                        {
                           'url':'http://acme-company-deploy.datmo.com:2053/credit/shabazp/xgboost-model/v1/add',
                           'route':'/credit/shabazp/xgboost-model/v1/add'
                        }
                     ],
                     'instances':[
                        {
                           'Monitoring':{
                              'State':'disabled'
                           },
                           'PublicDnsName':'ec2-18-202-54-17.eu-west-1.compute.amazonaws.com',
                           'ElasticGpuAssociations':[

                           ],
                           'State':{
                              'Code':16,
                              'Name':'running'
                           },
                           'EbsOptimized':False,
                           'LaunchTime':'2018-10-12T03:05:43.000Z',
                           'PublicIpAddress':'18.202.54.17',
                           'PrivateIpAddress':'10.0.14.216',
                           'ProductCodes':[

                           ],
                           'VpcId':'vpc-0562003fd66d02b39',
                           'CpuOptions':{
                              'CoreCount':1,
                              'ThreadsPerCore':1
                           },
                           'StateTransitionReason':'',
                           'InstanceId':'i-06f20e7a98674d402',
                           'EnaSupport':True,
                           'ImageId':'ami-1557d26c',
                           'PrivateDnsName':'ip-10-0-14-216.eu-west-1.compute.internal',
                           'KeyName':'datmo-key',
                           'SecurityGroups':[
                              {
                                 'GroupName':'datmo-cluster',
                                 'GroupId':'sg-0484ece16c5263c3e'
                              }
                           ],
                           'ClientToken':'',
                           'SubnetId':'subnet-0569e7224a5dc81f3',
                           'InstanceType':'t2.small',
                           'NetworkInterfaces':[
                              {
                                 'Status':'in-use',
                                 'MacAddress':'0a:8b:b0:a8:61:a2',
                                 'SourceDestCheck':True,
                                 'VpcId':'vpc-0562003fd66d02b39',
                                 'Description':'',
                                 'NetworkInterfaceId':'eni-09bb85544df95ad2b',
                                 'PrivateIpAddresses':[
                                    {
                                       'PrivateDnsName':'ip-10-0-14-216.eu-west-1.compute.internal',
                                       'PrivateIpAddress':'10.0.14.216',
                                       'Primary':True,
                                       'Association':{
                                          'PublicIp':'18.202.54.17',
                                          'PublicDnsName':'ec2-18-202-54-17.eu-west-1.compute.amazonaws.com',
                                          'IpOwnerId':'amazon'
                                       }
                                    }
                                 ],
                                 'PrivateDnsName':'ip-10-0-14-216.eu-west-1.compute.internal',
                                 'Attachment':{
                                    'Status':'attached',
                                    'DeviceIndex':0,
                                    'DeleteOnTermination':True,
                                    'AttachmentId':'eni-attach-0e2d2d5e6f8b1389c',
                                    'AttachTime':'2018-10-12T03:05:43.000Z'
                                 },
                                 'Groups':[
                                    {
                                       'GroupName':'datmo-cluster',
                                       'GroupId':'sg-0484ece16c5263c3e'
                                    }
                                 ],
                                 'Ipv6Addresses':[

                                 ],
                                 'OwnerId':'373706122488',
                                 'PrivateIpAddress':'10.0.14.216',
                                 'SubnetId':'subnet-0569e7224a5dc81f3',
                                 'Association':{
                                    'PublicIp':'18.202.54.17',
                                    'PublicDnsName':'ec2-18-202-54-17.eu-west-1.compute.amazonaws.com',
                                    'IpOwnerId':'amazon'
                                 }
                              }
                           ],
                           'SourceDestCheck':True,
                           'Placement':{
                              'Tenancy':'default',
                              'GroupName':'',
                              'AvailabilityZone':'eu-west-1a'
                           },
                           'Hypervisor':'xen',
                           'BlockDeviceMappings':[
                              {
                                 'DeviceName':'/dev/sda1',
                                 'Ebs':{
                                    'Status':'attached',
                                    'DeleteOnTermination':True,
                                    'VolumeId':'vol-01e2990ce94b6d700',
                                    'AttachTime':'2018-10-12T03:05:44.000Z'
                                 }
                              }
                           ],
                           'Architecture':'x86_64',
                           'RootDeviceType':'ebs',
                           'RootDeviceName':'/dev/sda1',
                           'VirtualizationType':'hvm',
                           'Tags':[
                              {
                                 'Value':'credit',
                                 'Key':'cluster'
                              },
                              {
                                 'Value':'datmo',
                                 'Key':'Creator'
                              },
                              {
                                 'Value':'datmo-cluster-credit-0',
                                 'Key':'Name'
                              }
                           ],
                           'AmiLaunchIndex':0
                        }
                     ],
                     'name':'credit',
                     'server_type':'t2.small'
                  }
               ]
            }
        """
        response = self.remote_api.get_deployment_info()
        cluster_info = response['body']['cluster_info']
        return cluster_info
