from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class CodeDriver(with_metaclass(ABCMeta, object)):
    """CodeDriver is the parent of all code drivers. Any child must implement the methods below

    Methods
    -------
    create_ref()
        add remaining files, make a commit and add to datmo ref
    exists_ref()
        check if commit reference exists
    delete_ref()
        delete commit reference if exists
    list_refs()
        list all commit references
    push_ref()
        push commit reference given
    fetch_ref()
        fetch commit reference given
    checkout_ref()
        checkout to commit reference given
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def create_ref(self, commit_id=None):
        """Add remaining files, make a commit and add to datmo ref

        Parameters
        ----------
        commit_id : str, optional
            if commit_id is given, it will not add files and not create a commit

        Returns
        -------
        commit_id : str
            commit_id for the ref created

        Raises
        ------
        GitCommitDoesNotExist
            commit id specified does not match a valid commit within the tree
        """
        pass

    @abstractmethod
    def exists_ref(self, commit_id):
        """Check if commit reference exists

        Parameters
        ----------
        commit_id : str
            commit id specified to check if commit ref exists

        Returns
        -------
        bool
            True if exists else False
        """
        pass

    @abstractmethod
    def delete_ref(self, commit_id):
        """Delete commit ref if exists

        Parameters
        ----------
        commit_id : str
            commit id for commit ref

        Returns
        -------
        bool
            True if success
        """
        pass

    @abstractmethod
    def list_refs(self):
        """List all commit references

        Returns
        -------
        list
            includes all commit ref ids present
        """
        pass

    # @abstractmethod
    # def push_ref(self, commit_id="*"):
    #     """Push commit reference given
    #
    #     Parameters
    #     ----------
    #     commit_id : str, optional
    #         commit id for commit ref (default is * to signify
    #         all refs)
    #
    #     Returns
    #     -------
    #     bool
    #         True if success
    #     """
    #     pass
    #
    # @abstractmethod
    # def fetch_ref(self, commit_id):
    #     """Fetch commit reference given
    #
    #     Parameters
    #     ----------
    #     commit_id : str
    #         commit id for commit ref
    #
    #     Returns
    #     -------
    #     bool
    #         True if success
    #     """
    #     pass

    @abstractmethod
    def checkout_ref(self, commit_id, remote=False):
        """Checkout commit reference given without affecting the .datmo directory

        Parameters
        ----------
        commit_id : str
            commit id for commit ref
        remote : bool
            signifies if commit id should be fetched before checkout

        Returns
        -------
        bool
            True if success
        """
        pass
