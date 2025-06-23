"""
Tests for User
"""
from datmo.core.entity.user import User

class TestUser():
    def setup_class(self):
        self.input_dict = {"name": "test", "email": "test@test.com"}

    def test_init_no_id(self):
        user_entity = User(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(user_entity, k) == v
        assert user_entity.id == None
        assert user_entity.created_at
        assert user_entity.updated_at

    def test_init_with_id(self):
        self.input_dict['id'] = "test"
        user_entity = User(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(user_entity, k) == v
        assert user_entity.created_at
        assert user_entity.updated_at

    def test_eq(self):
        user_entity_1 = User(self.input_dict)
        user_entity_2 = User(self.input_dict)

        assert user_entity_1 == user_entity_2

    def test_to_dictionary(self):
        user_entity = User(self.input_dict)
        output_dict = user_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(user_entity, k)
