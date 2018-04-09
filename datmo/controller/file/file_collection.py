from datmo.util.i18n import get as _
from datmo.controller.base import BaseController
from datmo.util.exceptions import RequiredArgumentMissing, \
    DoesNotExistException


class FileCollectionController(BaseController):
    """FileCollectionController inherits from BaseController and manages business logic related to the
    file system.

    Methods
    -------
    create(filepaths)
        create a file collection within the project
    list()
        list all file collections within the project
    delete(id)
        delete the specified file collection from the project
    """
    def __init__(self, home, dal_driver=None):
        super(FileCollectionController, self).__init__(home, dal_driver)

    def create(self, filepaths):
        """Create a FileCollection

        Parameters
        ----------
        filepaths : list
            list of absolute filepaths to collect

        Returns
        -------
        FileCollection
            an object representing the collection of files

        Raises
        ------
        RequiredArgumentMissing
            if any arguments needed for FileCollection are not provided
        """
        # Validate Inputs

        create_dict = {
            "model_id": self.model.id,
        }

        ## Required args
        required_args = ["id", "path", "driver_type"]
        traversed_args = []
        for required_arg in required_args:
            # Handle Id if provided or not
            if required_arg == "id":
                create_dict[required_arg] = \
                    self.file_driver.create_collection(filepaths)
                traversed_args.append(required_arg)
            elif required_arg == "path":
                create_dict[required_arg] = \
                    self.file_driver.get_collection_path(create_dict['id'])
                traversed_args.append(required_arg)
            elif required_arg == "driver_type":
                create_dict[required_arg] = self.file_driver.type
                traversed_args.append(required_arg)

        # Error if required values not present
        if not traversed_args == required_args:
            raise RequiredArgumentMissing(_("error",
                                            "controller.file_collection.create"))

        # Create file collection and return
        return self.dal.file_collection.create(create_dict)

    def list(self):
        # TODO: Add time filters
        return self.dal.file_collection.query({})

    def delete(self, id):
        """Delete all traces of FileCollection object

        Parameters
        ----------
        id : str
            file collection id to remove

        Returns
        -------
        bool
            returns True if success else False

        Raises
        ------
        DoesNotExistException
            if the specified FileCollection does not exist.
        """
        file_collection_obj = self.dal.file_collection.get_by_id(id)
        if not file_collection_obj:
            raise DoesNotExistException(_("error",
                                          "controller.file_collection.delete",
                                          id))
        # Remove file collection files
        delete_file_collection_success = self.file_driver.delete_collection(id)
        # Delete FileCollection
        delete_file_collection_obj_success = self.dal.file_collection.delete(file_collection_obj.id)

        return delete_file_collection_success and delete_file_collection_obj_success