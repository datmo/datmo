from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class FileDriver(with_metaclass(ABCMeta, object)):
    """FileDriver is the parent of all file drivers. Any child must implement the methods below

    Methods
    -------
    init()
        initialize the datmo file structure
    create(relative_path, directory=False)
        create a file or directory
    exists(relative_path, directory=False)
        determine if file or directory exists
    ensure(relative_path, directory=False)
        ensure file or directory exists or create if not
    delete(relative_path, directory=False)
        delete file or directory
    create_collection(filepaths)
        takes a list of absolute filepaths and aggregates into collection
    get_collection_path(filehash)
        return the collection path by filehash
    exists_collection(filehash)
        checks if a collection exists based on filehash
    delete_collection(filehash)
        deletes collection based on filehash
    transfer_collection(filehash, dst_dirpath)
        transfers collection contents to absolute dst path
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def init(self):
        """Initialize the datmo file structure

        Returns
        -------
        bool
            True if success

        Raises
        ------
        FileIOError
        """
        pass

    @abstractmethod
    def create(self, relative_path, directory=False):
        """Create a file or directory

        Parameters
        ----------
        relative_path : str
            path relative to the filepath
        dir : bool
            True if directory else file

        Returns
        -------
        str
            absolute filepath to the file or directory
        """
        pass

    @abstractmethod
    def exists(self, relative_path, directory=False):
        """Determine if a file or directory exists

        Parameters
        ----------
        relative_path : str
            path relative to the filepath
        dir : bool
            True if directory else file

        Returns
        -------
        bool
            True if exists else False
        """
        pass

    @abstractmethod
    def get(self, relative_path, mode="r", directory=False):
        """Retrieve file as python file object

        Parameters
        ----------
        relative_path : str
            path relative to the filepath
        mode : str
            file object open mode
        dir : bool
            True if directory else file

        Returns
        -------
        file
            python file object representing file opened
            in the mode specified
        """

    @abstractmethod
    def ensure(self, relative_path, directory=False):
        """Ensure file or directory exists or create if not

        Parameters
        ----------
        relative_path : str
            path relative to the filepath
        dir : bool
            True if directory else file

        Returns
        -------
        bool
            True if exists
        """
        pass

    @abstractmethod
    def delete(self, relative_path, directory=False):
        """Delete the file or directory

        Parameters
        ----------
        relative_path : str
            path relative to the filepath
        dir : bool
            True if directory else file

        Returns
        -------
        bool
            True if successfully deleted
        """
        pass

    @staticmethod
    @abstractmethod
    def get_filehash(filepath):
        """Return the hash of the file path given

        Parameters
        ----------
        filepath : str
            path of the file

        Returns
        -------
        str
            unique hash of the file
        """

    @staticmethod
    @abstractmethod
    def get_dirhash(dirpath):
        """Return the hash of the directory path given

        Parameters
        ----------
        dirpath : str
            path of the directory

        Returns
        -------
        str
            unique hash of the directory
        """

    @abstractmethod
    def create_collection(self, paths):
        """Takes a list of user given paths and aggregates into collection

        Parameters
        ----------
        paths : list, optional
            list of absolute or relative filepaths and/or dirpaths to collect with destination names
            (e.g. "/path/to/file>hello", "/path/to/file2", "/path/to/dir>newdir")

        Returns
        -------
        filehash : str
            hash representing the files in the collection
        """
        pass

    @abstractmethod
    def calculate_hash_paths(self, paths, directory):
        """Takes a list of user given paths, copies to directory, and returns hash

        Parameters
        ----------
        paths : list
            list of absolute or relative filepaths and/or dirpaths to collect with destination names
            (e.g. "/path/to/file>hello", "/path/to/file2", "/path/to/dir>newdir")
        directory : str
            directory to aggregate paths

        Returns
        -------
        str
            hash of all of the paths in a directory
        """

    @abstractmethod
    def get_collection_path(self, filehash):
        """Return the collection path by filehash

        Parameters
        ----------
        filehash : str
            hash representing the files in the collection

        Returns
        -------
        str
            absolute path to the collection
        """
        pass

    @abstractmethod
    def exists_collection(self, filehash):
        """Checks if a collection exists based on filehash

        Parameters
        ----------
        filehash : str
            hash representing the files in the collection

        Returns
        -------
        bool
            True if exists else False
        """
        pass

    @abstractmethod
    def get_collection_files(self, filehash, mode="r"):
        """Retrieve collection files as python file object

        Parameters
        ----------
        filehash : str
            hash representing the files in the collection
        mode : str
            file object open mode

        Returns
        -------
        list
            list of python file objects representing each
            file in the collection opened in mode specified
        """

    @abstractmethod
    def delete_collection(self, filehash):
        """Deletes collection based on filehash

        Parameters
        ----------
        filehash : str
            hash representing the files in the collection

        Returns
        -------
        bool
            True if successfully deleted
        """
        pass

    @abstractmethod
    def transfer_collection(self, filehash, dst_dirpath):
        """Transfers collection contents to absolute dst path

        Parameters
        ----------
        filehash : str
            hash representing the files in the collection
        dst_dirpath : str
            absolute filepath to copy collection contents to

        Returns
        -------
        bool
            True if successful
        """
        pass