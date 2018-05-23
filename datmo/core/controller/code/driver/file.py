import os
import shutil
import subprocess
import semver
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from giturlparse import parse

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (PathDoesNotExist)
from datmo.core.controller.code.driver import CodeDriver


class FileCodeDriver(CodeDriver):
    """File-based Code Driver handles source control management for the project with files
    """

    def __init__(self, filepath):
        super(FileCodeDriver, self).__init__()
        self.filepath = filepath
        # Check if filepath exists
        if not os.path.exists(self.filepath):
            raise PathDoesNotExist(
                __("error", "controller.code.driver.git.__init__.dne",
                   filepath))
        self._datmo_filepath = os.path.join(self.filepath, ".datmo")
        self._code_filepath = os.path.join(self._datmo_filepath, "code")
        self._is_initialized = self.is_initialized
        self.type = "file"

    @property
    def is_initialized(self):
        if os.path.isdir(self._datmo_filepath) and \
            os.path.isdir(self._code_filepath):
            self._is_initialized = True
            return self._is_initialized
        self._is_initialized = False
        return self._is_initialized

    def _tracked_files(self):
        """Return list of tracked files relative to the root directory

        This will look through all of the files and will exclude any datmo directories
        (.datmo, datmo_environment/, datmo_files/) and any paths included in .datmoignore
        """
        pass

    def _calculate_hash(self, tracked_files):
        """Return the hash of all the files that are to be changed"""
        # Move tracked files to temp directory within _code_filepath
        # Hash files and return hash
        pass

    def create_ref(self, commit_id=None):
        """Add all files except for those in .datmoignore, and make a commit

        If the commit_id is given, it will return the same commit_id or error

        Parameters
        ----------
        commit_id : str, optional
            if commit_id is given, it will ensure this commit_id exists and not create a new one

        Returns
        -------
        commit_id : str
            commit id for ref created

        Raises
        ------
        CommitDoesNotExist
            commit id specified does not match a valid commit
        """
        # Find all tracked files
        # Create the hash of the files
        # Check if the hash already exists with exists_ref
        # Create a new file with the commit hash if it is new
        # Loop through the tracked files
        # 1) create folder for each file (use path name from tracked files list) -- if already exists skip
        # 2) hash the file and check if already exists in the folder
        # 3) if doesn't exist in the folder then add file with file hash as name to folder for the file
        # 4) add a line into the new file for the commit hash with the following (filepath, filehash)
        # Return commit hash if success else ERROR
        pass

    def exists_ref(self, commit_id):
        """Returns a boolean if the commit exists

        Parameters
        ----------
        commit_id : str
            commit id to check for

        Returns
        -------
        bool
            True if exists else False
        """
        pass

    def delete_ref(self, commit_id):
        pass

    def list_refs(self):
        pass

    def checkout_ref(self, commit_id):
        pass
