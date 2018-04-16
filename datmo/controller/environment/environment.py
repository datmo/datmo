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
            definition_filepath : str
                absolute filepath to the environment definition file (e.g. ./Dockerfile)
            hardware_info : dict, optional
                information about the environment hardware
            description : str, optional
                description of the environment


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

        ## Required args
        required_args = ["driver_type", "definition_filename",
                         "hardware_info", "file_collection_id", "unique_hash"]
        for required_arg in required_args:
            # Add in any values that are
            if required_arg in dictionary:
                create_dict[required_arg] = dictionary[required_arg]
            else:
                # Pull in driver type from base
                if required_arg == "driver_type":
                    create_dict[required_arg] = self.environment_driver.type
                # Extract the hardware information
                elif required_arg == "hardware_info":
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
                # File setup
                elif required_arg == "file_collection_id":
                    if "definition_filepath" not in dictionary:
                        raise RequiredArgumentMissing(__("error",
                                                        "controller.environment.create"))
                    # Create environment files in the same dir as definition filepath
                    definition_path, definition_filename = os.path.split(dictionary['definition_filepath'])
                    # Create datmo environment definition in the same dir as definition filepath
                    datmo_definition_filepath = os.path.join(definition_path, "datmo" + definition_filename)
                    self.environment_driver.create(path=dictionary['definition_filepath'],
                                                   output_path=datmo_definition_filepath)
                    # Create hardware info file
                    hardware_info_filepath = os.path.join(definition_path, "hardware_info")
                    _ = JSONStore(hardware_info_filepath,
                                  initial_dict=create_dict['hardware_info'])

                    # Add all environment files to collection:
                    # definition path, datmo_definition_path, hardware_info
                    filepaths = [dictionary['definition_filepath'], datmo_definition_filepath,
                                 hardware_info_filepath]
                    file_collection_obj = self.file_collection.create(filepaths)
                    create_dict['file_collection_id'] = file_collection_obj.id
                    create_dict['definition_filename'] = definition_filename

                    # Delete temporary files created
                    os.remove(datmo_definition_filepath)
                    os.remove(hardware_info_filepath)
                elif required_arg == "unique_hash":
                    create_dict['unique_hash'] = file_collection_obj.filehash

        ## Optional args
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

            command : list
            ports : list
                Here are some example ports used for common applications.
                   *  'jupyter notebook' - 8888
                   *  flask API - 5000
                   *  tensorboard - 6006
            name : str
            volumes : dict
            detach : bool
            stdin_open : bool
            tty : bool
            gpu : bool
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