import os
import shutil
import pathspec
import tempfile
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.util.misc_functions import list_all_filepaths, dirhash
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
        self._datmo_ignore_filepath = os.path.join(self.filepath,
                                                   ".datmoignore")
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

    def init(self):
        # Create code path if does not exist
        if not os.path.isdir(self._code_filepath):
            os.makedirs(self._code_filepath)
        return True

    def _tracked_files(self):
        """Return list of tracked files relative to the root directory

        This will look through all of the files and will exclude any datmo directories
        (.datmo, datmo_environment/, datmo_files/) and any paths included in .datmoignore

        Returns
        -------
        list
            list of filepaths relative to the the root of the repo
        """
        all_files = set(list_all_filepaths(self.filepath))

        # Ignore the datmo_environment/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch',
                                            ["datmo_environment"])
        datmo_environment_files = set(spec.match_tree(self.filepath))

        # Ignore the datmo_files/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch', ["datmo_files"])
        datmo_files_files = set(spec.match_tree(self.filepath))

        # Load ignored files from .datmoignore file if exists
        datmoignore_files = {".datmoignore"}
        if os.path.isfile(os.path.join(self.filepath, ".datmoignore")):
            with open(self._datmo_ignore_filepath, "r") as f:
                spec = pathspec.PathSpec.from_lines('gitignore', f)
                datmoignore_files.update(set(spec.match_tree(self.filepath)))
        return list(all_files - datmo_environment_files - datmo_files_files -
                    datmoignore_files)

    def _calculate_commit_hash(self, tracked_files):
        """Return the commit hash of the repository"""
        # Move tracked files to temp directory within _code_filepath
        # Hash files and return hash
        temp_dir = tempfile.mkdtemp(dir=self._code_filepath)
        for rel_filepath in tracked_files:
            # Ensure new directory will exist in the temp dir
            filename = os.path.basename(rel_filepath)
            rel_dirpath = rel_filepath.replace(filename, "")
            new_dirpath = os.path.join(temp_dir, rel_dirpath)
            # Ensure directory exists
            if not os.path.isdir(new_dirpath):
                os.makedirs(new_dirpath)
            # Move individual file from old_filepath to new_filepath
            old_filepath = os.path.join(self.filepath, rel_filepath)
            new_filepath = os.path.join(new_dirpath, filename)
            shutil.copy2(old_filepath, new_filepath)
        return dirhash(temp_dir)

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
        # Find all tracked files (_tracked_files)
        # Create the hash of the files (_calculate_commit_hash)
        # Check if the hash already exists with exists_ref
        # Create a new file with the commit hash if it is new, else ERROR (no changes)
        # Loop through the tracked files
        # 1) create folder for each file (use path name from tracked files list) -- if already exists skip
        # 2) hash the file
        # 3) add file with file hash as name to folder for the file (if already exists, will overwrite file -- new ts)
        # 4) add a line into the new file for the commit hash with the following "filepath, filehash"
        # Return commit hash if success else ERROR

        tracked_files = self._tracked_files()
        commit_hash = self._calculate_commit_hash(tracked_files)
        if self.exists_ref(commit_hash):
            return commit_hash

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
