"""
Tests for Run
"""
from datmo.core.entity.task import Task as CoreTask
from datmo.core.entity.run import Run

class TestRun():
    def setup_class(self):
        self.task_dict = {
            "id": "test",
            "model_id": "my_model",
            "command": "python test.py"
        }

    def test_run_object_instantiate(self):
        task_obj = CoreTask(self.task_dict)
        result = Run(task_obj)
        assert result
        assert isinstance(result, Run)