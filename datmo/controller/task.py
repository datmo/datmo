import os
import platform
from datmo.controller.base import BaseController
from datmo.controller.snapshot import SnapshotController
from datmo.util.exceptions import TaskRunException

class TaskController(BaseController):
    def __init__(self, home, dal_driver=None):
        self.snapshot = SnapshotController(home, dal_driver)
        super(TaskController, self).__init__(home, dal_driver)

    def create(self, dictionary):
        """ Create Task object

        Parameters
        ----------
        dictionary : dict
            Options for task, command is required

        Returns
        -------
        Task
            Errors out if unsuccessful

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
            if required_arg in dictionary:
                create_dict[required_arg] = dictionary[required_arg]

        # Create Task
        return self.dal.task.create(create_dict)

    def _run_helper(self, environment_id, environment_file_collection_id,
                    log_filepath, options_dict):
        """  Run container with parameters

        Parameters
        ----------
        environment_id : str
            the environment_driver id for definition
        environment_file_collection_id : str
            the file_collection_id for the environment_driver
        log_filepath : str
            filepath to the log file
        options_dict : dict
            Can include the following values:

            command : list
            ports : list
            name : str
            volumes : dict
            detach : bool
            stdin_open : bool
            tty : bool
            gpu : bool

        Returns
        -------
        return_code : int
            Return code of the environment that was run
        container_id : str
            ID of the container environment that was run
        hardware_info : str
            Information about the hardware of the device the environment was run on
        logs : str
            Output logs from the run

        """
        # TODO: Fix DAL to keep objects in sync and remove "environment_file_collection_id" as passed param
        # try:
        #     environment_obj = self.local.environment_driver.get_by_id(environment_id)
        # except:
        #     raise DoesNotExistException("exception.environment_driver.docker.build_environment", {
        #         "exception": "Environment specified does not exist."
        #     })

        # Extract hardware info of the container (currently taking from system platform)
        # TODO: extract hardware information directly from the container
        (system, node, release, version, machine, processor) = platform.uname()
        hardware_info = {
            'system': system,
            'node': node,
            'release': release,
            'version': version,
            'machine': machine,
            'processor': processor
        }

        # Run container with options provided
        run_container_options = {
            "command": options_dict.get('command', None),
            "ports": options_dict.get('ports', None),
            "name": options_dict.get('name', None),
            "volumes": options_dict.get('volumes', None),
            "detach": options_dict.get('detach', False),
            "stdin_open": options_dict.get('stdin_open', False),
            "tty": options_dict.get('tty', False),
            "gpu": options_dict.get('gpu', False),
            "api": False
        }

        # Build image for environment_driver
        environment_file_collection_path = self.file_driver.\
            get_collection_path(environment_file_collection_id)
        self.environment_driver.build_image(
            tag=environment_id,
            definition_path=os.path.join(environment_file_collection_path, 'datmoDockerfile')
        )

        # Run image with environment_driver
        run_return_code, container_id = \
            self.environment_driver.run_container(image_name=environment_id, **run_container_options)
        log_return_code, logs = self.environment_driver.log_container(container_id, filepath=log_filepath)

        final_return_code = run_return_code and log_return_code

        return final_return_code, container_id, hardware_info, logs

    def run(self, task_id, dictionary=None):
        """ Run a task with parameters. If dictionary specified,
        create a new task with new run parameters

        Parameters
        ----------
        task_id : str
            id for the task you would like to run
        dictionary : dict
            filepaths : list
            config_filename : str
            stats_filename : str
            environment_id : str
            environment_file_collection_id : str
            ...
            parameters for task run

        Returns
        -------
        Task
            Returns the Task object which completed its run with updated parameters

        Raises
        ______
        TaskRunException
            If there is any error in creating files for the task or downstream errors

        """
        # Obtain Task to run
        task_obj = self.dal.task.get_by_id(task_id)

        # Create Task directory for user during run
        try:
            task_dirpath = self.file_driver.create(
                os.path.join("datmo_tasks",
                             task_obj.id), dir=True)
        except:
            raise TaskRunException("exception.project.run",  {
                "exception": "Error creating task directory"
            })

        # Create the before snapshot prior to execution
        before_snapshot_obj = self.snapshot.create(dictionary)

        # Update the task with pre-execution parameters
        task_obj = self.dal.task.update({
            "id": task_obj.id,
            "before_snapshot_id": dictionary.get('before_snapshot_id',
                                                 before_snapshot_obj.id),
            "ports": dictionary.get('ports', task_obj.ports),
            "gpu": dictionary.get('gpu', task_obj.gpu),
            "interactive": dictionary.get('interactive', task_obj.interactive),
            "task_dirpath": dictionary.get('task_dirpath', task_dirpath),
            "log_filepath": dictionary.get('log_filepath', os.path.join(task_dirpath, "task.log"))
        })

        # Copy over files from the before_snapshot file collection to task dir
        self.file_driver.copytree(self.file_driver.get_collection_path(
            before_snapshot_obj.file_collection_id),
            task_obj.task_dirpath
        )

        # Set the parameters set in the task
        environment_run_options = {
            "command": task_obj.command,
            "ports": task_obj.ports,
            "gpu": task_obj.gpu,
            "name": "datmo-task-" + task_obj.id,
            "volumes": {
                task_obj.task_dirpath: {
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

        # Run environment_driver
        return_code, container_id, hardware_info, logs =  \
            self._run_helper(before_snapshot_obj.environment_id,
                             dictionary['environment_file_collection_id'],
                             task_obj.log_filepath, environment_run_options)

        # Create the after snapshot after execution is completed
        after_snapshot_create_dict = {
            "filepaths": [task_obj.task_dirpath],
            "environment_id": before_snapshot_obj.environment_id,
            "config": dictionary['config'],
            "stats": dictionary['stats']
        }
        after_snapshot_obj = self.snapshot.create(after_snapshot_create_dict)

        # (optional) Remove temporary task directory path

        # Update the task with post-execution parameters
        return self.dal.task.update({
            "id": task_obj.id,
            "after_snapshot_id": after_snapshot_obj.id,
            "hardware_info": hardware_info,
            "container_id": container_id,
            "logs": logs,
            "status": "SUCCESS" if return_code==0 else "FAILED",
        })