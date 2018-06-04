from datetime import datetime


class Environment():
    """Environment is an entity object to represent a version of an environment

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
        driver_type : str
            the driver class that created the entity
        language : str
            programming language used
        definition_filename : str
            definition filename to search for
        hardware_info : dict
            hardware information of the device
        file_collection_id : str
            file collection id to store environment files
        unique_hash : str
            unique hash created from hardware and software info
        name : str, optional
            name of the environment given by the user
            (default is "", blank name)
        description : str, optional
            description of the environment given by user
            (default is "", blank description)
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
    driver_type : str
        the driver class that created the entity
    language : str
        programming language used
    definition_filename : str
        definition filename to search for
    hardware_info : dict
        hardware information of the device
    file_collection_id : str
        file collection id to store environment files
    unique_hash : str
        unique hash created from hardware and software info
    name : str or None
            name of the environment given by the user
    description : str or None
        description of the environment given by user
    created_at : datetime.datetime
    updated_at : datetime.datetime
    """

    def __init__(self, dictionary):
        self.id = dictionary.get('id', None)
        self.model_id = dictionary['model_id']
        self.driver_type = dictionary['driver_type']

        self.definition_filename = dictionary['definition_filename']
        self.hardware_info = dictionary['hardware_info']

        self.file_collection_id = dictionary['file_collection_id']
        self.unique_hash = dictionary['unique_hash']

        self.name = dictionary.get('name', None)
        self.description = dictionary.get('description', None)
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
