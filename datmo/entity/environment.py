from datetime import datetime


class Environment():
    """
    Environment is an entity object to represent a version of an environment

    Attributes
    ----------
    id : str
    model_id : str
    driver_type : str
    file_collection_id : str
    definition_filename : str
    created_at : datetime
    updated_at : datetime

    """
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.model_id = dictionary['model_id']
        self.driver_type = dictionary['driver_type']

        self.file_collection_id = dictionary['file_collection_id']
        self.definition_filename = dictionary['definition_filename']

        self.description = dictionary.get('description', "")
        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def toDictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = { attr: val
                    for attr, val in attr_dict.items() if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict