import os

from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.snapshot import Snapshot as CoreSnapshot
from datmo.core.util.exceptions import InvalidArgumentType, \
    SnapshotCreateFromTaskArgs
from datmo.core.util.misc_functions import prettify_datetime, format_table


class Snapshot():
    """Snapshot is an entity object to enable user access to properties

    Parameters
    ----------
    snapshot_entity : datmo.core.entity.snapshot.Snapshot
        core snapshot entity to reference

    Attributes
    ----------
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    session_id : str
        id of session associated with task
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    session_id : str
        session id within which snapshot is created
    message : str
        long description of snapshot
    code_id : str
        code reference associated with the snapshot
    environment_id : str
        id for environment used to create snapshot
    file_collection_id : str
        file collection associated with the snapshot
    config : dict
        key, value pairs of configurations
    stats : dict
        key, value pairs of metrics and statistics
    task_id : str
        task id associated with snapshot
    label : str
        short description of snapshot
    created_at : datetime.datetime

    Raises
    ------
    InvalidArgumentType
    """

    def __init__(self, snapshot_entity):
        if not isinstance(snapshot_entity, CoreSnapshot):
            raise InvalidArgumentType()

        self._core_snapshot = snapshot_entity

        self.id = self._core_snapshot.id
        self.model_id = self._core_snapshot.model_id
        self.session_id = self._core_snapshot.session_id
        self.message = self._core_snapshot.message

        self.code_id = self._core_snapshot.code_id
        self.environment_id = self._core_snapshot.environment_id
        self.config = self._core_snapshot.config
        self.stats = self._core_snapshot.stats
        self._files = None

        self.task_id = self._core_snapshot.task_id
        self.label = self._core_snapshot.label
        self.created_at = self._core_snapshot.created_at

    @property
    def files(self):
        self._files = self.get_files()
        return self._files

    def __get_core_snapshot(self):
        """Returns the latest core snapshot object for id

        Returns
        -------
        datmo.core.entity.snapshot.Snapshot
            core snapshot object for the snapshot
        """
        snapshot_controller = SnapshotController()
        return snapshot_controller.get(self.id)

    def get_files(self, mode="r"):
        """Returns a list of file objects for the snapshot

        Parameters
        ----------
        mode : str
            file object mode
            (default is "r" which signifies read mode)

        Returns
        -------
        list
            list of file objects associated with the snapshot
        """
        snapshot_controller = SnapshotController()
        return snapshot_controller.get_files(self.id, mode=mode)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        if self.label:
            final_str = '\033[94m' + "snapshot " + self.id + '\033[0m'
            final_str = final_str + '\033[94m' + " (" + '\033[0m'
            final_str = final_str + '\033[93m' + '\033[1m' + "label: " + self.label + '\033[0m'
            final_str = final_str + '\033[94m' + ")" + '\033[0m' + os.linesep
        else:
            final_str = '\033[94m' + "snapshot " + self.id + '\033[0m' + os.linesep
        final_str = final_str + "Date: " + prettify_datetime(
            self.created_at) + os.linesep
        table_data = []
        if self.session_id:
            table_data.append(["Session", "-> " + self.session_id])
        if self.task_id:
            table_data.append(["Task", "-> " + self.task_id])
        # Components
        table_data.append(["Code", "-> " + self.code_id])
        table_data.append(["Environment", "-> " + self.environment_id])
        if not self.files:
            table_data.append(["Files", "-> None"])
        else:
            table_data.append(["Files", "-> " + self.files[0].name])
            if len(list(self.files)) > 1:
                for f in self.files[1:]:
                    table_data.append(["     ", "-> " + f.name])
        table_data.append(["Config", "-> " + str(self.config)])
        table_data.append(["Stats", "-> " + str(self.stats)])
        final_str = final_str + format_table(table_data)
        final_str = final_str + os.linesep + "    " + self.message + os.linesep + os.linesep
        return final_str

    def __repr__(self):
        return self.__str__()


