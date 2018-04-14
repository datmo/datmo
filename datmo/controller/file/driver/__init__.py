from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class FileDriver(with_metaclass(ABCMeta, object)):
    """FileDriver is the parent of all file drivers. Any child must implement the methods below

    Methods
    -------
    init()
        initialize the datmo file structure
    create(relative_path, dir=False)
        create a file or directory
    exists(relative_path, dir=False)
        determine if file or directory exists
    ensure(relative_path, dir=False)
        ensure file or directory exists or create if not
    delete(relative_path, dir=False)
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
        """
        Initialize the datmo file structure

        Returns
        -------
        bool
            True if success

        Raises
        ------
        FileIOException
        """
        pass

    @abstractmethod
    def create(self, relative_path, dir=False):
        """
        create a file or directory

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
    def exists(self, relative_path, dir=False):
        """
        determine if a file or directory exists

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
    def ensure(self, relative_path, dir=False):
        """
        ensure file or directory exists or create if not

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
    def delete(self, relative_path, dir=False):
        """
        delete the file or directory

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

    @abstractmethod
    def create_collection(self, filepaths):
        """
        takes a list of absolute filepaths and aggregates into collection

        Parameters
        ----------
        filepaths : list
            list of strings to absolute paths

        Returns
        -------
        filehash : str
            hash representing the files in the collection
        """
        pass

    @abstractmethod
    def get_collection_path(self, filehash):
        """
        return the collection path by filehash

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
        """
        checks if a collection exists based on filehash

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
    def delete_collection(self, filehash):
        """
        deletes collection based on filehash

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
        """
        transfers collection contents to absolute dst path

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