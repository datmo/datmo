from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.entity.file_collection import FileCollection
from datmo.core.util.exceptions import PathDoesNotExist, EnvironmentInitFailed


class FileCollectionController(BaseController):
    """FileCollectionController inherits from BaseController and manages business logic related to the
    file system.

    Parameters
    ----------
    home : str
        home path of the project

    Methods
    -------
    create(filepaths)
        create a file collection within the project
    list()
        list all file collections within the project
    delete(id)
        delete the specified file collection from the project
    """

    def __init__(self, home):
        try:
            super(FileCollectionController, self).__init__(home)
        except EnvironmentInitFailed:
            self.logger.warning(
                __("warn", "controller.general.environment.failed"))

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
        # TODO: Validate Inputs

        create_dict = {
            "model_id": self.model.id,
        }

        ## Required args for FileCollection entity
        required_args = ["filehash", "path", "driver_type"]
        for required_arg in required_args:
            if required_arg == "filehash":
                create_dict[required_arg] = \
                    self.file_driver.create_collection(filepaths)
                # If file collection with filehash exists, return it
                results = self.dal.file_collection.query({
                    "filehash": create_dict[required_arg]
                })
                if results: return results[0]
            elif required_arg == "path":
                create_dict[required_arg] = \
                    self.file_driver.get_relative_collection_path(create_dict['filehash'])
            elif required_arg == "driver_type":
                create_dict[required_arg] = self.file_driver.type
            else:
                raise NotImplementedError()

        # Create file collection and return
        return self.dal.file_collection.create(FileCollection(create_dict))

    def list(self):
        # TODO: Add time filters
        return self.dal.file_collection.query({})

    def delete(self, file_collection_id):
        """Delete all traces of FileCollection object

        Parameters
        ----------
        file_collection_id : str
            file collection id to remove

        Returns
        -------
        bool
            returns True if success else False

        Raises
        ------
        PathDoesNotExist
            if the specified FileCollection does not exist.
        """
        file_collection_obj = self.dal.file_collection.get_by_id(
            file_collection_id)
        if not file_collection_obj:
            raise PathDoesNotExist(
                __("error", "controller.file_collection.delete",
                   file_collection_id))
        # Remove file collection files
        delete_file_collection_success = self.file_driver.delete_collection(
            file_collection_obj.filehash)
        # Delete FileCollection
        delete_file_collection_obj_success = self.dal.file_collection.delete(
            file_collection_obj.id)

        return delete_file_collection_success and delete_file_collection_obj_success
