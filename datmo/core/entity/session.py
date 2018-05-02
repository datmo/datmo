from datetime import datetime


class Session():
    """Session is an entity object to represent a workspace to group tasks and snapshots

    Note
    ----
    All attributes of the class in the ``Attributes`` section must be serializable by the DB

    Parameters
    ----------
    dictionary : dict
        id : str, optional
            the id of the entity
            (default is None; storage driver has not assigned an id yet)
        model_id : str
            the parent model id for the entity
        name : str
            name given by the user at creation
        current : bool, optional
            identifies if the session is the current session
            (default is False, which means not current)
        created_at : datetime.datetime, optional
            (default is datetime.utcnow(), at time of instantiation)
        updated_at : datetime.datetime, optional
            (default is same as created_at, at time of instantiation)

    Attributes
    ----------
    id : str or None
        the id of the entity
    model_id : str
        the parent model id for the entity
    name : str
        name given by the user at creation
    current : bool
        identifies if the session is the current session
    created_at : datetime.datetime
    updated_at : datetime.datetime

    """

    def __init__(self, dictionary):
        self.id = dictionary.get('id', None)
        self.model_id = dictionary['model_id']

        self.name = dictionary['name']

        self.current = dictionary.get('current', False)

        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

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
