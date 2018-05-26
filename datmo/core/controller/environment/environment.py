import os
import shutil
import tempfile
import platform

from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.controller.file.file_collection import FileCollectionController
from datmo.core.entity.environment import Environment
from datmo.core.util.json_store import JSONStore
from datmo.core.util.exceptions import PathDoesNotExist, RequiredArgumentMissing, \
    TooManyArgumentsFound, FileAlreadyExistsError


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
        self._env_dir = os.path.join(home, ".datmo", "environment")
        # creating the environment hidden dir
        if not os.path.isdir(self._env_dir):
            os.makedirs(self._env_dir)
        self._proj_env_dir = os.path.join(home, "datmo_environment")

    def create(self, dictionary):
        """Create an environment

        Parameters
        ----------
        dictionary : dict
            optional values to populate required environment entity args
                definition_filepaths : list, optional
                    list of absolute filepath in string to the environment definition file
                    (default is to use a list of driver default filepath)
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
        RequiredArgumentMissing
            if any arguments above are not provided.
        """
        # Validate Inputs
        create_dict = {"model_id": self.model.id}
        create_dict["driver_type"] = self.environment_driver.type

        self.temp_env_dir = tempfile.mkdtemp(dir=self._env_dir)

        # Step 1: Collate all files in datmo env temp
        # a. if there exists datmo_environments folder, then content from it
        # is copied into temp env directory
        if os.path.isdir(self._proj_env_dir):
            self.file_driver.copytree(self._proj_env_dir, self.temp_env_dir)

        all_current_filenames = [f for f in os.listdir(self.temp_env_dir)
                             if os.path.isfile(os.path.join(self.temp_env_dir, f))]

        # b. if any file is being passed as `definition_filepaths`
        if "definition_filepaths" in dictionary and dictionary['definition_filepaths']:
            filepaths = dictionary['definition_filepaths']
            for filepath in filepaths:
                filepath_list = filepath.split(":")

                # Creating src, dst files
                if len(filepath_list) == 2:
                    src_filepath = filepath_list[0]
                    filename = filepath_list[1]
                    dst_filepath = os.path.join(self.temp_env_dir, filename)
                else:
                    src_filepath = filepath
                    _, filename = os.path.split(filepath)
                    dst_filepath = os.path.join(self.temp_env_dir, filename)

                # Check for src to exist and dst to not exist
                if not os.path.exists(src_filepath):
                    raise PathDoesNotExist(
                        __("error", "controller.environment.create.filepath.dne",
                           src_filepath))
                if filename in all_current_filenames:
                    raise FileAlreadyExistsError(
                        __("error",
                           "controller.environment.create.file.exists.datmoenvironment",
                           dst_filepath))
                if os.path.exists(dst_filepath):
                    raise FileAlreadyExistsError(
                        __("error",
                           "controller.environment.create.filename.exists",
                           dst_filepath))
                shutil.copy2(src_filepath, dst_filepath)

        all_current_filenames = [f for f in os.listdir(self.temp_env_dir)
                             if os.path.isfile(os.path.join(self.temp_env_dir, f))]

        # c. copy default environment file from root project directory only if
        # there are still no files in hidden environment folder
        src_environment_filepath = self.environment_driver.default_environment_definition()
        _, environment_filename = os.path.split(src_environment_filepath)
        if not all_current_filenames and os.path.exists(src_environment_filepath):
            dst_environment_filepath = os.path.join(self.temp_env_dir, environment_filename)
            shutil.copy2(src_environment_filepath, dst_environment_filepath)

        all_current_filenames = [f for f in os.listdir(self.temp_env_dir)
                             if os.path.isfile(os.path.join(self.temp_env_dir, f))]

        # Step 2: Check if the necessary environment filepath exists, else create
        # Dockerfile with baseimage
        if environment_filename not in all_current_filenames:
            self.environment_driver.create_default_dockerfile(self.temp_env_dir)

        # Step 3: Create datmo definition filepath
        original_definition_filepath = os.path.join(self.temp_env_dir, environment_filename)

        # Step 4: Create datmo environment definition in the same dir as definition filepath
        # Split up the given path and save definition filename
        definition_path, definition_filename = \
            os.path.split(original_definition_filepath)
        create_dict['definition_filename'] = definition_filename
        datmo_definition_filepath = \
            os.path.join(definition_path, "datmo" + definition_filename)
        _, original_definition_filepath, datmo_definition_filepath = \
            self.environment_driver.create(path=original_definition_filepath, output_path=datmo_definition_filepath)
        self._store_hardware_info(dictionary, create_dict, definition_path)

        # Add all environment files to collection:
        filepaths = [os.path.join(self.temp_env_dir, f) for f in os.listdir(self.temp_env_dir)
                                 if os.path.isfile(os.path.join(self.temp_env_dir, f))]

        file_collection_obj = self.file_collection.create(filepaths)
        create_dict['file_collection_id'] = file_collection_obj.id
        create_dict['unique_hash'] = file_collection_obj.filehash
        # Check if unique hash is unique or not.
        # If not, DO NOT CREATE Environment and return existing Environment object
        results = self.dal.environment.query({
            "unique_hash": file_collection_obj.filehash
        })
        if results: return results[0]

        # Optional args for Environment entity
        for optional_arg in ["description"]:
            if optional_arg in dictionary:
                create_dict[optional_arg] = dictionary[optional_arg]

        # Create environment and return
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