import os

from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.snapshot import Snapshot as CoreSnapshot
from datmo.core.util.exceptions import InvalidArgumentType


class Snapshot():
    """Snapshot is an entity object to enable user access to properties

    Parameters
    ----------
    snapshot_entity : datmo.core.entity.snapshot.Snapshot
        core snapshot entity to reference
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

    def __init__(self, snapshot_entity, home=None):
        if not home:
            home = os.getcwd()

        if not isinstance(snapshot_entity, CoreSnapshot):
            raise InvalidArgumentType()

        self._core_snapshot = snapshot_entity
        self._home = home

        self.id = self._core_snapshot.id
        self.model_id = self._core_snapshot.model_id
        self.session_id = self._core_snapshot.session_id
        self.message = self._core_snapshot.message

        self.code_id = self._core_snapshot.code_id
        self.environment_id = self._core_snapshot.environment_id
        self.file_collection_id = self._core_snapshot.file_collection_id
        self.config = self._core_snapshot.config
        self.stats = self._core_snapshot.stats

        self.task_id = self._core_snapshot.task_id
        self.label = self._core_snapshot.label
        self.created_at = self._core_snapshot.created_at

    def __eq__(self, other):
        return self.id == other.id if other else False


def create(message,
           label=None,
           commit_id=None,
           environment_id=None,
           filepaths=None,
           config=None,
           stats=None,
           home=None):
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
    commit_id : str, optional
        provide the exact commit hash associated with the snapshot
        (default is None, which means it automatically creates a commit)
    environment_id : str, optional
        provide the environment object id to use with this snapshot
        (default is None, which means it creates a default environment)
    filepaths : list, optional
        provides a list of absolute filepaths to files or directories
        that are relevant (default is None, which means we have an empty
    config : dict, optional
        provide the dictionary of configurations
        (default is None, which means it is empty)
    stats : dict, optional
        provide the dictionary of relevant statistics or metrics
        (default is None, which means it is empty)
    home : str, optional
        absolute home path of the project
        (default is None, which will use the CWD as the project path)

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
    >>> datmo.sdk.python.snapshot.create(message="my first snapshot", filepaths=["/path/to/a/large/file"], config={"test": 0.4, "test2": "string"}, stats={"accuracy": 0.94})
    """
    if not home:
        home = os.getcwd()
    snapshot_controller = SnapshotController(home=home)

    snapshot_create_dict = {"message": message}

    # add arguments if they are not None
    if label:
        snapshot_create_dict['label'] = label
    if commit_id:
        snapshot_create_dict['commit_id'] = commit_id
    if environment_id:
        snapshot_create_dict['environment_id'] = environment_id
    if filepaths:
        snapshot_create_dict['filepaths'] = filepaths
    if config:
        snapshot_create_dict['config'] = config
    if stats:
        snapshot_create_dict['stats'] = stats
    if label:
        snapshot_create_dict['label'] = label

    # Create a new core snapshot object
    core_snapshot_obj = snapshot_controller.create(snapshot_create_dict)

    # Create a new snapshot object
    client_snapshot_obj = Snapshot(core_snapshot_obj, home=home)

    return client_snapshot_obj


def create_from_task(message, task_id, home=None):
    """Create a snapshot within a project from a completed task

    Parameters
    ----------
    message : str
        a description of the snapshot for later reference
    task_id : str
        task object id to use to create snapshot

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
    >>> datmo.sdk.python.snapshot.create_from_task(message="my first snapshot from task", task_id="1jfkshg049")
    """
    if not home:
        home = os.getcwd()
    snapshot_controller = SnapshotController(home=home)

    # Create a new core snapshot object
    core_snapshot_obj = snapshot_controller.create_from_task(message, task_id)

    # Create a new snapshot object
    client_snapshot_obj = Snapshot(core_snapshot_obj, home=home)

    return client_snapshot_obj


def ls(session_id=None, filter=None, home=None):
    """List snapshots within a project

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    session_id : str, optional
        a description of the snapshot for later reference
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
        returns a list of Snapshot entities (as defined above)

    Examples
    --------
    You can use this function within a project repository to list snapshots.

    >>> import datmo
    >>> snapshots = datmo.sdk.python.snapshot.ls()
    """
    if not home:
        home = os.getcwd()
    snapshot_controller = SnapshotController(home=home)

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
                    (filter in core_snapshot_obj.message) \
                    or (core_snapshot_obj.label != None and filter in core_snapshot_obj.label):
                filtered_core_snapshot_objs.append(core_snapshot_obj)

    # Return Snapshot entities
    return [
        Snapshot(filtered_core_snapshot_obj, home=home)
        for filtered_core_snapshot_obj in filtered_core_snapshot_objs
    ]
