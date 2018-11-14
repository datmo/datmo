import os

from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.task import Task as CoreTask
from datmo.core.util.exceptions import InvalidArgumentType
from datmo.core.util.misc_functions import printable_object, prettify_datetime, format_table


class Run():
    """Run is an object to enable user access to properties

    Parameters
    ----------
    task_entity : datmo.core.entity.task.Task
        core task entity to reference

    Attributes
    ----------
    id : str
        the id of task associated with run
    model_id : str
        the parent model id for the entity
    before_snapshot_id : str
        id of snapshot associated before the run
    after_snapshot_id : str
        id of snapshot associated after the run
    command : str
        command that is used by the run
    type : str
        type of task, script or workspace (jupyterlab, notebook, rstudio, terminal)
    status : str or None
        status of the current run
    start_time : datetime.datetime or None
        timestamp for the beginning time of the run
    end_time : datetime.datetime or None
        timestamp for the end time of the run
    duration : float or None
        delta in seconds between start and end times
    logs : str or None
        string output of logs
    config : dict
        dictionary containing input or output configs from the run
    results : dict
        dictionary containing output results from the run
    files : list
        returns list of file objects for the run in read mode

    Methods
    -------
    get_files(mode="r")
        Returns a list of file objects for the run

    Raises
    ------
    InvalidArgumentType
    """

    def __init__(self, task_entity):
        if not isinstance(task_entity, CoreTask):
            raise InvalidArgumentType()

        self._core_task = task_entity

        self.id = self._core_task.id
        self.model_id = self._core_task.model_id
        self.created_at = self._core_task.created_at
        self.before_snapshot_id = task_entity.before_snapshot_id
        self.after_snapshot_id = task_entity.after_snapshot_id

        # Execution definition
        self.command = self._core_task.command
        self._type = None
        self._core_snapshot_id = None
        self._environment_id = None
        self._config = {}

        # Run parameters
        self._status = self._core_task.status
        self._start_time = self._core_task.start_time
        self._end_time = self._core_task.end_time
        self._duration = self._core_task.duration

        # Outputs
        self._logs = self._core_task.logs
        self._results = {}
        self._files = None

    @property
    def status(self):
        self._core_task = self.__get_core_task()
        self._status = self._core_task.status
        return self._status

    @property
    def type(self):
        self._type = self._core_task.workspace\
            if self._core_task.workspace else 'script'
        return self._type

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
    def config(self):
        self._core_snapshot = self.__get_core_snapshot()
        self._config = self._core_snapshot.config if self._core_snapshot else {}
        return self._config

    @property
    def results(self):
        self._core_task = self.__get_core_task()
        self._results = {}
        if self._core_task.results is not None:
            self._results = self._core_task.results
        else:
            self._core_snapshot = self.__get_core_snapshot()
            self._results = self._core_snapshot.stats if self._core_snapshot else {}
        return self._results

    @property
    def core_task(self):
        return self._core_task

    @property
    def core_snapshot_id(self):
        self._core_snapshot_id = self.get_core_snapshot_id()
        return self._core_snapshot_id

    @property
    def environment_id(self):
        self._environment_id = self.get_environment_id()
        return self._environment_id

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
        return self._core_task

    def __get_core_snapshot(self):
        """Returns the latest core snapshot object for id

        Returns
        -------
        datmo.core.entity.snapshot.Snapshot or None
            core snapshot object for the Snapshot
        """
        snapshot_controller = SnapshotController()
        snapshot_id = self.after_snapshot_id if self.after_snapshot_id else self.before_snapshot_id
        snapshot_obj = snapshot_controller.get(
            snapshot_id) if snapshot_id else None
        return snapshot_obj

    def get_environment_id(self):
        """Returns the environment id for the run

        Returns
        -------
        str or None
            string for environment id associated with the task
        """
        self._core_snapshot = self.__get_core_snapshot()
        return self._core_snapshot.environment_id if self._core_snapshot else None

    def get_core_snapshot_id(self):
        """Returns the core snapshot id for the run

        Returns
        -------
        str or None
            string for core snapshot id associated with the task
        """
        self._core_snapshot = self.__get_core_snapshot()
        return self._core_snapshot.id if self._core_snapshot else None

    def get_files(self, mode="r"):
        """Returns a list of file objects for the task

        Parameters
        ----------
        mode : str
            file object mode
            (default is "r" which signifies read mode)

        Returns
        -------
        list or None
            list of file objects associated with the task
        """
        snapshot_controller = SnapshotController()
        self._core_snapshot = self.__get_core_snapshot()
        return snapshot_controller.get_files(
            self._core_snapshot.id, mode=mode) if self._core_snapshot else None

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        final_str = '\033[94m' + "run " + self.id + os.linesep + '\033[0m'
        table_data = []
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
        if self.config:
            table_data.append(["Config", "-> " + str(self.config)])
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
        final_str = final_str + os.linesep + "    " + self.command + os.linesep + os.linesep
        return final_str

    def __repr__(self):
        return self.__str__()
