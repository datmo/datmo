"""
Tests for Environment
"""
from datmo.entity.environment import Environment


class TestEnvironment():
    def test_init(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "docker",
            "definition_filename": "Dockerfile",
            "hardware_info": {"system": "test"},
            "file_collection_id": "my_collection",
            "unique_hash": "sjfl39w",
            "language": "python3"
        }
        environment_entity = Environment(input_dict)

        for k, v in input_dict.items():
            assert getattr(environment_entity, k) == v
        assert environment_entity.description == ""
        assert environment_entity.created_at
        assert environment_entity.updated_at
        assert environment_entity.language

    def test_eq(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "docker",
            "definition_filename": "Dockerfile",
            "hardware_info": {"system": "test"},
            "file_collection_id": "my_collection",
            "unique_hash": "sjfl39w",
            "language": "python3"
        }
        environment_entity_1 = Environment(input_dict)
        environment_entity_2 = Environment(input_dict)

        assert environment_entity_1 == environment_entity_2

    def test_to_dictionary(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "docker",
            "definition_filename": "Dockerfile",
            "hardware_info": {"system": "test"},
            "file_collection_id": "my_collection",
            "unique_hash": "sjfl39w",
            "language": "python3"
        }
        environment_entity = Environment(input_dict)
        output_dict = environment_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(environment_entity, k)
