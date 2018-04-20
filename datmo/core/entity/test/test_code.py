"""
Tests for Code
"""
from datmo.core.entity.code import Code


class TestCode():
    def test_init(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "git",
            "commit_id": "mycommit"
        }
        code_entity = Code(input_dict)

        for k, v in input_dict.items():
            assert getattr(code_entity, k) == v
        assert code_entity.created_at
        assert code_entity.updated_at

    def test_eq(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "git",
            "commit_id": "mycommit"
        }
        code_entity_1 = Code(input_dict)
        code_entity_2 = Code(input_dict)
        assert code_entity_1 == code_entity_2

    def test_to_dictionary(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "git",
            "commit_id": "mycommit"
        }
        code_entity = Code(input_dict)
        output_dict = code_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(code_entity, k)
