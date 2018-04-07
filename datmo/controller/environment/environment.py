import os
import hashlib
from datmo.controller.base import BaseController
from datmo.util.exceptions import RequiredArgumentMissing, \
    DoesNotExistException

class EnvironmentController(BaseController):
    def __init__(self, home, dal_driver=None):
        super(EnvironmentController, self).__init__(home, dal_driver)

    def _get_filehash(self, filepath):
        if not os.path.isfile(filepath):
            raise DoesNotExistException("exception.environment_driver.docker.create_environment", {
                "exception": "filepath is not a file."
            })
        BUFF_SIZE = 65536
        sha1 = hashlib.md5()
        with open(filepath, "rb") as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def create(self, dictionary):
        """ Create an Environment

        Parameters
        ----------
        dictionary : dict
            driver_type : str
                Environment driver type to use
            definition_filepath : str
                Absolute filepath to the Environment definition file

        Returns
        -------
        Environment
            Returns an object representing the environment created

        Raises
        ______
        RequiredArgumentMissing
            If any arguments above are not provided.

        """
        # Validate Inputs

        create_dict = {
            "model_id": self.model.id,
        }

        ## Required args
        required_args = ["id", "driver_type", "file_collection_id", "definition_filename"]
        for required_arg in required_args:
            # Add in any values that are
            if required_arg in dictionary:
                create_dict[required_arg] = dictionary[required_arg]
            else:
                # Id creation from filehash
                if required_arg == "id":
                    create_dict[required_arg] = \
                        self._get_filehash(dictionary["definition_filepath"])
                # File setup
                elif required_arg == "file_collection_id":
                    if "definition_filepath" not in dictionary:
                        raise RequiredArgumentMissing("exception.controller.environment_driver.create", {
                            "exception": "Required argument definition_filepath missing to create environment_driver"
                        })
                    #  Create datmo definition file
                    definition_path, definition_filename = os.path.split(dictionary['definition_filepath'])
                    datmo_definition_filepath = os.path.join(definition_path, "datmo" + definition_filename)
                    self.environment_driver.form_datmo_definition_file(input_definition_path=dictionary['definition_filepath'],
                                                                       output_definition_path=datmo_definition_filepath)
                    # Add definition_filepath and datmo_definition_filepath to file_collection
                    filepaths = [dictionary['definition_filepath'], datmo_definition_filepath]
                    create_dict['file_collection_id'] = self.file_driver. \
                        create_collection(filepaths)
                    create_dict['definition_filename'] = definition_filename

        ## Optional args
        optional_args = ["description"]
        for optional_arg in optional_args:
            if optional_arg in dictionary:
                create_dict[optional_arg] = dictionary[optional_arg]


        # Create snapshot and return
        return self.dal.environment.create(create_dict)

    def build(self, id):
        """ Build Environment from definition file

        Parameters
        ----------
        id : str
            Environment object id to build

        Returns
        -------
        bool
            Returns True if success else False

        Raises
        ______
        DoesNotExistException
            If the specified Environment does not exist.

        """
        environment_obj = self.dal.environment.get_by_id(id)
        if not environment_obj:
            raise DoesNotExistException("exception.controller.environment.build", {
                "exception": "Environment does not exist"
            })
        # Build the Environment with the driver
        datmo_definition_filepath = os.path.join(self.file_driver.
                                                 get_collection_path(
            environment_obj.file_collection_id), "datmo" + environment_obj.definition_filename)
        result = self.environment_driver.build_image(id, definition_path=datmo_definition_filepath)
        return result

    def list(self):
        # Get all environment_driver objects for this project
        return self.dal.environment.query({})

    def delete(self, id):
        """ Delete all traces of an Environment

        Parameters
        ----------
        id : str
            Environment object id to remove

        Returns
        -------
        bool
            Returns True if success else False

        Raises
        ______
        DoesNotExistException
            If the specified Environment does not exist.

        """
        environment_obj = self.dal.environment.get_by_id(id)
        if not environment_obj:
            raise DoesNotExistException("exception.environment_driver.docker.delete_environment", {
                "exception": "environment_driver directory does not exist"
            })
        # Remove file collection
        file_collection_deleted = self.file_driver.delete_collection(environment_obj.file_collection_id)
        # Remove images associated with the environment_driver
        image_removed = self.environment_driver.remove_image(id, force=True)
        # Remove running containers associated with environment_driver
        containers_stopped_and_removed = self.environment_driver.\
            stop_remove_containers_by_term(id, force=True)
        # Delete environment_driver object
        delete_success = self.dal.environment.delete(environment_obj.id)

        return file_collection_deleted and image_removed and \
               containers_stopped_and_removed and delete_success

