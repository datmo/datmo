"""
Tests for Model
"""
from datmo.core.entity.model import Model

class TestModel():
    def setup_class(self):
        self.input_dict = {"name": "test"}

    def test_init_no_id(self):
        model_entity = Model(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(model_entity, k) == v
        assert model_entity.id == None
        assert model_entity.description == None
        assert model_entity.created_at
        assert model_entity.updated_at

    def test_init_with_id(self):
        self.input_dict['id'] = "test"
        model_entity = Model(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(model_entity, k) == v
        assert model_entity.description == None
        assert model_entity.created_at
        assert model_entity.updated_at

    def test_eq(self):
        model_entity_1 = Model(self.input_dict)
        model_entity_2 = Model(self.input_dict)

        assert model_entity_1 == model_entity_2

    def test_to_dictionary(self):
        model_entity = Model(self.input_dict)
        output_dict = model_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(model_entity, k)
