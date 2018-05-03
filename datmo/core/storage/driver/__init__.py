from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class DALDriver(with_metaclass(ABCMeta, object)):
    """DALDriver is the parent of all dal drivers. Any child must implement the methods below

    Methods
    -------
    get(collection, entity_id)
        get entity object from collection
    set(collection, obj)
        create entity object in collection
    exists(collection, entity_id)
        checks if entity exists in collection
    query(collection, query_params)
        find entities in collection matching params
    delete(collection, entity_id)
        delete entity from collection
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get(self, collection, entity_id):
        """
        get entity object from collection

        Parameters
        ----------
        collection : str
            name of the collection
        entity_id : str
            id of entity in collection

        Returns
        -------
        dict
            normalized python representation of entity
        """
        pass

    @abstractmethod
    def set(self, collection, obj):
        """
        create entity object in collection

        Parameters
        ----------
        collection : str
            name of the collection
        obj : dict
            normalized python representation of entity to save

        Returns
        -------
        dict
            normalized python representation of entity
        """
        pass

    @abstractmethod
    def exists(self, collection, entity_id):
        """
        checks if entity exists in collection

        Parameters
        ----------
        collection : str
            name of the collection
        entity_id : str
            id of the entity in the collection

        Returns
        -------
        bool
            True if exists else False
        """
        pass

    @abstractmethod
    def query(self, collection, query_params):
        """
        find entities in collection matching params

        Parameters
        ----------
        collection : str
            name of the collection
        query_params : dict
            query dictionary for driver

        Returns
        -------
        list
            list of dictionaries of normalized python
            representations of the entities
        """
        pass

    @abstractmethod
    def delete(self, collection, entity_id):
        """
        delete entity from collection

        Parameters
        ----------
        collection : str
            name of the collection
        entity_id : str
            id of the entity in the collection

        Returns
        -------
        bool
            True if successful delete
        """
        pass
