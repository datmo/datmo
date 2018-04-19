from datetime import datetime


class Environment():
    """Environment is an entity object to represent a version of an environment

    Attributes
    ----------
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    driver_type : str
        the driver class that created the entity
    definition_filename : str
        definition filename to search for
    hardware_info : dict
        hardware information of the device
    file_collection_id : str
        file collection id to store environment files
    unique_hash : str
        unique hash created from hardware and software info
    description : str, optional
    created_at : datetime, optional
    updated_at : datetime, optional

    """
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.model_id = dictionary['model_id']
        self.driver_type = dictionary['driver_type']

        self.language = dictionary['language']
        self.definition_filename = dictionary['definition_filename']
        self.hardware_info = dictionary['hardware_info']

        self.file_collection_id = dictionary['file_collection_id']
        self.unique_hash = dictionary['unique_hash']

        self.description = dictionary.get('description', "")
        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def to_dictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = { attr: val
                    for attr, val in attr_dict.items() if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict