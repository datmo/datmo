"""
Tests for Code
"""
from datmo.core.entity.code import Code

class TestCode():
    def setup_class(self):
        self.input_dict = {
            "model_id": "my_model",
            "driver_type": "git",
            "commit_id": "mycommit"
        }

    def test_init_no_id(self):
        code_entity = Code(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(code_entity, k) == v
        assert code_entity.id == None
        assert code_entity.created_at
        assert code_entity.updated_at

    def test_init_with_id(self):
        self.input_dict['id'] = "test"
        code_entity = Code(self.input_dict)
        for k, v in self.input_dict.items():
            assert getattr(code_entity, k) == v
        assert code_entity.created_at
        assert code_entity.updated_at

    def test_eq(self):
        code_entity_1 = Code(self.input_dict)
        code_entity_2 = Code(self.input_dict)
        assert code_entity_1 == code_entity_2

    def test_to_dictionary(self):
        code_entity = Code(self.input_dict)
        output_dict = code_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(code_entity, k)
