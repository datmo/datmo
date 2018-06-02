import os
import shutil

from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.util.misc_functions import get_dirhash
from datmo.core.entity.file_collection import FileCollection
from datmo.core.util.exceptions import PathDoesNotExist, EnvironmentInitFailed, FileNotInitialized, UnstagedChanges


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
        self.datmo_file_path = os.path.join(self.home, "datmo_files")
        if not os.path.isdir(self.datmo_file_path):
            os.makedirs(self.datmo_file_path)

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

    def exists(self, file_collection_id=None, file_hash=None):
        """Returns a boolean if the file collection exists

        Parameters
        ----------
        file_collection_id : str
            file collection id to check for
        file_hash : str
            file hash for the file collection to check for

        Returns
        -------
        bool
            True if exists else False

        """
        file_collection_objs = []
        if file_collection_id is not None:
            file_collection_objs = self.dal.file_collection.query({
                "id": file_collection_id
            })
        elif file_hash is not None:
            file_collection_objs = self.dal.file_collection.query({
                "filehash": file_hash
            })
        file_collection_exists = False
        if file_collection_objs:
            file_collection_exists = True
        return file_collection_exists

    def _calculate_datmo_files_hash(self):
        """Return the file hash of the file collections filepaths for `datmo_file`"""
        file_path = os.path.join(self.home, "datmo_files")
        return get_dirhash(file_path)

    def _has_unstaged_changes(self):
        """Return whether there are unstaged changes"""
        file_hash = self._calculate_datmo_files_hash()
        # if file hash is not for empty directory and it already exists in file collection
        if file_hash == 'd41d8cd98f00b204e9800998ecf8427e' or self.exists(file_hash=file_hash):
            return False
        return True

    def check_unstaged_changes(self):
        """Checks if there exists any unstaged changes for the file collection in `datmo_file` folder

        Raises
        ------
        FileNotInitialized
            error if not initialized (must initialize first)

        UnstagedChanges
            error if not there exists unstaged changes in files

        """
        if not self.is_initialized:
            raise FileNotInitialized()

        # Check if unstaged changes exist
        if self._has_unstaged_changes():
            raise UnstagedChanges()

        return True

    def checkout(self, file_collection_id):
        """Checkout to specific file collection id

        Raises
        ------
        FileNotInitialized
            error if not initialized (must initialize first)

        UnstagedChanges
            error if not there exists unstaged changes in files

        """
        if not self.is_initialized:
            raise FileNotInitialized()
        if not self.exists(file_collection_id=file_collection_id):
            raise IOError(
                __("error", "controller.file_collection.checkout_file"))
        # Check if unstaged changes exist
        if self._has_unstaged_changes():
            raise UnstagedChanges()
        # Check if environment has is same as current
        results = self.dal.file_collection.query({
            "id": file_collection_id
        })
        file_collection_obj = results[0]
        file_hash = file_collection_obj.filehash

        if self._calculate_datmo_files_hash() == file_hash:
            return True
        # Remove all content from `datmo_file` folder
        # TODO Use datmo environment path as a class attribute
        for file in os.listdir(self.datmo_file_path):
            file_path = os.path.join(self.datmo_file_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
        # Add in files for that file collection id
        file_collection_path = os.path.join(
            self.home, file_collection_obj.path)
        self.file_driver.copytree(file_collection_path, self.datmo_file_path)
        return True