def create(message,
           label=None,
           run_id=None,
           environment_id=None,
           env=None,
           paths=None,
           config=None,
           stats=None):
    """Create a snapshot within a project

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------

    message : str
        a description of the snapshot for later reference
    label : str, optional
        a short description of the snapshot for later reference
        (default is None, which means a blank label is stored)
    run_id : str, optional
        run object id to use to create snapshot
        if run id is passed then subsequent parameters would be ignored.
        when using run id, it will overwrite the following inputs

        *environment_id*: used to run the task,

        *paths*: this is the set of all files saved during the task

        *config*: nothing is passed into this variable. the user may add
        something to the config by passing in a dict for the config

        *stats*:  the task.results are added into the stats variable of the
        snapshot.

    environment_id : str, optional
        provide the environment object id to use with this snapshot
        (default is None, which means it creates a default environment)
    env : str or list, optional
        the absolute file path for the environment definition path. env is not used if environment_id is also passed.
        this can be either a string or list
        (default is None, environment_id is also not passed, which will defer to the environment to find a
        default environment or will fail if not found)
    paths : list, optional
        list of absolute or relative filepaths and/or dirpaths to collect with destination names
        (e.g. "/path/to/file>hello", "/path/to/file2", "/path/to/dir>newdir")
    config : dict, optional
        provide the dictionary of configurations
        (default is None, which means it is empty)
    stats : dict, optional
        provide the dictionary of relevant statistics or metrics
        (default is None, which means it is empty)

    Returns
    -------
    Snapshot
        returns a Snapshot entity as defined above

    Examples
    --------
    You can use this function within a project repository to save snapshots
    for later use. Once you have created this, you will be able to view the
    snapshot with the `datmo snapshot ls` cli command

    >>> import datmo
    >>> datmo.snapshot.create(message="my first snapshot", paths=["/path/to/a/large/file"], config={"test": 0.4, "test2": "string"}, stats={"accuracy": 0.94})

    You can also use the result of a task run in order to create a snapshot

    >>> datmo.snapshot.create(message="my first snapshot from task", task_id="1jfkshg049")
    """

    snapshot_controller = SnapshotController()

    if run_id is not None:
        excluded_args = ["environment_id", "paths"]
        for arg in excluded_args:
            if eval(arg) is not None:
                raise SnapshotCreateFromTaskArgs(
                    "error", "sdk.snapshot.create.run.args", arg)

        # Create a new core snapshot object
        core_snapshot_obj = snapshot_controller.create_from_task(
            message, run_id, label=label, config=config, stats=stats)

        # Create a new snapshot object
        client_snapshot_obj = Snapshot(core_snapshot_obj)

        return client_snapshot_obj
    else:
        snapshot_create_dict = {"message": message}

        # add arguments if they are not None
        if label:
            snapshot_create_dict['label'] = label
        if environment_id:
            snapshot_create_dict['environment_id'] = environment_id
        elif isinstance(env, list):
            snapshot_create_dict['environment_paths'] = env
        elif env:
            snapshot_create_dict['environment_paths'] = [env]
        if paths:
            snapshot_create_dict['paths'] = paths
        if config:
            snapshot_create_dict['config'] = config
        if stats:
            snapshot_create_dict['stats'] = stats
        if label:
            snapshot_create_dict['label'] = label

        # Create a new core snapshot object
        core_snapshot_obj = snapshot_controller.create(snapshot_create_dict)
        core_snapshot_obj = snapshot_controller.update(
            core_snapshot_obj.id, visible=True)

        # Create a new snapshot object
        client_snapshot_obj = Snapshot(core_snapshot_obj)

        return client_snapshot_obj


def ls(session_id=None, filter=None):
    """List snapshots within a project

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    session_id : str, optional
        session id to filter output snapshots
        (default is None, which means no session filter is given)
    filter : str, optional
        a string to use to filter from message and label
        (default is to give all snapshots, unless provided a specific string. eg: best)

    Returns
    -------
    list
        returns a list of Snapshot entities (as defined above)

    Examples
    --------
    You can use this function within a project repository to list snapshots.

    >>> import datmo
    >>> snapshots = datmo.snapshot.ls()
    """

    snapshot_controller = SnapshotController()

    # add arguments if they are not None
    if not session_id:
        session_id = snapshot_controller.current_session.id

    core_snapshot_objs = snapshot_controller.list(
        session_id,
        visible=True,
        sort_key='created_at',
        sort_order='descending')

    # Filtering Snapshots
    # TODO: move to list function in SnapshotController
    # Add in preliminary snapshots if no filter
    filtered_core_snapshot_objs = [
        core_snapshot_obj for core_snapshot_obj in core_snapshot_objs
        if core_snapshot_obj.visible and not filter
    ]
    # If filter is present then use it and only add those that pass filter
    for core_snapshot_obj in core_snapshot_objs:
        if core_snapshot_obj.visible:
            if filter and \
                ((filter in core_snapshot_obj.message) \
                    or (core_snapshot_obj.label != None and filter in core_snapshot_obj.label)):
                filtered_core_snapshot_objs.append(core_snapshot_obj)

    # Return Snapshot entities
    return [
        Snapshot(filtered_core_snapshot_obj)
        for filtered_core_snapshot_obj in filtered_core_snapshot_objs
    ]


def update(snapshot_id=None, config=None, stats=None, message=None,
           label=None):
    """Update a snapshot within a project

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    snapshot_id : str
        snapshot id to be updated
    config : dict, optional
        provide the dictionary of configurations to update
        (default is None, which means it is not being updated)
    stats : dict, optional
        provide the dictionary of relevant statistics or metrics to update
        (default is None, which means it is not being updated)
    message : str, optional
        a string to use as a new message for the snapshot
        (default is the already given message to that snapshot, unless provided a specific string.)
    label : str, optional
        a string to use as a new label for the snapshot
        (default is the already given label to that snapshot, unless provided a specific string.)

    Returns
    -------
    snapshot entity
        returns a Snapshot entity

    Examples
    --------
    You can use this function within a project repository to update a snapshot.

    >>> import datmo
    >>> snapshots = datmo.snapshot.update(snapshot_id="4L24adFfsa", config={"depth": "10", "learning_rate": "0.91"},
    ...          stats={"acc": "91.34", "f1_score": "0.91"}, message="new message", label="best")
    """
    snapshot_controller = SnapshotController()

    return snapshot_controller.update(
        snapshot_id=snapshot_id,
        config=config,
        stats=stats,
        message=message,
        label=label)


def delete(snapshot_id=None):
    """Delete a snapshot within a project

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    snapshot_id : str
        snapshot id to be updated

    Returns
    -------
    snapshot entity
        returns a Snapshot entity

    Examples
    --------
    You can use this function within a project repository to delete a snapshot.

    >>> import datmo
    >>> datmo.snapshot.delete(snapshot_id="4L24adFfsa")
    """
    snapshot_controller = SnapshotController()

    snapshot_controller.delete(snapshot_id=snapshot_id)
