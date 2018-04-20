"""
Tests for Model
"""
from datmo.core.entity.model import Model


class TestModel():
    def test_init(self):
        input_dict = {
            "id": "test",
            "name": "test"
        }
        model_entity = Model(input_dict)

        for k, v in input_dict.items():
            assert getattr(model_entity, k) == v
        assert model_entity.description == ""
        assert model_entity.created_at
        assert model_entity.updated_at

    def test_eq(self):
        input_dict = {
            "id": "test",
            "name": "test"
        }
        model_entity_1 = Model(input_dict)
        model_entity_2 = Model(input_dict)

        assert model_entity_1 == model_entity_2

    def test_to_dictionary(self):
        input_dict = {
            "id": "test",
            "name": "test",
        }
        model_entity = Model(input_dict)
        output_dict = model_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(model_entity, k)
