#!/usr/bin/python
"""
Tests for monitoring module
"""
import os
import tempfile
import platform
try:
    basestring
except NameError:
    basestring = str

from datmo.monitoring import Monitoring


class TestMonitoringModule():
    def setup_class(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        # TODO: move API key to environment variable
        self.monitoring = Monitoring(
            api_key="d41d8cd98f00b204e9800998ecf8427e")
        self.monitoring.set_model_id("model_id")
        self.monitoring.set_model_version_id("v3")
        self.monitoring.set_deployment_version_id("microservice")
        self.input_dict = {"test": 0.43}
        self.prediction_dict = {"test_output": 0.39}
        self.feedback_dict = {"real_output": 0.40}
        # TODO: move this only into test_set_track
        self.test_data_id = self.monitoring.track(
            input=self.input_dict, prediction=self.prediction_dict)

    def teardown_class(self):
        pass

    def test_set_track(self):
        assert isinstance(self.test_data_id, basestring)

    def test_set_track_double(self):
        data_id = self.monitoring.track(
            input=self.input_dict, prediction=self.prediction_dict)
        assert data_id != self.test_data_id

    def test_track_actual(self):
        result = self.monitoring.track_actual(
            id=self.test_data_id, actual=self.feedback_dict)
        assert isinstance(result, bool)
        assert result == True

    def test_search_metadata(self):
        filter = {"model_id": "model_id"}
        result = self.monitoring.search_metadata(filter)
        assert isinstance(result, list)
        assert len(result) >= 2

        filter = {"model_id": "model_id", "model_version_id": "v3"}
        result = self.monitoring.search_metadata(filter)
        assert isinstance(result, list)
        assert len(result) >= 2

        filter = {
            "model_id": "model_id",
            "deployment_version_id": "microservice"
        }
        result = self.monitoring.search_metadata(filter)
        assert isinstance(result, list)
        assert len(result) >= 2

        filter = {"model_id": "model_id", "id": self.test_data_id}
        result = self.monitoring.search_metadata(filter)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["updated_at"] > result[0]["created_at"]
        assert result[0]['id'] == self.test_data_id

        filter = {"model_id": "model_id", "start": 0, "count": 1}
        result = self.monitoring.search_metadata(filter)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_delete_meta_data(self):
        filter = {"model_id": "model_id", "id": self.test_data_id}
        result = self.monitoring.delete_metadata(filter)
        assert isinstance(result, dict)
        assert result['total'] == 1
        assert result['deleted'] == 1

    # TODO: separate deployment into another file

    def test_get_deployment_master_info(self):
        result = self.monitoring._get_datmo_deployment_master_info()
        assert isinstance(result, dict)
        assert isinstance(result['datmo_master_ip'], basestring)
        assert isinstance(result['kibana_dashboard'], dict)
        assert isinstance(result['grafana_dashboard'], dict)

    def test_get_deployment_cluster_info(self):
        result = self.monitoring._get_datmo_deployment_cluster_info()
        assert isinstance(result, dict)
        assert isinstance(result['clusters'], list)
        assert len(result['clusters']) == 1
