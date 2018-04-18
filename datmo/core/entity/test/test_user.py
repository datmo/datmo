"""
Tests for User
"""
from datmo.core.entity.user import User


class TestUser():
    def test_init(self):
        input_dict = {
            "id": "test",
            "name": "test",
            "email": "test@test.com"
        }
        user_entity = User(input_dict)

        for k, v in input_dict.items():
            assert getattr(user_entity, k) == v
        assert user_entity.created_at
        assert user_entity.updated_at

    def test_eq(self):
        input_dict = {
            "id": "test",
            "name": "test",
            "email": "test@test.com"
        }
        user_entity_1 = User(input_dict)
        user_entity_2 = User(input_dict)

        assert user_entity_1 == user_entity_2

    def test_to_dictionary(self):
        input_dict = {
            "id": "test",
            "name": "test",
            "email": "test@test.com"
        }
        user_entity = User(input_dict)
        output_dict = user_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(user_entity, k)
