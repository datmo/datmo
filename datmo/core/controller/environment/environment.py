import os
import platform

from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.controller.file.file_collection import FileCollectionController
from datmo.core.entity.environment import Environment
from datmo.core.util.json_store import JSONStore
from datmo.core.util.misc_functions import get_datmo_temp_path, parse_path, list_all_filepaths
from datmo.core.util.exceptions import PathDoesNotExist, RequiredArgumentMissing, \
    TooManyArgumentsFound


class EnvironmentController(BaseController):
    """EnvironmentController inherits from BaseController and manages business logic related to the
    environment.

    Parameters
    ----------
    home : str
        home path of the project

    Methods
    -------
    create(dictionary)
        Create an environment within the project
    build(id)
        Build the environment for use within the project
    list()
        List all environments within the project
    delete(id)
        Delete the specified environment from the project
    """

    def __init__(self, home):
        super(EnvironmentController, self).__init__(home)
        self.file_collection = FileCollectionController(home)
        self._proj_env_dir = os.path.join(home, "datmo_environment")

    def create(self, dictionary):
        """Create an environment

        Parameters
        ----------
        dictionary : dict
            optional values to populate required environment entity args
                definition_paths : list, optional
                    list of absolute filepaths and/or dirpaths to collect for environment definition
                    (e.g. "/path/to/file:hello", "/path/to/file2", "/path/to/dir:newdir")
                    (default is to pull from datmo_environments/ folder and project root OR default driver definition if none found)
                hardware_info : dict, optional
                    information about the environment hardware
                    (default is to extract hardware from platform currently running)
            optional values to populate optional  environment entity args
                description : str, optional
                    description of the environment
                    (default is blank)


        Returns
        -------
        Environment
            returns an object representing the environment created

        Raises
        ------
        PathDoesNotExist
            if any source paths provided do not exist
        """
        # Validate Inputs
        create_dict = {"model_id": self.model.id}
        create_dict["driver_type"] = self.environment_driver.type

        # Create temp environment folder
        self._temp_env_dir = get_datmo_temp_path(self.home)

        # Step 1: Populate a path list from the user inputs in a format compatible
        # with the input of the File Collection create function
        paths = []

        # a. add in user given paths as is if they exist
        if "definition_paths" in dictionary and dictionary['definition_paths']:
            paths.extend(dictionary['definition_paths'])

        # b. if there exists datmo_environments folder, add in absolute paths
        if os.path.isdir(self._proj_env_dir):
            paths.extend([
                os.path.join(self._proj_env_dir, filepath)
                for filepath in list_all_filepaths(self._proj_env_dir)
            ])

        # c. add in default environment definition filepath as specified by the environment driver
        # if path exists and NO OTHER PATHS exist
        src_environment_filepath = self.environment_driver.get_default_definition_path(
        )
        _, environment_filename = os.path.split(src_environment_filepath)
        create_dict['definition_filename'] = environment_filename
        if not paths and os.path.exists(src_environment_filepath):
            paths.append(src_environment_filepath + ":" + environment_filename)

        # Step 2: Check existing paths and create files as needed to populate the
        # full environment within the temporary directory

        # a. look for the default definition, if not present add it to temp directory, and add it to paths
        original_definition_filepath = ""
        if all(environment_filename not in path for path in paths):
            self.environment_driver.create_default_definition(
                self._temp_env_dir)
            original_definition_filepath = os.path.join(
                self._temp_env_dir, environment_filename)
            paths.append(original_definition_filepath)
        else:
            for idx, path in enumerate(paths):
                if environment_filename in path:
                    src_path, dest_path = parse_path(path)
                    original_definition_filepath = src_path

        # b. use the default definition and create a datmo definition in the temp directory, and add to paths
        datmo_definition_filepath = \
            os.path.join(self._temp_env_dir, "datmo" + environment_filename)
        if not os.path.isfile(datmo_definition_filepath):
            _, original_definition_filepath, datmo_definition_filepath = \
                self.environment_driver.create(path=original_definition_filepath, output_path=datmo_definition_filepath)
        paths.append(datmo_definition_filepath)

        # c. get the hardware info and save it in the temp directory, and add to paths
        hardware_info_filepath = self._store_hardware_info(
            dictionary, create_dict, self._temp_env_dir)
        paths.append(hardware_info_filepath)

        # Step 3: Pass in all paths for the environment to the file collection create
        # If PathDoesNotExist is found for any source paths, then error
        try:
            file_collection_obj = self.file_collection.create(paths)
        except PathDoesNotExist as e:
            raise PathDoesNotExist(
                __("error", "controller.environment.create.filepath.dne",
                   str(e)))

        # Step 4: Add file collection information to create dict and check unique hash
        create_dict['file_collection_id'] = file_collection_obj.id
        create_dict['unique_hash'] = file_collection_obj.filehash
        # Check if unique hash is unique or not.
        # If not, DO NOT CREATE Environment and return existing Environment object
        results = self.dal.environment.query({
            "unique_hash": file_collection_obj.filehash
        })
        if results: return results[0]

        # Step 5: Add optional arguments to the Environment entity
        for optional_arg in ["description"]:
            if optional_arg in dictionary:
                create_dict[optional_arg] = dictionary[optional_arg]

        # Step 6: Create environment and return
        return self.dal.environment.create(Environment(create_dict))

    def _store_hardware_info(self, dictionary, create_dict, definition_path):
        if "hardware_info" in dictionary:
            create_dict['hardware_info'] = dictionary['hardware_info']
        else:
            # Extract hardware info of the container (currently taking from system platform)
            # TODO: extract hardware information directly from the container
            (system, node, release, version, machine,
             processor) = platform.uname()
            create_dict['hardware_info'] = {
                'system': system,
                'node': node,
                'release': release,
                'version': version,
                'machine': machine,
                'processor': processor
            }
        # Create hardware info file in definition path
        hardware_info_filepath = os.path.join(definition_path, "hardware_info")
        _ = JSONStore(
            hardware_info_filepath, initial_dict=create_dict['hardware_info'])
        return hardware_info_filepath

    def build(self, environment_id):
        """Build environment from definition file

        Parameters
        ----------
        environment_id : str
            environment object id to build

        Returns
        -------
        bool
            returns True if success

        Raises
        ------
        PathDoesNotExist
            if the specified Environment does not exist.
        """
        self.environment_driver.init()
        environment_obj = self.dal.environment.get_by_id(environment_id)
        if not environment_obj:
            raise PathDoesNotExist(
                __("error", "controller.environment.build", environment_id))
        file_collection_obj = self.dal.file_collection.\
            get_by_id(environment_obj.file_collection_id)
        # TODO: Check hardware info here if different from creation time
        # Build the Environment with the driver
        datmo_definition_filepath = os.path.join(
            self.home, file_collection_obj.path,
            "datmo" + environment_obj.definition_filename)
        result = self.environment_driver.build(
            environment_id, path=datmo_definition_filepath)
        return result

    def run(self, environment_id, options, log_filepath):
        """Run and log an instance of the environment with the options given

        Parameters
        ----------
        environment_id : str
        options : dict
            can include the following values:

            command : list, optional
            ports : list, optional
                Here are some example ports used for common applications.
                   *  'jupyter notebook' - 8888
                   *  flask API - 5000
                   *  tensorboard - 6006
                An example input for the above would be ["8888:8888", "5000:5000", "6006:6006"]
                which maps the running host port (right) to that of the environment (left)
            name : str, optional
            volumes : dict, optional
            gpu : bool, default False
            detach : bool, optional
            stdin_open : bool, optional
            tty : bool, optional
        log_filepath : str
            filepath to the log file

        Returns
        -------
        return_code : int
            system return code for container and logs
        run_id : str
            identification for run of the environment
        logs : str
            string version of output logs for the container
        """
        self.environment_driver.init()
        # TODO: Check hardware info here if different from creation time
        final_return_code, run_id, logs = \
            self.environment_driver.run(environment_id, options, log_filepath)
        return final_return_code, run_id, logs

    def list(self):
        # TODO: Add time filters
        return self.dal.environment.query({})

    def delete(self, environment_id):
        """Delete all traces of an environment

        Parameters
        ----------
        environment_id : str
            environment object id to remove

        Returns
        -------
        bool
            True if success

        Raises
        ------
        PathDoesNotExist
            if the specified Environment does not exist.
        """
        self.environment_driver.init()
        environment_obj = self.dal.environment.get_by_id(environment_id)
        if not environment_obj:
            raise PathDoesNotExist(
                __("error", "controller.environment.delete", environment_id))
        # Remove file collection
        file_collection_deleted = self.file_collection.delete(
            environment_obj.file_collection_id)
        # Remove artifacts associated with the environment_driver
        environment_artifacts_removed = self.environment_driver.remove(
            environment_id, force=True)
        # Delete environment_driver object
        delete_success = self.dal.environment.delete(environment_obj.id)

        return file_collection_deleted and environment_artifacts_removed and \
               delete_success

    def stop(self, run_id=None, match_string=None, all=False):
        """Stop the trace of running environment

        Parameters
        ----------
        run_id : str, optional
            stop environment with specific run id
            (default is None, which means it is not used)
        match_string : str, optional
            stop environment with a string to match the environment name
            (default is None, which means it is not used)
        all : bool, optional
            stop all environments

        Notes
        -----
            The user must provide only one of the above, if multiple are given
            or none are given the function will error

        Returns
        -------
        bool
            True if success

        Raises
        ------
        RequiredArgumentMissing
        TooManyArguments
        """
        self.environment_driver.init()
        if not (run_id or match_string or all):
            raise RequiredArgumentMissing()
        if sum(map(bool, [run_id, match_string, all])) > 1:
            raise TooManyArgumentsFound()
        if run_id:
            # Stop the instance(e.g. container) running using environment driver(e.g. docker)
            stop_success = self.environment_driver.stop(run_id, force=True)
        if match_string:
            # Stop all tasks matching the string given
            stop_success = self.environment_driver.stop_remove_containers_by_term(
                term=match_string, force=True)
        if all:
            # Stop all tasks associated within the enclosed project
            all_match_string = "datmo-task-" + self.model.id
            stop_success = self.environment_driver.stop_remove_containers_by_term(
                term=all_match_string, force=True)
        return stop_success
