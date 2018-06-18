from datetime import datetime


class Model():
    """Model is an entity object that encapsulates other entities

    Note
    ----
    All attributes of the class in the ``Attributes`` section must be serializable by the DB

    Parameters
    ----------
    dictionary : dict
        id : str, optional
            the id of the entity
            (default is None; storage driver has not assigned an id yet)
        name : str, optional
            name given by the user at creation
            (default is None, which means no name set)
        description : str, optional
            description given by the user at creation
            (default is None, which means no description set)
        created_at : datetime.datetime, optional
            (default is datetime.utcnow(), at time of instantiation)
        updated_at : datetime.datetime, optional
            (default is same as created_at, at time of instantiation)

    Attributes
    ----------
    id : str or None
        the id of the entity
    name : str or None
        name given by the user at creation
    description : str or None
        description given by the user at creation
    created_at : datetime.datetime
    updated_at : datetime.datetime
    """

    def __init__(self, dictionary):
        self.id = dictionary.get('id', None)
        self.name = dictionary.get('name', None)
        # TODO: figure out User object and handling of owner in Project
        # self.owner_id = dictionary['owner_id']

        self.description = dictionary.get('description', None)
        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

        # self.best_snapshot_id = best_snapshot_id
        # self.owner_id = owner_id
        # self.base_model_id = base_model_id
        # self.family_id = family_id

    def __eq__(self, other):
        return self.id == other.id if other else False

    def to_dictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = {
            attr: val
            for attr, val in attr_dict.items()
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict
