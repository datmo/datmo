import os
from datetime import datetime

from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.task import Task
from datmo.core.util.exceptions import TaskRunException, RequiredArgumentMissing, \
    ProjectNotInitializedException, PathDoesNotExist


class TaskController(BaseController):
    """TaskController inherits from BaseController and manages business logic associated with tasks
    within the project.

    Parameters
    ----------
    home : str
        home path of the project

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
    run(self, id, dictionary=None)
        runs the task and tracks the run, logs, inputs and outputs
    list(session_id=None)
        lists all tasks within the project given filters
    delete(id)
        deletes the specified task from the project

    """

    def __init__(self, home):
        super(TaskController, self).__init__(home)
        self.environment = EnvironmentController(home)
        self.snapshot = SnapshotController(home)
        if not self.is_initialized:
            raise ProjectNotInitializedException(
                __("error", "controller.task.__init__"))

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
            object entity for Task (datmo.core.entity.task.Task)
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
                raise RequiredArgumentMissing(
                    __("error", "controller.task.create.arg", required_arg))

        # Create Task
        return self.dal.task.create(Task(create_dict))

    def _run_helper(self, environment_id, options, log_filepath):
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
        run_id : str
            id of the environment run (different from environment id)
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
        return_code, run_id, logs = \
            self.environment.run(environment_id, run_options, log_filepath)

        return return_code, run_id, logs

    def _parse_logs_for_results(self, logs):
        """Parse log string to extract results and return dictionary.

        Note
        ----
        If the same key is found multiple times in the logs, the last occurring
        one will be the one that is saved.

        Parameters
        ----------
        logs : str
            raw string value of output logs

        Returns
        -------
        dict
            dictionary to represent results from task
        """
        results = {}
        for line in logs.split("\n"):
            split_line = line.split(":")
            if len(split_line) == 2:
                results[split_line[0].strip()] = split_line[1].strip()
        return results

    def run(self, task_id, snapshot_dict=None, task_dict=None):
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
            default is None, which means dictionary with `visible` False will be added to
            hide auto-generated snapshot) NOTE: `visible` False will always be False regardless
            of whether the user provides another value for `visible`.
        task_dict : dict
            set of parameters to characterize the task run
            (default is None, which translate to {}, see datmo.core.entity.task.Task for more details on inputs)

        Returns
        -------
        Task
            the Task object which completed its run with updated parameters

        Raises
        ------
        TaskRunException
            If there is any error in creating files for the task or downstream errors
        """
        # Ensure visible=False is present in the snapshot dictionary
        if not snapshot_dict:
            snapshot_dict = {"visible": False}
        else:
            snapshot_dict['visible'] = False

        if not task_dict:
            task_dict = {}

        # Obtain Task to run
        task_obj = self.dal.task.get_by_id(task_id)

        if task_obj.status == None:
            task_obj.status = 'RUNNING'
        else:
            raise TaskRunException(
                __("error", "cli.task.run.already_running", task_obj.id))

        # Create Task directory for user during run
        task_dirpath = os.path.join("datmo_tasks", task_obj.id)
        try:
            _ = self.file_driver.create(
                os.path.join("datmo_tasks", task_obj.id), directory=True)
        except:
            raise TaskRunException(
                __("error", "controller.task.run", task_dirpath))

        # Create the before snapshot prior to execution
        before_snapshot_dict = snapshot_dict.copy()
        before_snapshot_dict[
            'message'] = "autogenerated snapshot created before task %s is run" % task_obj.id
        before_snapshot_obj = self.snapshot.create(before_snapshot_dict)

        # Update the task with pre-execution parameters
        task_obj = self.dal.task.update({
            "id":
                task_obj.id,
            "before_snapshot_id":
                task_dict.get('before_snapshot_id', before_snapshot_obj.id),
            "ports":
                task_dict.get('ports', task_obj.ports),
            "gpu":
                task_dict.get('gpu', task_obj.gpu),
            "interactive":
                task_dict.get('interactive', task_obj.interactive),
            "task_dirpath":
                task_dict.get('task_dirpath', task_dirpath),
            "log_filepath":
                task_dict.get('log_filepath',
                              os.path.join(task_dirpath, "task.log")),
            "start_time":
                task_dict.get('start_time', datetime.utcnow())
        })

        # Copy over files from the before_snapshot file collection to task dir
        file_collection_obj =  \
            self.dal.file_collection.get_by_id(before_snapshot_obj.file_collection_id)
        self.file_driver.copytree(
            os.path.join(self.home, file_collection_obj.path),
            os.path.join(self.home, task_obj.task_dirpath))

        # Set the parameters set in the task
        environment_run_options = {
            "command": task_obj.command,
            "ports": [] if task_obj.ports is None else task_obj.ports,
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
        return_code, run_id, logs =  \
            self._run_helper(before_snapshot_obj.environment_id,
                             environment_run_options,
                             os.path.join(self.home, task_obj.log_filepath))

        # Create the after snapshot after execution is completed with new filepaths
        after_snapshot_dict = snapshot_dict.copy()
        after_snapshot_dict[
            'message'] = "autogenerated snapshot created after task %s is run" % task_obj.id

        # Add in absolute filepaths from running task directory
        absolute_task_dir_path = os.path.join(self.home, task_obj.task_dirpath)
        absolute_filepaths = []
        for item in os.listdir(absolute_task_dir_path):
            path = os.path.join(absolute_task_dir_path, item)
            if os.path.isfile(path) or os.path.isdir(path):
                absolute_filepaths.append(path)
        after_snapshot_dict.update({
            "filepaths": absolute_filepaths,
            "environment_id": before_snapshot_obj.environment_id,
        })
        after_snapshot_obj = self.snapshot.create(after_snapshot_dict)

        # (optional) Remove temporary task directory path
        # Update the task with post-execution parameters
        end_time = datetime.utcnow()
        duration = (end_time - task_obj.start_time).total_seconds()
        return self.dal.task.update({
            "id": task_obj.id,
            "after_snapshot_id": after_snapshot_obj.id,
            "run_id": run_id,
            "logs": logs,
            "results": self._parse_logs_for_results(logs),
            # "results": task_obj.results, # TODO: update during run
            "status": "SUCCESS" if return_code == 0 else "FAILED",
            "end_time": end_time,
            "duration": duration
        })

    def list(self, session_id=None):
        query = {}
        if session_id:
            query['session_id'] = session_id
        return self.dal.task.query(query)

    def get_files(self, task_id, mode="r"):
        """Get list of file objects for task id. It will look in the following areas in the following order

        1) look in the after snapshot for file collection
        2) look in the running task file collection
        3) look in the before snapshot for file collection

        Parameters
        ----------
        task_id : str
            id for the task you would like to get file objects for
        mode : str
            file open mode
            (default is "r" to open file for read)

        Returns
        -------
        list
            list of python file objects

        Raises
        ------
        PathDoesNotExist
            no file objects exist for the task
        """
        task_obj = self.dal.task.get_by_id(task_id)
        if task_obj.after_snapshot_id:
            # perform number 1) and return file list
            after_snapshot_obj = \
                self.dal.snapshot.get_by_id(task_obj.after_snapshot_id)
            file_collection_obj = \
                self.dal.file_collection.get_by_id(after_snapshot_obj.file_collection_id)
            return self.file_driver.\
                get_collection_files(file_collection_obj.filehash, mode=mode)
        elif task_obj.task_dirpath:
            # perform number 2) and return file list
            return self.file_driver.get(
                task_obj.task_dirpath, mode=mode, directory=True)
        elif task_obj.before_snapshot_id:
            # perform number 3) and return file list
            before_snapshot_obj = \
                self.dal.snapshot.get_by_id(task_obj.before_snapshot_id)
            file_collection_obj = \
                self.dal.file_collection.get_by_id(before_snapshot_obj.file_collection_id)
            return self.file_driver. \
                get_collection_files(file_collection_obj.filehash, mode=mode)
        else:
            # Error because the task does not have any files associated with it
            raise PathDoesNotExist()

    def delete(self, task_id):
        if not task_id:
            raise RequiredArgumentMissing(
                __("error", "controller.task.delete.arg", "id"))
        return self.dal.task.delete(task_id)

    def stop(self, task_id):
        """Stop and remove run for the task

        Parameters
        ----------
        task_id : str
            id for the task you would like to stop

        Returns
        -------
        return_code : bool
            system return code of the stop
        """
        if not task_id:
            raise RequiredArgumentMissing(
                __("error", "controller.task.stop.arg", "id"))
        task_obj = self.dal.task.get_by_id(task_id)
        run_id = task_obj.run_id
        return_code = self.environment.stop(run_id)
        return return_code
