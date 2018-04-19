import os
import platform

from datmo.util.i18n import get as __
from datmo.controller.base import BaseController
from datmo.controller.file.file_collection import FileCollectionController
from datmo.util.json_store import JSONStore
from datmo.util.exceptions import RequiredArgumentMissing, \
    DoesNotExistException


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
    def __init__(self, home, dal_driver=None):
        super(EnvironmentController, self).__init__(home, dal_driver)
        self.file_collection = FileCollectionController(home, self.dal.driver)

    def create(self, dictionary):
        """Create an Environment

        Parameters
        ----------
        dictionary : dict
            optional values to populate required environment entity args
                definition_filepath : str, optional
                    absolute filepath to the environment definition file
                    (default is to use driver default filepath)
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

        create_dict = {
            "model_id": self.model.id,
        }

        # Required args for Environment entity
        required_args = ["driver_type", "definition_filename",
                         "hardware_info", "file_collection_id", "unique_hash"]
        for required_arg in required_args:
            # Pull in driver type from base
            if required_arg == "driver_type":
                create_dict[required_arg] = self.environment_driver.type
            elif required_arg == "definition_filename":
                language = dictionary.get("language", "python3")
                create_dict['language'] = language
                if "definition_filepath" in dictionary:
                    original_definition_filepath = dictionary['definition_filepath']
                    # Split up the given path and save definition filename
                    definition_path, definition_filename = \
                        os.path.split(original_definition_filepath)
                    create_dict['definition_filename'] = definition_filename
                    # Create datmo environment definition in the same dir as definition filepath
                    datmo_definition_filepath = \
                        os.path.join(definition_path, "datmo" + definition_filename)
                    _, _, _, requirements_filepath = self.environment_driver.create(path=dictionary['definition_filepath'],
                                                   output_path=datmo_definition_filepath)
                else:
                    # Use the default create to find environment definition
                    _, original_definition_filepath, datmo_definition_filepath, requirements_filepath = \
                        self.environment_driver.create(language=language)
                    # Split up the default path obtained to save the definition name
                    definition_path, definition_filename = \
                        os.path.split(original_definition_filepath)
                    create_dict['definition_filename'] = definition_filename

            # Extract the hardware information
            elif required_arg == "hardware_info":
                if "hardware_info" in dictionary:
                    create_dict['hardware_info'] = dictionary['hardware_info']
                else:
                    # Extract hardware info of the container (currently taking from system platform)
                    # TODO: extract hardware information directly from the container
                    (system, node, release, version, machine, processor) = platform.uname()
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
                _ = JSONStore(hardware_info_filepath,
                              initial_dict=create_dict['hardware_info'])
            # File collection setup using files created above
            elif required_arg == "file_collection_id":
                # Add all environment files to collection:
                # definition path, datmo_definition_path, hardware_info
                if not requirements_filepath:
                    filepaths = [original_definition_filepath, datmo_definition_filepath,
                                 hardware_info_filepath]
                else:
                    filepaths = [original_definition_filepath, datmo_definition_filepath,
                                 requirements_filepath, hardware_info_filepath]
                file_collection_obj = self.file_collection.create(filepaths)
                create_dict['file_collection_id'] = file_collection_obj.id

                # Delete temporary files created once transfered into file collection
                os.remove(datmo_definition_filepath)
                os.remove(hardware_info_filepath)
            # Create new unique hash or find existing from the file collection above
            elif required_arg == "unique_hash":
                create_dict['unique_hash'] = file_collection_obj.filehash
                # Check if unique hash is unique or not.
                # If not, DO NOT CREATE Environment and return existing Environment object
                results = self.dal.environment.query({
                    "unique_hash": file_collection_obj.filehash
                })
                if results: return results[0];
            else:
                NotImplementedError()

        # Optional args for Environment entity
        optional_args = ["description"]
        for optional_arg in optional_args:
            if optional_arg in dictionary:
                create_dict[optional_arg] = dictionary[optional_arg]


        # Create environment and return
        return self.dal.environment.create(create_dict)

    def build(self, id):
        """Build Environment from definition file

        Parameters
        ----------
        id : str
            environment object id to build

        Returns
        -------
        bool
            returns True if success

        Raises
        ------
        DoesNotExistException
            if the specified Environment does not exist.
        """
        environment_obj = self.dal.environment.get_by_id(id)
        if not environment_obj:
            raise DoesNotExistException(__("error",
                                          "controller.environment.build",
                                          id))
        file_collection_obj = self.dal.file_collection.\
            get_by_id(environment_obj.file_collection_id)
        # TODO: Check hardware info here if different from creation time
        # Build the Environment with the driver
        datmo_definition_filepath = os.path.join(self.home, file_collection_obj.path,
                                                 "datmo" + environment_obj.definition_filename)
        result = self.environment_driver.build(id, path=datmo_definition_filepath)
        return result

    def run(self, id, options, log_filepath):
        """Run and log an instance of the environment with the options given

        Parameters
        ----------
        id : str
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
            detach : bool, optional
            stdin_open : bool, optional
            tty : bool, optional
            gpu : bool, optional
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
        # TODO: Check hardware info here if different from creation time
        final_return_code, run_id, logs = \
            self.environment_driver.run(id, options, log_filepath)
        return final_return_code, run_id, logs

    def list(self):
        # TODO: Add time filters
        return self.dal.environment.query({})

    def delete(self, id):
        """Delete all traces of an Environment

        Parameters
        ----------
        id : str
            environment object id to remove

        Returns
        -------
        bool
            True if success

        Raises
        ------
        DoesNotExistException
            if the specified Environment does not exist.
        """
        environment_obj = self.dal.environment.get_by_id(id)
        if not environment_obj:
            raise DoesNotExistException(__("error",
                                          "controller.environment.delete",
                                          id))
        # Remove file collection
        file_collection_deleted = self.file_collection.delete(environment_obj.file_collection_id)
        # Remove artifacts associated with the environment_driver
        environment_artifacts_removed = self.environment_driver.remove(id, force=True)
        # Delete environment_driver object
        delete_success = self.dal.environment.delete(environment_obj.id)

        return file_collection_deleted and environment_artifacts_removed and \
               delete_success