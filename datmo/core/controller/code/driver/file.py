import os
import shutil
import errno
import pathspec
import tempfile
import hashlib
import checksumdir
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.util.misc_functions import list_all_filepaths
from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (PathDoesNotExist, FileIOError,
                                        UnstagedChanges, CodeNotInitialized,
                                        CommitDoesNotExist)
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
        self._datmo_directory_name = ".datmo"
        self._datmo_directory_path = os.path.join(self.filepath,
                                                  self._datmo_directory_name)
        self._environment_directory_name = "datmo_environment"
        self._environment_directory_path = os.path.join(
            self.filepath, self._environment_directory_name)
        self._files_directory_name = "datmo_files"
        self._files_directory_path = os.path.join(self.filepath,
                                                  self._files_directory_name)
        self._code_filepath = os.path.join(self._datmo_directory_path, "code")
        self._datmo_ignore_filepath = os.path.join(self.filepath,
                                                   ".datmoignore")
        self._is_initialized = self.is_initialized
        self.type = "file"

    @property
    def is_initialized(self):
        if os.path.isdir(self._datmo_directory_path) and \
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

    def _get_tracked_files(self):
        """Return list of tracked files relative to the root directory

        This will look through all of the files and will exclude any datmo directories
        (.datmo, datmo_environment/, datmo_files/) and any paths included in .datmoignore
        TODO: add general list of directories to ignore here (should be passed in by higher level code)

        Returns
        -------
        list
            list of filepaths relative to the the root of the repo
        """
        all_files = set(list_all_filepaths(self.filepath))

        # Ignore the .datmo/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch',
                                            [self._datmo_directory_name])
        dot_datmo_files = set(spec.match_tree(self.filepath))

        # Ignore the .git/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch', [".git"])
        dot_git_files = set(spec.match_tree(self.filepath))

        # Ignore the datmo_environment/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch',
                                            [self._environment_directory_name])
        datmo_environment_files = set(spec.match_tree(self.filepath))

        # Ignore the datmo_files/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch',
                                            [self._files_directory_name])
        datmo_files_files = set(spec.match_tree(self.filepath))

        # TODO: REMOVE THIS CODE
        # Ignore the datmo_environments/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch',
                                            ["datmo_environments"])
        datmo_snapshots_files = set(spec.match_tree(self.filepath))

        # Ignore the datmo_files/ folder and all contents within it
        spec = pathspec.PathSpec.from_lines('gitwildmatch', ["datmo_files"])
        datmo_tasks_files = set(spec.match_tree(self.filepath))

        # TODO: REMOVE THE ABOVE

        # Load ignored files from .datmoignore file if exists
        datmoignore_files = {".datmoignore"}
        if os.path.isfile(os.path.join(self.filepath, ".datmoignore")):
            with open(self._datmo_ignore_filepath, "r") as f:
                spec = pathspec.PathSpec.from_lines('gitignore', f)
                datmoignore_files.update(set(spec.match_tree(self.filepath)))
        return list(
            all_files - dot_datmo_files - dot_git_files -
            datmo_environment_files - datmo_files_files -
            datmo_snapshots_files - datmo_tasks_files - datmoignore_files)

    def _calculate_commit_hash(self, tracked_files):
        """Return the commit hash of the repository"""
        # Move tracked files to temp directory within _code_filepath
        # Hash files and return hash
        try:
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
            return self._get_dirhash(temp_dir)
        finally:
            try:
                shutil.rmtree(temp_dir)  # delete directory
            except OSError as exc:
                if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
                    raise  # re-raise exception

    @staticmethod
    def _get_filehash(absolute_filepath):
        if not os.path.isfile(absolute_filepath):
            raise PathDoesNotExist(
                __("error", "util.misc_functions.get_filehash",
                   absolute_filepath))
        BUFF_SIZE = 65536
        sha1 = hashlib.md5()
        with open(absolute_filepath, "rb") as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    @staticmethod
    def _get_dirhash(absolute_dirpath):
        return checksumdir.dirhash(absolute_dirpath)

    def _has_unstaged_changes(self):
        """Return whether there are unstaged changes"""
        # TODO: fix circular logic: for empty tracked filepaths, must return "unstaged" until commit is created.
        # TODO: otherwise initial commit will always fail because of no unstaged changes
        tracked_filepaths = self._get_tracked_files()
        commit_hash = self._calculate_commit_hash(tracked_filepaths)
        if self.exists_ref(commit_hash):
            return False
        return True

    def create_ref(self, commit_id=None):
        """Add all files except for those in .datmoignore, and make a commit

        If the commit_id is given, it will return the same commit_id or error

        Parameters
        ----------
        commit_id : str, optional
            if commit_id is given, it will ensure this commit_id exists and not create a new one

        Returns
        -------
        commit_id : str, optional
            if commit_id is given, it will not add files and will not create a commit

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        CommitDoesNotExist
            commit id specified does not match a valid commit
        CommitFailed
            commit could not be created
        """
        if not self.is_initialized:
            raise CodeNotInitialized()
        # If commit is given and it exists then just return it back
        if commit_id:
            if not self.exists_ref(commit_id):
                raise CommitDoesNotExist(
                    __("error",
                       "controller.code.driver.file.create_ref.no_commit",
                       commit_id))
            return commit_id
        # Find all tracked files (_get_tracked_files)
        tracked_filepaths = self._get_tracked_files()
        # Create the hash of the files (_calculate_commit_hash)
        commit_hash = self._calculate_commit_hash(tracked_filepaths)
        # Check if the hash already exists with exists_ref
        if self.exists_ref(commit_hash):
            return commit_hash
        # Create a new file with the commit hash if it is new, else ERROR (no changes)
        commit_filepath = os.path.join(self._code_filepath, commit_hash)
        with open(commit_filepath, "a+") as f:
            # Loop through the tracked files
            for tracked_filepath in tracked_filepaths:
                absolute_filepath = os.path.join(self.filepath,
                                                 tracked_filepath)
                absolute_dirpath = os.path.join(self._code_filepath,
                                                tracked_filepath)
                # 1) create dir for file (use path name from tracked files list) -- if already exists skip
                if not os.path.isdir(absolute_dirpath):
                    os.makedirs(absolute_dirpath)
                # 2) hash the file
                filehash = self._get_filehash(absolute_filepath)
                # 3) add file with file hash as name to folder for the file (if already exists, will overwrite file -- new ts)
                new_absolute_filepath = os.path.join(absolute_dirpath,
                                                     filehash)
                shutil.copy2(absolute_filepath, new_absolute_filepath)
                # 4) append a line into the new file for the commit hash with the following "filepath, filehash"
                f.write(tracked_filepath + "," + filehash + "\n")
        # Return commit hash if success else ERROR
        return commit_hash

    def current_ref(self):
        """Returns the current ref of the code (may not be a commit id, if not saved)

        Returns
        -------
        commit_id : str
            the current commit_id (this may not be a commit id)

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        """
        if not self.is_initialized:
            raise CodeNotInitialized()
        tracked_filepaths = self._get_tracked_files()
        return self._calculate_commit_hash(tracked_filepaths)

    def latest_ref(self):
        """Returns the latest ref of the code

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        """
        if not self.is_initialized:
            raise CodeNotInitialized()

        def getmtime(absolute_filepath):
            # Keeping it granular as timestaps in git
            return int(os.path.getmtime(absolute_filepath))

        # List all files in the code directory (ignore directories)
        for _, _, commit_hashes in os.walk(self._code_filepath):
            sorted_commit_hashes = sorted(
                [
                    os.path.join(self._code_filepath, commit_hash)
                    for commit_hash in commit_hashes
                ],
                key=getmtime,
                reverse=True)
            _, filename = os.path.split(sorted_commit_hashes[0])
            return filename

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

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        """
        if not self.is_initialized:
            raise CodeNotInitialized()
        # List all files in code directory
        commit_hashes = self.list_refs()
        # Check if commit_id exists in the list
        if commit_id in commit_hashes:
            return True
        return False

    def delete_ref(self, commit_id):
        """Removes the commit hash file, but not the file references

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        """
        if not self.is_initialized:
            raise CodeNotInitialized()
        if not self.exists_ref(commit_id):
            raise FileIOError(
                __("error", "controller.code.driver.file.delete_ref"))
        commit_filepath = os.path.join(self._code_filepath, commit_id)
        os.remove(commit_filepath)
        return True

    def list_refs(self):
        """List all commits in repo

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        """
        if not self.is_initialized:
            raise CodeNotInitialized()
        # List all files in the code directory (ignore directories)
        for _, _, commit_hashes in os.walk(self._code_filepath):
            return commit_hashes

    def check_unstaged_changes(self):
        """Checks if there exists any unstaged changes for code. Returns False if it's already staged

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)

        UnstagedChanges
            error if not there exists unstaged changes in environment

        """
        if not self.is_initialized:
            raise CodeNotInitialized()

        # Check if unstaged changes exist
        if self._has_unstaged_changes():
            raise UnstagedChanges()

        return False

    def checkout_ref(self, commit_id):
        """Checkout to specific commit

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        UnstagedChanges
            error if not there exists unstaged changes in code
        """
        if not self.is_initialized:
            raise CodeNotInitialized()
        if not self.exists_ref(commit_id):
            raise FileIOError(
                __("error", "controller.code.driver.file.checkout_ref"))
        # Check if unstaged changes exist
        if self._has_unstaged_changes():
            raise UnstagedChanges()
        # Check if commit given is same as current
        tracked_filepaths = self._get_tracked_files()
        if self._calculate_commit_hash(tracked_filepaths) == commit_id:
            return True
        # Remove all tracked files from repository
        for tracked_filepath in self._get_tracked_files():
            absolute_filepath = os.path.join(self.filepath, tracked_filepath)
            os.remove(absolute_filepath)
        # Add in files from the commit
        commit_filepath = os.path.join(self._code_filepath, commit_id)
        with open(commit_filepath, "r") as f:
            for line in f:
                tracked_filepath, filehash = line.rstrip().split(",")
                source_absolute_filepath = os.path.join(
                    self._code_filepath, tracked_filepath, filehash)
                destination_absolute_filepath = os.path.join(
                    self.filepath, tracked_filepath)
                shutil.copy2(source_absolute_filepath,
                             destination_absolute_filepath)
        return True
