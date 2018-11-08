import os
import shutil

from datmo.core.controller.base import BaseController
from datmo.core.controller.file.file_collection import FileCollectionController
from datmo.core.entity.environment import Environment
from datmo.core.util.i18n import get as __
from datmo.core.util.validation import validate
from datmo.core.util.spinner import Spinner
from datmo.core.util.json_store import JSONStore
from datmo.core.util.misc_functions import get_datmo_temp_path, list_all_filepaths
from datmo.core.util.exceptions import PathDoesNotExist, RequiredArgumentMissing, TooManyArgumentsFound,\
    EnvironmentNotInitialized, UnstagedChanges, ArgumentError, EnvironmentDoesNotExist, ProjectNotInitialized


class EnvironmentController(BaseController):
    """EnvironmentController inherits from BaseController and manages business logic related to the
    environment.

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

    def __init__(self):
        super(EnvironmentController, self).__init__()
        self.file_collection = FileCollectionController()
        self.spinner = Spinner()
        if not self.is_initialized:
            raise ProjectNotInitialized(
                __("error", "controller.environment.__init__"))

    def get_environment_types(self):
        """Get the environment types

        Returns
        -------
        list
            List of supported environment type
        """
        return self.environment_driver.get_environment_types()

    def get_supported_frameworks(self, environment_type):
        """Get all the supported frameworks

        Parameters
        ----------
        environment_type : str
            the type of environment

        Returns
        -------
        list
            List of available frameworks and their info
        """
        return self.environment_driver.get_supported_frameworks(
            environment_type)

    def get_supported_languages(self, environment_type, environment_framework):
        """Get all the supported languages for the environment

        Parameters
        ----------
        environment_type : str
            the type of environment
        environment_framework : str
            the framework for the environment

        Returns
        -------
        list
            List of available languages for the environments
        """
        return self.environment_driver.get_supported_languages(
            environment_type, environment_framework)

    def setup(self, options, save_hardware_file=True):
        """Create a pre-defined supported environment and add it to the project environment directory

        The user can build on top of the pre-defined environment and create new ones of their own

        Parameters
        ----------
        options : dict
            can include the following values:

            name : str
                the name to be used to specify a supported environment
        save_hardware_file : bool, optional
            boolean to save hardware file along with other files
            (default is True to save the file and create distinct hashes based on software and hardware)

        Returns
        -------
        Environment
            returns an object representing the environment created

        Raises
        ------
        UnstagedChanges
            if unstaged changes exist in the environment it should fail
        """
        # Check unstaged changes before trying to setup
        try:
            self.check_unstaged_changes()
        except UnstagedChanges:
            raise UnstagedChanges(
                __("error", "controller.environment.setup.unstaged",
                   self.environment_driver.environment_directory_path))
        try:
            _ = self.environment_driver.setup(
                options,
                definition_path=self.environment_driver.
                environment_directory_path)
        except Exception:
            raise
        name = options.get('name', None)
        if name is None:
            environment_framework = options['environment_framework']
            environment_type = options['environment_type']
            environment_language = options['environment_language']
            if environment_language:
                name = "%s:%s-%s" % (environment_framework, environment_type,
                                     environment_language)
            else:
                name = "%s:%s" % (environment_framework, environment_type)
        create_dict = {
            "name": name,
            "description": "supported environment created by datmo"
        }
        return self.create(create_dict, save_hardware_file=save_hardware_file)

    def current_environment(self):
        """Get the current environment object

        Returns
        -------
        Environment
            returns an object representing the current environment state

        Raises
        ------
        UnstagedChanges
            if there are unstaged changes error out because no current environment
        """
        self.check_unstaged_changes()
        return self.create({})

    def create(self, dictionary, save_hardware_file=True):
        """Create an environment

        Parameters
        ----------
        dictionary : dict
            optional values to populate required environment entity args
                paths : list, optional
                    list of absolute or relative filepaths and/or dirpaths to collect with destination names
                    (e.g. "/path/to/file>hello", "/path/to/file2", "/path/to/dir>newdir")
                    (default if none provided is to pull from project environment folder and project root. If none found create default definition)
                name : str, optional
                    name of the environment
                    (default is None)
                description : str, optional
                    description of the environment
                    (default is None)
        save_hardware_file : bool
            boolean to save hardware file along with other files
            (default is True to save the file and create distinct hashes based on software and hardware)

        Returns
        -------
        Environment
            returns an object representing the environment created

        Raises
        ------
        EnvironmentDoesNotExist
            if there is no environment found after given parameters and defaults are checked
        PathDoesNotExist
            if any source paths provided do not exist
        """
        # Validate Inputs
        create_dict = {"model_id": self.model.id}
        create_dict["driver_type"] = self.environment_driver.type

        validate("create_environment", dictionary)

        # Create temp environment folder
        _temp_env_dir = get_datmo_temp_path(self.home)
        # Step 1: Populate a path list from the user inputs in a format compatible
        # with the input of the File Collection create function
        paths = []

        # a. add in user given paths as is if they exist
        if "paths" in dictionary and dictionary['paths']:
            paths.extend(dictionary['paths'])

        # b. if there exists project environment directory AND no paths exist, add in absolute paths
        if not paths and os.path.isdir(
                self.environment_driver.environment_directory_path):
            paths.extend([
                os.path.join(
                    self.environment_driver.environment_directory_path,
                    filepath) for filepath in list_all_filepaths(
                        self.environment_driver.environment_directory_path)
            ])

        # c. add in default environment definition filepath as specified by the environment driver
        # if path exists and NO OTHER PATHS exist
        src_environment_filename = self.environment_driver.get_default_definition_filename(
        )
        src_environment_filepath = os.path.join(self.home,
                                                src_environment_filename)
        _, environment_filename = os.path.split(src_environment_filepath)
        create_dict['definition_filename'] = environment_filename
        if not paths and os.path.exists(src_environment_filepath):
            paths.append(src_environment_filepath)

        # Step 2: Check existing paths and create files as needed to populate the
        # full environment within the temporary directory

        paths = self._setup_compatible_environment(
            create_dict,
            paths,
            _temp_env_dir,
            save_hardware_file=save_hardware_file)

        # Step 3: Pass in all paths for the environment to the file collection create
        # If PathDoesNotExist is found for any source paths, then error
        if not paths:
            raise EnvironmentDoesNotExist()
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

        # Step 5: Delete the temporary directory
        shutil.rmtree(_temp_env_dir)

        # Step 6: Add optional arguments to the Environment entity
        for optional_arg in ["name", "description"]:
            if optional_arg in dictionary:
                create_dict[optional_arg] = dictionary[optional_arg]

        # Step 7: Create environment and return
        return self.dal.environment.create(Environment(create_dict))

    def build(self, environment_id, workspace=None):
        """Build environment from definition file

        Parameters
        ----------
        environment_id : str
            environment object id to build
        workspace : str
            workspace to be used
        Returns
        -------
        bool
            returns True if success

        Raises
        ------
        EnvironmentDoesNotExist
            if the specified Environment does not exist.
        """
        self.environment_driver.init()
        if not self.exists(environment_id):
            raise EnvironmentDoesNotExist(
                __("error", "controller.environment.build", environment_id))
        environment_obj = self.dal.environment.get_by_id(environment_id)
        file_collection_obj = self.dal.file_collection.\
            get_by_id(environment_obj.file_collection_id)
        # TODO: Check hardware info here if different from creation time
        # Add in files for that environment id
        environment_definition_path = os.path.join(self.home,
                                                   file_collection_obj.path)
        # Copy to temp folder and remove files that are datmo specific
        _temp_env_dir = get_datmo_temp_path(self.home)
        self.file_driver.copytree(environment_definition_path, _temp_env_dir)
        # get definition filepath for the temp folder
        environment_definition_filepath = os.path.join(
            _temp_env_dir, environment_obj.definition_filename)
        try:
            # Build the Environment with the driver
            self.spinner.start()
            result = self.environment_driver.build(
                environment_id,
                path=environment_definition_filepath,
                workspace=workspace)
        finally:
            self.spinner.stop()
        # Remove both temporary directories
        shutil.rmtree(_temp_env_dir)
        return result

    def extract_workspace_url(self, name, workspace=None):
        """Extract workspace url from the environment

        Parameters
        ----------
        name : str
            name of the environment being run
        workspace : str
            workspace being used for the run

        Returns
        -------
        str
            web url for the workspace being run, None if it doesn't exist
        """
        return self.environment_driver.extract_workspace_url(name, workspace)

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
            mem_limit : str, optional
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

    def update(self, environment_id, name=None, description=None):
        """Update the environment metadata"""
        if not self.exists(environment_id):
            raise EnvironmentDoesNotExist()
        update_environment_input_dict = {"id": environment_id}
        if name:
            update_environment_input_dict['name'] = name
        if description:
            update_environment_input_dict['description'] = description
        return self.dal.environment.update(update_environment_input_dict)

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
        EnvironmentDoesNotExist
            if the specified Environment does not exist.
        """
        self.environment_driver.init()
        if not self.exists(environment_id):
            raise EnvironmentDoesNotExist(
                __("error", "controller.environment.delete", environment_id))
        # Remove file collection
        environment_obj = self.dal.environment.get_by_id(environment_id)
        file_collection_deleted = self.file_collection.delete(
            environment_obj.file_collection_id)
        # Remove artifacts associated with the environment_driver
        environment_artifacts_removed = self.environment_driver.remove(
            environment_id, force=True)
        # Delete environment object
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
        stop_success = False
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

    def exists(self, environment_id=None, environment_unique_hash=None):
        """Returns a boolean if the environment exists

        Parameters
        ----------
        environment_id : str
            environment id to check for
        environment_unique_hash : str
            unique hash for the environment to check for

        Returns
        -------
        bool
            True if exists else False
        """
        if environment_id:
            environment_objs = self.dal.environment.query({
                "id": environment_id
            })
        elif environment_unique_hash:
            environment_objs = self.dal.environment.query({
                "unique_hash": environment_unique_hash
            })
        else:
            raise ArgumentError()
        env_exists = False
        if environment_objs:
            env_exists = True
        return env_exists

    def check_unstaged_changes(self):
        """Checks if there exists any unstaged changes for the environment in project environment directory.

        Returns
        -------
        bool
            False if it's already staged else error

        Raises
        ------
        EnvironmentNotInitialized
            if the environment driver is not initialized properly, will fail
        UnstagedChanges
            error if not there exists unstaged changes in environment
        """
        if not self.environment_driver.is_initialized:
            raise EnvironmentNotInitialized()

        # Check if unstaged changes exist
        if self._has_unstaged_changes():
            raise UnstagedChanges()

        return False

    def checkout(self, environment_id):
        """Checkout to specific environment id

        Parameters
        ----------
        environment_id : str
            environment id to checkout to

        Returns
        -------
        bool
            True if success

        Raises
        ------
        EnvironmentNotInitialized
            error if not initialized (must initialize first)
        PathDoesNotExist
            if environment id does not exist
        UnstagedChanges
            error if not there exists unstaged changes in environment

        """
        if not self.is_initialized:
            raise EnvironmentNotInitialized()
        if not self.exists(environment_id):
            raise EnvironmentDoesNotExist(
                __("error", "controller.environment.checkout_env",
                   environment_id))
        # Check if unstaged changes exist
        if self._has_unstaged_changes():
            raise UnstagedChanges()
        # Check if environment has is same as current
        results = self.dal.environment.query({"id": environment_id})
        environment_obj = results[0]
        environment_hash = environment_obj.unique_hash

        if self._calculate_project_environment_hash() == environment_hash:
            return True
        # Remove all content from project environment directory
        for file in os.listdir(
                self.environment_driver.environment_directory_path):
            file_path = os.path.join(
                self.environment_driver.environment_directory_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
        # Add in files for that environment id
        file_collection_obj = self.dal.file_collection.\
            get_by_id(environment_obj.file_collection_id)
        environment_definition_path = os.path.join(self.home,
                                                   file_collection_obj.path)
        # Copy to temp folder and remove files that are datmo specific
        _temp_env_dir = get_datmo_temp_path(self.home)
        self.file_driver.copytree(environment_definition_path, _temp_env_dir)
        for filename in self.environment_driver.get_datmo_definition_filenames(
        ):
            os.remove(os.path.join(_temp_env_dir, filename))
        # Copy from temp folder to project environment directory
        self.file_driver.copytree(
            _temp_env_dir, self.environment_driver.environment_directory_path)
        shutil.rmtree(_temp_env_dir)
        return True

    def _setup_compatible_environment(self,
                                      create_dict,
                                      paths,
                                      directory,
                                      save_hardware_file=True):
        """Setup compatible environment from user paths. Creates the necessary datmo files if
        they are not already present

        Parameters
        ----------
        create_dict : dict
            dictionary for entity creation, this is mutated in the function (not returned)
        paths : list
            list of absolute or relative filepaths and/or dirpaths to collect with destination names
            (e.g. "/path/to/file>hello", "/path/to/file2", "/path/to/dir>newdir")
        directory : str
            path of directory to save additional files to
        save_hardware_file : bool
            boolean to save hardware file along with other files
            (default is True to save the file and create distinct hashes based on software and hardware)

        Returns
        -------
        paths : list
            returns the input paths with the paths of the new files created appended
        """
        # a. look for the default definition, if not present add it to the directory, and add it to paths
        if all(create_dict['definition_filename'] not in path
               for path in paths):
            self.environment_driver.create_default_definition(directory)
            original_definition_filepath = os.path.join(
                directory, create_dict['definition_filename'])
            paths.append(original_definition_filepath)

        # b. get the hardware info and save it to the entity, if save_hardware_file is True
        # then save it to file and add it to the paths
        create_dict[
            'hardware_info'] = self.environment_driver.get_hardware_info()
        if save_hardware_file:
            hardware_info_filepath = os.path.join(directory, "hardware_info")
            _ = JSONStore(
                hardware_info_filepath,
                initial_dict=create_dict['hardware_info'])
            paths.append(hardware_info_filepath)
        return paths

    def _calculate_project_environment_hash(self, save_hardware_file=True):
        """Return the environment hash from contents in project environment directory.
        If environment_directory not present then will assume it is empty

        Parameters
        ----------
        save_hardware_file : bool
            include the hardware info file within the hash

        Returns
        -------
        str
            unique hash of the project environment directory
        """
        # Populate paths from the project environment directory
        paths = []
        if os.path.isdir(self.environment_driver.environment_directory_path):
            paths.extend([
                os.path.join(
                    self.environment_driver.environment_directory_path,
                    filepath) for filepath in list_all_filepaths(
                        self.environment_driver.environment_directory_path)
            ])

        # Create a temp dir to save any additional files necessary
        _temp_dir = get_datmo_temp_path(self.home)

        # Setup compatible environment and create add paths
        paths = self._setup_compatible_environment(
            {
                "definition_filename":
                    self.environment_driver.get_default_definition_filename()
            },
            paths,
            _temp_dir,
            save_hardware_file=save_hardware_file)

        # Create new temp directory
        _temp_dir_2 = get_datmo_temp_path(self.home)

        # Hash the paths of the environment with a different temp dir
        dirhash = self.file_driver.calculate_hash_paths(paths, _temp_dir_2)

        # Remove both temporary directories
        shutil.rmtree(_temp_dir)
        shutil.rmtree(_temp_dir_2)

        return dirhash

    def _has_unstaged_changes(self):
        """Return whether there are unstaged changes"""
        env_hash = self._calculate_project_environment_hash()
        env_hash_no_hardware = self._calculate_project_environment_hash(
            save_hardware_file=False)
        environment_files = list_all_filepaths(
            self.environment_driver.environment_directory_path)
        if self.exists(environment_unique_hash=env_hash) or self.exists(
                environment_unique_hash=env_hash_no_hardware
        ) or not environment_files:
            return False
        return True
