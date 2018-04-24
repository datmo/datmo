import os

from datmo.core.controller.snapshot import SnapshotController


def create(message, label=None, commit_id=None, environment_id=None, filepaths=None,
           config=None, stats=None, home=None):
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
        returns a snapshot entity (as defined in datmo.core.entity.snapshot)

    Examples
    --------
    You can use this function within a project repository to save snapshots
    for later use. Once you have created this, you will be able to view the
    snapshot with the `datmo snapshot ls` cli command

    >>> import datmo
    >>> datmo.snapshot.create(message="my first snapshot", filepaths=["/path/to/a/large/file"], config={"test": 0.4, "test2": "string"}, stats={"accuracy": 0.94})
    """
    if not home:
        home = os.getcwd()
    snapshot_controller = SnapshotController(home=home)

    snapshot_create_dict = {
        "message": message
    }

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

    return snapshot_controller.create(snapshot_create_dict)

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
        returns a list of Snapshot entities (as defined in datmo.core.entity.snapshot)

    Examples
    --------
    You can use this function within a project repository to list snapshots.

    >>> import datmo
    >>> snapshots = datmo.snapshot.ls()
    """
    if not home:
        home = os.getcwd()
    snapshot_controller = SnapshotController(home=home)

    # add arguments if they are not None
    if not session_id:
        session_id = snapshot_controller.current_session.id

    snapshot_objs = snapshot_controller.list(session_id)

    # Filtering Snapshots
    # TODO: move to list function in SnapshotController
    # Add in preliminary snapshots if no filter
    filtered_snapshot_objs = [snapshot_obj for snapshot_obj in snapshot_objs
                              if snapshot_obj.visible and not filter]
    # If filter is present then use it and only add those that pass filter
    for snapshot_obj in snapshot_objs:
        if snapshot_obj.visible:
            if filter and (filter in snapshot_obj.message
                             or filter in snapshot_obj.label):
                filtered_snapshot_objs.append(snapshot_obj)

    # Return Snapshot entities
    return filtered_snapshot_objs