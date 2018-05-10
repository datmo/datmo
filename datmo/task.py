import os
import shlex
import platform
try:
    basestring
except NameError:
    basestring = str

from datmo.core.controller.task import TaskController
from datmo.core.entity.task import Task as CoreTask
from datmo.core.util.exceptions import InvalidArgumentType


class Task():
    """Task is an entity object to enable user access to properties

    Parameters
    ----------
    task_entity : datmo.core.entity.task.Task
        core task entity to reference
    home : str, optional
        root directory of the project
        (default is CWD, if not provided)

    Attributes
    ----------
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    session_id : str
        id of session associated with task
    command : str
        command that is used by the task
    status : str or None
        status of the current task
    start_time : datetime.datetime or None
        timestamp for the beginning time of the task
    end_time : datetime.datetime or None
        timestamp for the end time of the task
    duration : datetime.timedelta or None
        delta between start and end times
    logs : str or None
        string output of logs
    results : dict or None
        dictionary containing output results from the task

    Methods
    -------
    files(mode="r")
        Returns a list of file objects for the task

    Raises
    ------
    InvalidArgumentType
    """

    def __init__(self, task_entity, home=None):
        if not home:
            home = os.getcwd()

        if not isinstance(task_entity, CoreTask):
            raise InvalidArgumentType()

        self._core_task = task_entity
        self._home = home

        self.id = self._core_task.id
        self.model_id = self._core_task.model_id
        self.session_id = self._core_task.session_id

        # Execution definition
        self.command = self._core_task.command

        # Run parameters
        self.status = self._core_task.status
        self.start_time = self._core_task.start_time
        self.end_time = self._core_task.end_time
        self.duration = self._core_task.duration
        self.logs = self._core_task.logs
        self.results = self._core_task.results

    def files(self, mode="r"):
        """Returns a list of file objects for the task

        Parameters
        ----------
        mode : str
            file object mode
            (default is "r" which signifies read mode)

        Returns
        -------
        list
            list of file objects associated with the task
        """
        task_controller = TaskController(home=self._home)
        return task_controller.get_files(self.id, mode=mode)

    def __eq__(self, other):
        return self.id == other.id if other else False


def run(command, env=None, home=None):
    """Run the code or script inside

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    command : str or list
        the command to be run in environment. this can be either a string or list
    env : str, optional
        the location for the environment definition path
        (default is None, which will defer to the environment to find a default environment,
        or will fail if not found)
    home : str, optional
        absolute home path of the project
        (default is None, which will use the CWD as the project path)

    Returns
    -------
    Task
        returns a Task entity as defined above

    Examples
    --------
    You can use this function within a project repository to run tasks
    in the following way.

    >>> import datmo
    >>> datmo.task.run(command="python script.py")
    >>> datmo.task.run(command="python script.py", env='Dockerfile')
    """
    if not home:
        home = os.getcwd()
    task_controller = TaskController(home=home)

    # Create input dictionaries
    snapshot_dict = {}
    task_dict = {}

    if env:
        snapshot_dict["environment_definition_filepath"] = env

    if isinstance(command, list):
        task_dict["command"] = command
    else:
        if platform.system() == "Windows":
            task_dict["command"] = command
        else:
            task_dict["command"] = shlex.split(command)

    if isinstance(command, list):
        task_dict["command"] = command
    else:
        if platform.system() == "Windows":
            task_dict["command"] = command
        elif isinstance(command, basestring):
            task_dict["command"] = shlex.split(command)

    # Create the task object
    core_task_obj = task_controller.create()

    # Pass in the task
    updated_core_task_obj = task_controller.run(
        core_task_obj.id, snapshot_dict=snapshot_dict, task_dict=task_dict)

    # Create a new task object for the
    client_task_obj = Task(updated_core_task_obj, home=home)

    return client_task_obj
