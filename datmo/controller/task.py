import os

from datmo.util.i18n import get as __
from datmo.controller.base import BaseController
from datmo.controller.environment.environment import EnvironmentController
from datmo.controller.snapshot import SnapshotController
from datmo.util.exceptions import TaskRunException, RequiredArgumentMissing


class TaskController(BaseController):
    """TaskController inherits from BaseController and manages business logic associated with tasks
    within the project.

    Attributes
    ----------
    environment : EnvironmentController
        used to create environment if new definition file
    snapshot : SnapshotController
        used to create snapshots before and after tasks

    Methods
    -------
    create(dictionary)
        creates a Task object with the permanent parameters
    _run_helper(environment_id, log_filepath, options)
        helper for run to start environment and run with the appropriate parameters
    run(self, task_id, dictionary=None)
        runs the task and tracks the run, logs, inputs and outputs
    list(session_id=None)
        lists all tasks within the project given filters
    delete(id)
        deletes the specified task from the project

    """
    def __init__(self, home, dal_driver=None):
        super(TaskController, self).__init__(home, dal_driver)
        self.environment = EnvironmentController(home, self.dal.driver)
        self.snapshot = SnapshotController(home, self.dal.driver)

    def create(self, dictionary):
        """Create Task object

        Parameters
        ----------
        dictionary : dict
            command : str
                full command used

        Returns
        -------
        Task
            object entity for Task
        """

        # Validate Inputs

        create_dict = {
            "model_id": self.model.id,
            "session_id": self.current_session.id
        }

        ## Required args
        required_args = ["command"]
        for required_arg in required_args:
            # Add in any values that are
            if required_arg in dictionary and dictionary[required_arg] is not None:
                create_dict[required_arg] = dictionary[required_arg]
            else:
                raise RequiredArgumentMissing(__("error",
                                                "controller.task.create.arg",
                                                required_arg))

        # Create Task
        return self.dal.task.create(create_dict)

    def _run_helper(self, environment_id,
                    options, log_filepath):
        """Run environment with parameters

        Parameters
        ----------
        environment_id : str
            the environment id for definition
        options : dict
            can include the following values:

            command : list
            ports : list
                Here are some example ports used for common applications.
                   *  'jupyter notebook' - 8888
                   *  flask API - 5000
                   *  tensorboard - 6006
                An example input for the above would be ["8888:8888", "5000:5000", "6006:6006"]
                which maps the running host port (right) to that of the environment (left)
            name : str
            volumes : dict
            detach : bool
            stdin_open : bool
            tty : bool
            gpu : bool
        log_filepath : str
            absolute filepath to the log file

        Returns
        -------
        return_code : int
            system return code of the environment that was run
        container_id : str
            id of the container environment that was run
        logs : str
            output logs from the run
        """
        # Run container with options provided
        run_options = {
            "command": options.get('command', None),
            "ports": options.get('ports', None),
            "name": options.get('name', None),
            "volumes": options.get('volumes', None),
            "detach": options.get('detach', False),
            "stdin_open": options.get('stdin_open', False),
            "tty": options.get('tty', False),
            "gpu": options.get('gpu', False),
            "api": False
        }

        # Build image for environment
        self.environment.build(environment_id)

        # Run container with environment
        return_code, container_id, logs = \
            self.environment.run(environment_id, run_options, log_filepath)

        return return_code, container_id, logs

    def run(self, task_id, snapshot_dict={"visible": False}, task_dict={}):
        """Run a task with parameters. If dictionary specified, create a new task with new run parameters.
        Snapshot objects are created before and after the task to keep track of the state. During the run,
        you can access task outputs using environment variable DATMO_TASK_DIR or `/task` which points to
        location of datmo_tasks/[task-id]. Create config.json, stats.json and any weights or any file such
        as graphs and visualizations within that directory for quick access

        Parameters
        ----------
        task_id : str
            id for the task you would like to run
        snapshot_dict : dict
            set of parameters to create a snapshot (see SnapshotController for details.
            default is dictionary with `visible` False to hide auto-generated snapshot)
        task_dict : dict
            set of parameters to characterize the task run (default is empty dictionary,
            see datmo.entity.task for more details on inputs)

        Returns
        -------
        Task
            the Task object which completed its run with updated parameters

        Raises
        ------
        TaskRunException
            If there is any error in creating files for the task or downstream errors
        """
        # Obtain Task to run
        task_obj = self.dal.task.get_by_id(task_id)

        # Create Task directory for user during run
        task_dirpath = os.path.join("datmo_tasks",
                                    task_obj.id)
        try:
            _ = self.file_driver.create(
                os.path.join("datmo_tasks",
                             task_obj.id), dir=True)
        except:
            raise TaskRunException(__("error",
                                     "controller.task.run",
                                     task_dirpath))

        # Create the before snapshot prior to execution
        before_snapshot_obj = self.snapshot.create(snapshot_dict)

        # Update the task with pre-execution parameters
        task_obj = self.dal.task.update({
            "id": task_obj.id,
            "before_snapshot_id": task_dict.get('before_snapshot_id',
                                                 before_snapshot_obj.id),
            "ports": task_dict.get('ports', task_obj.ports),
            "gpu": task_dict.get('gpu', task_obj.gpu),
            "interactive": task_dict.get('interactive', task_obj.interactive),
            "task_dirpath": task_dict.get('task_dirpath', task_dirpath),
            "log_filepath": task_dict.get('log_filepath', os.path.join(task_dirpath, "task.log"))
        })

        # Copy over files from the before_snapshot file collection to task dir
        file_collection_obj =  \
            self.dal.file_collection.get_by_id(before_snapshot_obj.file_collection_id)
        self.file_driver.copytree(os.path.join(self.home, file_collection_obj.path),
            os.path.join(self.home, task_obj.task_dirpath)
        )

        # Set the parameters set in the task
        environment_run_options = {
            "command": task_obj.command,
            "ports": task_obj.ports,
            "gpu": task_obj.gpu,
            "name": "datmo-task-" + task_obj.id,
            "volumes": {
                os.path.join(self.home, task_obj.task_dirpath): {
                    'bind': '/task/',
                    'mode': 'rw'
                },
                self.home: {
                    'bind': '/home/',
                    'mode': 'rw'
                }
            },
            "detach": task_obj.interactive,
            "stdin_open": task_obj.interactive,
            "tty": False,
            "api": not task_obj.interactive
        }

        # Run environment via the helper function
        return_code, container_id, logs =  \
            self._run_helper(before_snapshot_obj.environment_id,
                             environment_run_options,
                             os.path.join(self.home, task_obj.log_filepath))

        # Create the after snapshot after execution is completed with new filepaths
        after_snapshot_dict = snapshot_dict.copy()
        after_snapshot_dict.update({
            "filepaths": [os.path.join(self.home, task_obj.task_dirpath)],
            "environment_id": before_snapshot_obj.environment_id,
        })
        after_snapshot_obj = self.snapshot.create(after_snapshot_dict)

        # (optional) Remove temporary task directory path

        # Update the task with post-execution parameters
        return self.dal.task.update({
            "id": task_obj.id,
            "after_snapshot_id": after_snapshot_obj.id,
            "container_id": container_id,
            "logs": logs,
            "status": "SUCCESS" if return_code==0 else "FAILED",
        })

    def list(self, session_id=None):
        query = {}
        if session_id:
            query['session_id'] = session_id
        return self.dal.task.query(query)

    def delete(self, id):
        if not id:
            raise RequiredArgumentMissing(__("error",
                                            "controller.task.delete.arg",
                                            "id"))
        return self.dal.task.delete(id)