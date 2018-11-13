import os
from datetime import datetime

from datmo.core.util.misc_functions import prettify_datetime, format_table


class Task():
    """Task is an entity object to represent an experiment run. A snapshot is taken before and after the task
    to capture the relevant components. These snapshots are flagged as temporary unless otherwise specified
    by the user but are stored as ids within the task object for reference.

    Note
    ----
    All attributes of the class in the ``Attributes`` section must be serializable by the DB

    Parameters
    ----------
    dictionary : dict
        id : str, optional
            the id of the entity
            (default is None; storage driver has not assigned an id yet)
        model_id : str
            the parent model id for the entity
        before_snapshot_id : str, optional
            snapshot created before the task is run
            (default is None, which means it isn't set yet)
        command : str, optional
            command that is used by the task
            (default is None, which means it isn't set yet)
        command_list : list or None
            command that is used by the task in list form (same as above)
            (default is None, which means it isn't set yet)
        data_file_path_map: list
            list of tuple, mapping the source absolute file path to destination relative file path
        data_directory_path_map: list
            list of tuple, mapping the source absolute directory path to destination relative directory path
        interactive : bool, optional
            boolean to signify if task should be run in interactive mode
            (default is False, which means no interactive mode unless specified)
        detach : bool, optional
            boolean to signify if task should be run in detach mode
            (default is False, which means output will not be shown in stdout)
        ports : list, optional
            list of string mappings from host system (left) to environment (right)
            (e.g. ["9999:9999", "8888:8888"])
            (default is None, which means it isn't set yet)
        mem_limit : string, optional
            maximum amount of memory the environment can use
            (these options take a positive integer, followed by a suffix of b, k, m, g, to indicate bytes, kilobytes,
            megabytes, or gigabytes. memory limit is contrained by total memory of the VM in which docker runs)
        task_dirpath : str, optional
            task directory path relative to the project root
            (default is None, which means it isn't set yet)
        log_filepath : str, optional
            log filepath relative to the project root
            (default is None, which means it isn't set yet)
        start_time : datetime.datetime, optional
            timestamp for the beginning time of the task
            (default is None, which means it isn't set yet)
        after_snapshot_id : str, optional
            snapshot created after the task is run
            (default is None, which means it isn't set yet)
        run_id : str, optional
            run id for the run (different from environment id and task id)
            (default is None, which means it isn't set yet)
        logs : str, optional
            string output of logs
            (default is None, which means it isn't set yet)
        status : str, optional
            status of the current task
            (default is None, which means it isn't set yet)
        results : dict, optional
            dictionary containing output results from the task
            (default is None, which means it isn't set yet)
        end_time : datetime.datetime, optional
            timestamp for the beginning time of the task
            (default is None, which means it isn't set yet)
        duration : float, optional
            float object signifying number of seconds for run
            (default is None, which means it isn't set yet)
        created_at : datetime.datetime, optional
            (default is datetime.utcnow(), at time of instantiation)
        updated_at : datetime.datetime, optional
            (default is same as created_at, at time of instantiation)

    Attributes
    ----------
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    before_snapshot_id : str or None
        snapshot created before the task is run
    command : str or None
        command that is used by the task
    command_list : list or None
        command that is used by the task in list form (same as above)
    interactive : bool
        boolean to signify if task should be run in interactive mode
    detach : bool
        boolean to signify if task should be run in detach mode
    gpu : bool
        boolean to signify gpu task
    ports : list or None
        list of string mappings from host system (left) to environment (right)
        (e.g. ["9999:9999", "8888:8888"])
    task_dirpath : str or None
        task directory path relative to the project root
    data_file_path_map: list
            list of tuple, mapping the source absolute file path to destination relative file path
    data_directory_path_map: list
        list of tuple, mapping the source absolute directory path to destination relative directory path
    log_filepath : str or None
        log filepath relative to the project root
    start_time : datetime.datetime or None
        timestamp for the beginning time of the task
    after_snapshot_id : str or None
        snapshot created after the task is run
    run_id : str or None
        run id for the run (different from environment id and task id)
    logs : str or None
        string output of logs
    status : str or None
        status of the current task
    results : dict or None
        dictionary containing output results from the task
    end_time : datetime.datetime or None
        timestamp for the beginning time of the task
    duration : float or None
        float object signifying number of seconds for run
    created_at : datetime.datetime
    updated_at : datetime.datetime
    """

    def __init__(self, dictionary):
        self.id = dictionary.get('id', None)
        self.model_id = dictionary['model_id']

        # Pre-Execution
        self.before_snapshot_id = dictionary.get('before_snapshot_id', None)
        self.command = dictionary.get('command', None)
        self.command_list = dictionary.get('command_list', None)
        self.interactive = dictionary.get('interactive', False)
        self.detach = dictionary.get('detach', False)
        self.gpu = dictionary.get('gpu', False)
        self.mem_limit = dictionary.get('mem_limit', None)
        self.workspace = dictionary.get('workspace', None)
        self.ports = dictionary.get('ports', None)
        self.task_dirpath = dictionary.get('task_dirpath', None)
        self.data_file_path_map = dictionary.get('data_file_path_map', None)
        self.data_directory_path_map = dictionary.get(
            'data_directory_path_map', None)
        self.task_dirpath = dictionary.get('task_dirpath', None)
        self.log_filepath = dictionary.get('log_filepath', None)
        self.start_time = dictionary.get('start_time', None)

        # Post-Execution
        self.after_snapshot_id = dictionary.get('after_snapshot_id', None)
        self.run_id = dictionary.get('run_id', None)
        self.logs = dictionary.get('logs', None)
        self.status = dictionary.get('status', None)
        self.results = dictionary.get('results', None)
        self.end_time = dictionary.get('end_time', None)
        self.duration = dictionary.get('duration', None)

        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        final_str = '\033[94m' + "task " + self.id + os.linesep + '\033[0m'
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
        if self.results:
            table_data.append(["Results", "-> " + str(self.results)])
        final_str = final_str + format_table(table_data)
        if self.command:
            final_str = final_str + os.linesep + "    " + self.command + os.linesep + os.linesep
        return final_str

    def __repr__(self):
        return self.__str__()

    def to_dictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = {
            attr: val
            for attr, val in attr_dict.items()
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict
