"""
Tests for task module
"""
import os
import tempfile
import platform
import datetime
from io import open, TextIOWrapper
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.task import run, ls
from datmo.task import Task
from datmo.core.entity.task import Task as CoreTask
from datmo.core.controller.project import ProjectController
from datmo.core.util.exceptions import (GitCommitDoesNotExist, DoesNotExist,
                                        InvalidProjectPath,
                                        SessionDoesNotExist)
from datmo.core.util.misc_functions import pytest_docker_environment_failed_instantiation

# provide mountable tmp directory for docker
tempfile.tempdir = "/tmp" if not platform.system() == "Windows" else None
test_datmo_dir = os.environ.get('TEST_DATMO_DIR', tempfile.gettempdir())


class TestTaskModule():
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)
        _ = ProjectController(self.temp_dir).\
            init("test", "test description")
        self.input_dict = {
            "id": "test",
            "model_id": "my_model",
            "session_id": "my_session",
            "command": "python test.py"
        }

    def teardown_method(self):
        pass

    def test_task_entity_instantiate(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)

        for k, v in self.input_dict.items():
            assert getattr(task_entity, k) == v

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_run(self):
        # 1) Run task with no commit or code available (cannot save states before), string command
        # 2) Run task with simple python file, no environment definition, string command (auto generate env)
        # 3) Run task with simple python file and environment definition, string command
        # 4) Run task with simple python file and environment definition, list command

        # 1) Test out option 1)
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
            f.write(to_unicode("import os\n"))
            f.write(to_unicode("import sys\n"))
            f.write(to_unicode("print('hello')\n"))
            f.write(to_unicode("print(' accuracy: 0.56 ')\n"))

        # 2) Test out option 2
        task_obj_0 = run(command="python script.py", home=self.temp_dir)
        assert isinstance(task_obj_0, Task)
        assert task_obj_0.id
        assert 'hello' in task_obj_0.logs
        assert task_obj_0.results == {"accuracy": "0.56"}

        # Add environment definition
        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))

        # 3) Test out option 3
        task_obj_1 = run(
            command="python script.py", env=test_filepath, home=self.temp_dir)
        assert isinstance(task_obj_1, Task)
        assert task_obj_1.id
        assert 'hello' in task_obj_1.logs
        assert task_obj_1.results == {"accuracy": "0.56"}

        # 4) Test out option 4
        task_obj_2 = run(
            command=["python", "script.py"],
            env=test_filepath,
            home=self.temp_dir)
        assert isinstance(task_obj_2, Task)
        assert task_obj_2.id
        assert 'hello' in task_obj_2.logs
        assert task_obj_2.results == {"accuracy": "0.56"}

    def test_ls(self):
        # check project is not initialized if wrong home
        failed = False
        try:
            ls(home=os.path.join("does", "not", "exist"))
        except InvalidProjectPath:
            failed = True
        assert failed

        # check session does not exist if wrong session
        failed = False
        try:
            ls(session_id="does_not_exist", home=self.temp_dir)
        except SessionDoesNotExist:
            failed = True
        assert failed

        # run a task with default params
        self.__setup()

        # list all tasks with no filters
        task_list_1 = ls(home=self.temp_dir)

        assert task_list_1
        assert len(list(task_list_1)) == 1
        assert isinstance(task_list_1[0], Task)

        # run another task with default params
        self.__setup(command="test")

        # list all tasks with no filters (works when more than 1 task)
        task_list_2 = ls(home=self.temp_dir)

        assert task_list_2
        assert len(list(task_list_2)) == 2
        assert isinstance(task_list_2[0], Task)
        assert isinstance(task_list_2[1], Task)

        # list tasks with specific filter
        task_list_3 = ls(filter="script.py", home=self.temp_dir)

        assert task_list_3
        assert len(list(task_list_3)) == 1
        assert isinstance(task_list_3[0], Task)

        # list snapshots with filter of none
        task_list_4 = ls(filter="random", home=self.temp_dir)

        assert len(list(task_list_4)) == 0

    def __setup(self, command="python script.py"):
        # Create a basic task and run it with string command
        test_filepath = os.path.join(self.temp_dir, "script.py")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("import numpy\n"))
            f.write(to_unicode("import sklearn\n"))
            f.write(to_unicode("print 'hello'\n"))

        test_filepath = os.path.join(self.temp_dir, "Dockerfile")
        with open(test_filepath, "w") as f:
            f.write(to_unicode("FROM datmo/xgboost:cpu"))

        return run(command=command, env=test_filepath, home=self.temp_dir)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_status(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.status
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.status

        assert result
        assert isinstance(result, to_unicode)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_start_time(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.start_time
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.start_time

        assert result
        assert isinstance(result, datetime.datetime)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_end_time(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.end_time
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.end_time

        assert result
        assert isinstance(result, datetime.datetime)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_duration(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.duration
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.duration

        assert result
        assert isinstance(result, float)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_logs(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.logs
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.logs

        assert result
        assert isinstance(result, to_unicode)

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_results(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.results
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.results

        assert isinstance(result, dict)
        assert result == {}

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_files(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.files
        except DoesNotExist:
            failed = True
        assert failed
        # Test success
        task_entity = self.__setup()
        result = task_entity.files

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].mode == "r"
        assert result[0].name

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_get_files(self):
        core_task_entity = CoreTask(self.input_dict)
        task_entity = Task(core_task_entity, home=self.temp_dir)
        # Test failure because entity has not been created by controller
        failed = False
        try:
            task_entity.get_files()
        except DoesNotExist:
            failed = True
        assert failed

        task_entity = self.__setup()
        result = task_entity.get_files()

        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].mode == "r"
        assert result[0].name

        result = task_entity.get_files(mode="a")
        assert len(result) == 1
        assert isinstance(result[0], TextIOWrapper)
        assert result[0].mode == "a"
        assert result[0].name

    @pytest_docker_environment_failed_instantiation(test_datmo_dir)
    def test_task_entity_str(self):
        task_entity = self.__setup()
        for k in self.input_dict:
            if k != "model_id":
                assert str(task_entity.__dict__[k]) in str(task_entity)