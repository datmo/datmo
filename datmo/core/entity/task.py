from datetime import datetime


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
        session_id : str
            id of session associated with task
        before_snapshot_id : str, optional
            snapshot created before the task is run
            (default is None, which means it isn't set yet)
        command : str, optional
            command that is used by the task
            (default is None, which means it isn't set yet)
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
    session_id : str
        id of session associated with task
    before_snapshot_id : str or None
        snapshot created before the task is run
    command : str or None
        command that is used by the task
    interactive : bool
        boolean to signify if task should be run in interactive mode
    detach : bool
        boolean to signify if task should be run in detach mode
    ports : list or None
        list of string mappings from host system (left) to environment (right)
        (e.g. ["9999:9999", "8888:8888"])
    task_dirpath : str or None
        task directory path relative to the project root
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
        self.session_id = dictionary['session_id']

        # Pre-Execution
        self.before_snapshot_id = dictionary.get('before_snapshot_id', None)
        self.command = dictionary.get('command', None)
        self.interactive = dictionary.get('interactive', False)
        self.detach = dictionary.get('detach', False)
        self.ports = dictionary.get('ports', None)
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

    def to_dictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = {
            attr: val
            for attr, val in attr_dict.items()
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict
