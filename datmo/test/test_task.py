"""
Tests for task module
"""
import os
import shutil
import tempfile
import platform
from io import open, TextIOWrapper
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.task import run
from datmo.task import Task
from datmo.core.entity.task import Task as CoreTask
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import GitCommitDoesNotExist, \
    EntityNotFound


class TestTaskModule():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        _ = ProjectController(self.temp_dir).\
            init("test", "test description")

    def teardown_method(self):
        pass

    def test_task_entity_instantiate(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "session_id": "my_session",
            "command": "python test.py"
        }
        core_task_entity = CoreTask(input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)

        for k, v in input_dict.items():
            assert getattr(task_entity, k) == v
        assert task_entity.status == ""
        assert task_entity.start_time == None
        assert task_entity.end_time == None
        assert task_entity.duration == None
        assert task_entity.logs == ""
        assert task_entity.results == {}

    def test_run(self):
        # Try task run with no commit (cannot save states before)
        failed = False
        try:
            _ = run(command="test", home=self.temp_dir)
        except GitCommitDoesNotExist:
            failed = True
        assert failed

        # Create a basic task and run it with string command
        # (fails w/ no environment)
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print 'hello'\n"))

        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))

        task_obj_1 = run(command="python script.py", env=test_filepath,
                         home=self.temp_dir)
        assert isinstance(task_obj_1, Task)
        assert task_obj_1.id
        assert 'hello' in task_obj_1.logs

        # Run task with list as command
        task_obj_2 = run(command=["python", "script.py"], env=test_filepath,
                         home=self.temp_dir)
        assert isinstance(task_obj_2, Task)
        assert task_obj_2.id
        assert 'hello' in task_obj_2.logs

    def test_task_entity_files(self):
        input_dict = {
            "id": "test",
            "model_id": "my_model",
            "session_id": "my_session",
            "command": "python test.py"
        }
        core_task_entity = CoreTask(input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.files()
        except EntityNotFound:
            failed = True
        assert failed

        # Create a basic task and run it with string command
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print 'hello'\n"))

        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))

        task_entity = run(command="python script.py", env=test_filepath,
                          home=self.temp_dir)
        result = task_entity.files()

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].name
