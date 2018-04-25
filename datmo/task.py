import os
import shlex

from datmo.core.controller.task import TaskController
from datetime import datetime


class ClientTask():
    """ClientTask is an entity object to represent an experiment run as output while using the client

    Initialize with task object returned from controller task run

    Attributes
    ----------
    id : str
        the id of the entity
    command : str
    files : list
        list of file absolute paths created during the task
    logs : str
        absolute path for the logs for the experiment
    result : dict
        dictionary containing output results from the experiment
    status : str, optional
    created_at : datetime, optional
    updated_at : datetime, optional

    """
    def __init__(self, task_entity, home=None):
        if hasattr(task_entity,'to_dictionary'):
            dictionary = task_entity.to_dictionary()
        else:
            dictionary = task_entity

        self.id = dictionary['id']

        # Execution definition
        self.command = dictionary['command']

        # Post-Execution
        self.logs = dictionary.get('logs', "")
        task_path = dictionary.get('task_dirpath', "")

        if task_path:
            task_path = os.path.join(home, task_path)
            self.files = [f for f in os.listdir(task_path)
                          if (os.path.isfile(os.path.join(task_path, f))
                                             and f != 'task.log')]
        else:
            self.files = []
        self.result = dictionary.get('result', {})
        self.status = dictionary.get('status', "")

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


def run(command, env=None, home=None):
    """
    Run the code or script inside

    The project must be created before this is implemented. You can do that by using
    the following command::

        $ datmo init


    Parameters
    ----------
    command : str
        the command to be run in environment
    env : str, optional
        the location for the environment definition path
        (default is None, which means a blank label is stored)
    home : str, optional
        absolute home path of the project
        (default is None, which will use the CWD as the project path)

    Returns
    -------
    Snapshot
        returns a snapshot entity for reference

    Examples
    --------
    You can use this function within a project repository to save snapshots
    for later use. Once you have created this, you will be able to view the
    snapshot with the `datmo snapshot ls` cli command

    >>> import datmo
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

    if type(command) is list:
        task_dict["command"] = command
    else:
        task_dict["command"] = shlex.split(command)

    # Create the task object
    task_obj = task_controller.create(task_dict)

    # Pass in the task
    updated_task_obj = task_controller.run(task_obj.id, snapshot_dict=snapshot_dict)

    # Create a new task object for the
    sdk_task_obj = ClientTask(updated_task_obj, home)

    return sdk_task_obj