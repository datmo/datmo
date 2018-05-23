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
from datmo.core.util.misc_functions import prettify_datetime, format_table


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
    duration : float or None
        delta in seconds between start and end times
    logs : str or None
        string output of logs
    results : dict or None
        dictionary containing output results from the task
    files : list
        returns list of file objects for the task in read mode

    Methods
    -------
    get_files(mode="r")
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
        self._status = self._core_task.status
        self._start_time = self._core_task.start_time
        self._end_time = self._core_task.end_time
        self._duration = self._core_task.duration

        # Outputs
        self._logs = self._core_task.logs
        self._results = self._core_task.results
        self._files = None

    @property
    def status(self):
        self._core_task = self.__get_core_task()
        self._status = self._core_task.status
        return self._status

    @property
    def start_time(self):
        self._core_task = self.__get_core_task()
        self._start_time = self._core_task.start_time
        return self._start_time

    @property
    def end_time(self):
        self._core_task = self.__get_core_task()
        self._end_time = self._core_task.end_time
        return self._end_time

    @property
    def duration(self):
        self._core_task = self.__get_core_task()
        self._duration = self._core_task.duration
        return self._duration

    @property
    def logs(self):
        self._core_task = self.__get_core_task()
        self._logs = self._core_task.logs
        return self._logs

    @property
    def results(self):
        self._core_task = self.__get_core_task()
        self._results = self._core_task.results
        return self._results

    @property
    def files(self):
        self._files = self.get_files()
        return self._files

    def __get_core_task(self):
        """Returns the latest core task object for id

        Returns
        -------
        datmo.core.entity.task.Task
            core task object fo the task
        """
        task_controller = TaskController(home=self._home)
        return task_controller.get(self.id)

    def get_files(self, mode="r"):
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

    def __str__(self):
        final_str = '\033[94m' + "task " + self.id + "\n" + '\033[0m'
        table_data = []
        if self.session_id:
            table_data.append(["Session", "-> " + self.session_id])
        if self.status:
            table_data.append(["Status", "-> " + self.status])
        if self.start_time:
            table_data.append(
                ["Start Time", "-> " + prettify_datetime(self.start_time)])
        if self.end_time:
            table_data.append(
                ["End Time", "-> " + prettify_datetime(self.end_time)])
        if self.duration:
            table_data.append(
                ["Duration", "-> " + str(self.duration) + " seconds"])
        # Outputs
        if self.logs:
            table_data.append(
                ["Logs", "-> Use task log to view or download logs"])
        if self.results:
            table_data.append(["Results", "-> " + str(self.results)])
        if not self.files:
            table_data.append(["Files", "-> None"])
        else:
            table_data.append(["Files", "-> " + self.files[0].name])
            if len(list(self.files)) > 1:
                for f in self.files[1:]:
                    table_data.append(["     ", "-> " + f.name])
        final_str = final_str + format_table(table_data)
        final_str = final_str + "\n" + "    " + self.command + "\n" + "\n"
        return final_str

    def __repr__(self):
        return self.__str__()


def run(command, env=None, home=None, gpu=False):
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
    gpu: boolean
        try to run task on GPU (if available)

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
        task_dict["command_list"] = command
    else:
        if platform.system() == "Windows":
            task_dict["command"] = command
        elif isinstance(command, basestring):
            task_dict["command_list"] = shlex.split(command)

    task_dict["gpu"] = gpu

    # Create the task object
    core_task_obj = task_controller.create()

    # Pass in the task
    updated_core_task_obj = task_controller.run(
        core_task_obj.id, snapshot_dict=snapshot_dict, task_dict=task_dict)

    # Create a new task object for the
    client_task_obj = Task(updated_core_task_obj, home=home)

    return client_task_obj


def ls(session_id=None, filter=None, home=None):
    """List tasks within a project

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    session_id : str, optional
        session to filter output tasks
        (default is None, which means no session filter is given)
    filter : str, optional
        a string to use to filter from message and label
        (default is to give all snapshots, unless provided a specific string. eg: best)
    home : str, optional
        absolute home path of the project
        (default is None, which will use the CWD as the project path)

    Returns
    -------
    list
        returns a list of Task entities (as defined above)

    Examples
    --------
    You can use this function within a project repository to list tasks.

    >>> import datmo
    >>> tasks = datmo.task.ls()
    """
    if not home:
        home = os.getcwd()
    task_controller = TaskController(home=home)

    # add arguments if they are not None
    if not session_id:
        session_id = task_controller.current_session.id

    core_task_objs = task_controller.list(
        session_id, sort_key='created_at', sort_order='descending')

    # Filtering Tasks
    # TODO: move to list function in TaskController
    # Add in preliminary tasks if no filter
    filtered_core_task_objs = [
        core_task_obj for core_task_obj in core_task_objs if not filter
    ]
    # If filter is present then use it and only add those that pass filter
    for core_task_obj in core_task_objs:
        if filter and \
            (filter in core_task_obj.command):
            filtered_core_task_objs.append(core_task_obj)

    # Return Task entities
    return [
        Task(filtered_core_task_obj, home=home)
        for filtered_core_task_obj in filtered_core_task_objs
    ]
