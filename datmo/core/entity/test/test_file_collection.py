"""
Tests for FileCollection
"""
from datmo.core.entity.file_collection import FileCollection


class TestFileCollection():
    def setup_class(self):
        self.input_dict = {
            "id": "test",
            "model_id": "my_model",
            "driver_type": "docker",
            "filehash": "myhash",
            "path": "/path/to/file",
        }

    def test_init(self):
        file_collection_entity = FileCollection(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(file_collection_entity, k) == v
        assert file_collection_entity.created_at
        assert file_collection_entity.updated_at

    def test_eq(self):
        file_collection_entity_1 = FileCollection(self.input_dict)
        file_collection_entity_2 = FileCollection(self.input_dict)
        assert file_collection_entity_1 == file_collection_entity_2

    def test_to_dictionary(self):
        file_collection_entity = FileCollection(self.input_dict)
        output_dict = file_collection_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(file_collection_entity, k)
