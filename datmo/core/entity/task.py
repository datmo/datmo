from datetime import datetime


class Task():
    """Task is an entity object to represent an experiment run. A snapshot is taken before and after the task
    to capture the relevant components. These snapshots are flagged as temporary unless otherwise specified
    by the user but are stored as ids within the task object for reference.

    Parameters
    ----------
    dictionary : dict
        id : str
            the id of the entity
        model_id : str
            the parent model id for the entity
        session_id : str
            id of session associated with task
        command : str
            command that is used by the task
        before_snapshot_id : str, optional
            snapshot created before the task is run
            (default is "", which means it isn't set yet)
        ports : list, optional
            list of string mappings from host system (left) to environment (right)
            (e.g. ["9999:9999", "8888:8888"])
            (default is [], which means it isn't set yet)
        gpu : bool, optional
            boolean to signify if run requires gpu
            (default is False, which means no gpu unless specified)
        interactive : bool, optional
            boolean to signify if should be run in interactive mode
            (default is False, which means no interactive mode unless specified)
        task_dirpath : str, optional
            task directory path relative to the project root
            (default is "", which means it isn't set yet)
        log_filepath : str, optional
            log filepath relative to the project root
            (default is "", which means it isn't set yet)
        start_time : datetime.datetime
            timestamp for the beginning time of the task
            (default is None, which means it isn't set yet)
        after_snapshot_id : str, optional
            snapshot created after the task is run
            (default is "", which means it isn't set yet)
        run_id : str, optional
            run id for the run (different from environment id and task id)
            (default is "", which means it isn't set yet)
        logs : str, optional
            string output of logs
            (default is "", which means it isn't set yet)
        status : str, optional
            status of the current task
            (default is "", which means it isn't set yet)
        results : dict, optional
            dictionary containing output results from the task
            (default is {}, which means it isn't set yet)
        end_time : datetime.datetime, optional
            timestamp for the beginning time of the task
            (default is None, which means it isn't set yet)
        duration : datetime.timedelta, optional
            timedelta object signifying the time taken to run
            (default is None, which means it isn't set yet)
        created_at : datetime, optional
            (default is datetime.utcnow(), at time of instantiation)
        updated_at : datetime, optional
            (default is same as created_at, at time of instantiation)

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
    before_snapshot_id : str
        snapshot created before the task is run
    ports : list
        list of string mappings from host system (left) to environment (right)
        (e.g. ["9999:9999", "8888:8888"])
    gpu : bool
        boolean to signify if run requires gpu
    interactive : bool
        boolean to signify if should be run in interactive mode
    task_dirpath : str
        task directory path relative to the project root
    log_filepath : str
        log filepath relative to the project root
        (default is None, which means it isn't set yet)
    start_time : datetime.datetime
        timestamp for the beginning time of the task
    after_snapshot_id : str
        snapshot created after the task is run
    run_id : str
        run id for the run (different from environment id and task id)
    logs : str
        string output of logs
    status : str
        status of the current task
    results : dict
        dictionary containing output results from the task
    end_time : datetime.datetime
        timestamp for the beginning time of the task
    duration : datetime.timedelta
        timedelta object signifying the time taken to run
    created_at : datetime
    updated_at : datetime
    """
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.model_id = dictionary['model_id']
        self.session_id = dictionary['session_id']

        # Execution definition
        self.command = dictionary['command']

        # Pre-Execution
        self.before_snapshot_id = dictionary.get('before_snapshot_id', "")
        self.ports = dictionary.get('ports', [])
        self.gpu = dictionary.get('gpu', False)
        self.interactive = dictionary.get('interactive', False)
        self.task_dirpath = dictionary.get('task_dirpath', "")
        self.log_filepath = dictionary.get('log_filepath', "")
        self.start_time = dictionary.get('start_time', None)

        # Post-Execution
        self.after_snapshot_id = dictionary.get('after_snapshot_id', "")
        self.run_id = dictionary.get('run_id', "")
        self.logs = dictionary.get('logs', "")
        self.status = dictionary.get('status', "")
        self.results = dictionary.get('results', {})
        self.end_time = dictionary.get('end_time', None)
        self.duration = dictionary.get('duration', None)

        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def to_dictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = { attr: val
                    for attr, val in attr_dict.items() if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict