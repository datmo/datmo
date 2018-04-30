"""
Tests for Task
"""
from datmo.core.entity.task import Task


class TestTask():
    def setup_class(self):
        self.input_dict = {
            "model_id": "my_model",
            "session_id": "my_session",
            "command": "python test.py"
        }

    def test_init_no_id(self):
        task_entity = Task(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(task_entity, k) == v
        assert task_entity.id == None
        assert task_entity.before_snapshot_id == ""
        assert task_entity.ports == []
        assert task_entity.gpu == False
        assert task_entity.interactive == False
        assert task_entity.task_dirpath == ""
        assert task_entity.log_filepath == ""
        assert task_entity.start_time == None

        # Post-Execution
        assert task_entity.after_snapshot_id == ""
        assert task_entity.run_id == ""
        assert task_entity.logs == ""
        assert task_entity.status == ""
        assert task_entity.results == {}
        assert task_entity.end_time == None
        assert task_entity.duration == None
        assert task_entity.created_at
        assert task_entity.updated_at

    def test_init_with_id(self):
        self.input_dict['id'] = "test"
        task_entity = Task(self.input_dict)

        for k, v in self.input_dict.items():
            assert getattr(task_entity, k) == v
        assert task_entity.before_snapshot_id == ""
        assert task_entity.ports == []
        assert task_entity.gpu == False
        assert task_entity.interactive == False
        assert task_entity.task_dirpath == ""
        assert task_entity.log_filepath == ""
        assert task_entity.start_time == None

        # Post-Execution
        assert task_entity.after_snapshot_id == ""
        assert task_entity.run_id == ""
        assert task_entity.logs == ""
        assert task_entity.status == ""
        assert task_entity.results == {}
        assert task_entity.end_time == None
        assert task_entity.duration == None
        assert task_entity.created_at
        assert task_entity.updated_at

    def test_eq(self):
        task_entity_1 = Task(self.input_dict)
        task_entity_2 = Task(self.input_dict)

        assert task_entity_1 == task_entity_2

    def test_to_dictionary(self):
        task_entity = Task(self.input_dict)
        output_dict = task_entity.to_dictionary()

        for k, v in output_dict.items():
            assert v == getattr(task_entity, k)
