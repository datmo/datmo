"""
Tests for Snapshot
"""
from datmo.core.entity.snapshot import Snapshot


class TestSnapshot():
    def test_init(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "code_id": "code_id",
            "environment_id": "environment_id",
            "file_collection_id": "file_collection_id",
            "config": {
                "hyperparameter": 0.8
            },
            "stats": {
                "performance": 0.98
            }
        }
        snapshot_entity = Snapshot(input_dict)

        for k, v in input_dict.items():
            assert getattr(snapshot_entity, k) == v
        assert snapshot_entity.session_id == ""
        assert snapshot_entity.task_id == ""
        assert snapshot_entity.message == ""
        assert snapshot_entity.label == ""
        assert snapshot_entity.visible == True
        assert snapshot_entity.created_at
        assert snapshot_entity.updated_at

    def test_eq(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "code_id": "code_id",
            "environment_id": "environment_id",
            "file_collection_id": "file_collection_id",
            "config": {
                "hyperparameter": 0.8
            },
            "stats": {
                "performance": 0.98
            }
        }
        snapshot_entity_1 = Snapshot(input_dict)
        snapshot_entity_2 = Snapshot(input_dict)

        assert snapshot_entity_1 == snapshot_entity_2

    def test_to_dictionary(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "code_id": "code_id",
            "environment_id": "environment_id",
            "file_collection_id": "file_collection_id",
            "config": {
                "hyperparameter": 0.8
            },
            "stats": {
                "performance": 0.98
            }
        }
        snapshot_entity = Snapshot(input_dict)
        output_dict = snapshot_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(snapshot_entity, k)
