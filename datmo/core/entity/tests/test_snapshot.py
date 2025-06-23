"""
Tests for Snapshot
"""
from datmo.core.entity.snapshot import Snapshot

class TestSnapshot():
    def setup_class(self):
        self.input_dict = {
            "model_id": "my_model",
            "message": "my message",
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

    def test_init_no_id(self):
        snapshot_entity = Snapshot(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(snapshot_entity, k) == v
        assert snapshot_entity.id == None
        assert snapshot_entity.task_id == None
        assert snapshot_entity.label == None
        assert snapshot_entity.visible == True
        assert snapshot_entity.created_at
        assert snapshot_entity.updated_at

    def test_init_with_id(self):
        self.input_dict['id'] = "test"
        snapshot_entity = Snapshot(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(snapshot_entity, k) == v
        assert snapshot_entity.task_id == None
        assert snapshot_entity.label == None
        assert snapshot_entity.visible == True
        assert snapshot_entity.created_at
        assert snapshot_entity.updated_at

    def test_eq(self):
        snapshot_entity_1 = Snapshot(self.input_dict)
        snapshot_entity_2 = Snapshot(self.input_dict)

        assert snapshot_entity_1 == snapshot_entity_2

    def test_str(self):
        snapshot_entity = Snapshot(self.input_dict)
        for k, v in self.input_dict.items():
            if k != "model_id":
                assert str(v) in str(snapshot_entity)

    def test_to_dictionary(self):
        snapshot_entity = Snapshot(self.input_dict)
        output_dict = snapshot_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(snapshot_entity, k)

        # Test stringify
        output_dict = snapshot_entity.to_dictionary(stringify=True)

        for k, v in output_dict.items():
            if k in [
                    "config", "stats", "message", "label", "created_at",
                    "updated_at"
            ]:
                assert isinstance(k, str)
            else:
                assert v == getattr(snapshot_entity, k)
