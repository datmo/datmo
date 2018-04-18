"""
Tests for Session
"""
from datmo.core.entity.session import Session


class TestSession():
    def test_init(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "name": "test"
        }
        session_entity = Session(input_dict)

        for k, v in input_dict.items():
            assert getattr(session_entity, k) == v
        assert session_entity.created_at
        assert session_entity.updated_at

    def test_eq(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "name": "test"
        }
        session_entity_1 = Session(input_dict)
        session_entity_2 = Session(input_dict)

        assert session_entity_1 == session_entity_2

    def test_to_dictionary(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "name": "test"
        }
        session_entity = Session(input_dict)
        output_dict = session_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(session_entity, k)
