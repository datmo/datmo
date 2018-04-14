from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class CodeDriver(with_metaclass(ABCMeta, object)):
    """CodeDriver is the parent of all code drivers. Any child must implement the methods below

    Methods
    -------
    create_code()
        create code reference
    exists_code()
        check if code reference exists
    delete_code()
        delete code reference if exists
    list_code()
        list all code references
    push_code()
        push code reference given
    fetch_code()
        fetch code reference given
    checkout_code()
        checkout to code reference given
    """
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def create_code(self, code_id=None):
        pass

    @abstractmethod
    def exists_code(self, code_id):
        pass

    @abstractmethod
    def delete_code(self, code_id):
        pass

    @abstractmethod
    def list_code(self):
        pass

    @abstractmethod
    def push_code(self, code_id="*"):
        pass

    @abstractmethod
    def fetch_code(self, code_id):
        pass

    @abstractmethod
    def checkout_code(self, code_id, remote=False):
        pass