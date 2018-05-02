"""
Tests for Session
"""
from datmo.core.entity.session import Session


class TestSession():
    def setup_class(self):
        self.input_dict = {
            "model_id": "my_model",
            "name": "test"
        }

    def test_init_no_id(self):
        session_entity = Session(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(session_entity, k) == v
        assert session_entity.id == None
        assert session_entity.created_at
        assert session_entity.updated_at

    def test_init_with_id(self):
        session_entity = Session(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(session_entity, k) == v
        assert session_entity.created_at
        assert session_entity.updated_at

    def test_eq(self):
        session_entity_1 = Session(self.input_dict)
        session_entity_2 = Session(self.input_dict)

        assert session_entity_1 == session_entity_2

    def test_to_dictionary(self):
        session_entity = Session(self.input_dict)
        output_dict = session_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(session_entity, k)
