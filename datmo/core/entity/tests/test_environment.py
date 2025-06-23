"""
Tests for Environment
"""
from datmo.core.entity.environment import Environment

class TestEnvironment():
    def setup_method(self):
        self.input_dict = {
            "model_id": "my_model",
            "driver_type": "docker",
            "definition_filename": "Dockerfile",
            "hardware_info": {
                "system": "test"
            },
            "file_collection_id": "my_collection",
            "unique_hash": "sjfl39w"
        }

    def test_init_no_id(self):
        environment_entity = Environment(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(environment_entity, k) == v
        assert environment_entity.id == None
        assert environment_entity.name == None
        assert environment_entity.description == None
        assert environment_entity.created_at
        assert environment_entity.updated_at

    def test_init_with_id(self):
        self.input_dict['id'] = "test"
        environment_entity = Environment(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(environment_entity, k) == v
        assert environment_entity.name == None
        assert environment_entity.description == None
        assert environment_entity.created_at
        assert environment_entity.updated_at

    def test_eq(self):
        environment_entity_1 = Environment(self.input_dict)
        environment_entity_2 = Environment(self.input_dict)

        assert environment_entity_1 == environment_entity_2

    def test_to_dictionary(self):
        environment_entity = Environment(self.input_dict)
        output_dict = environment_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(environment_entity, k)
