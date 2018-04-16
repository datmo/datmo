from datetime import datetime


class FileCollection():
    """
    FileCollection is an entity object to represent a collection of files

    Attributes
    ----------
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    driver_type : str
        the driver class that created the entity
    filehash : str
        hash of file collection contents
    path : str
        path to collection relative to project root
    created_at : datetime, optional
    updated_at : datetime, optional

    """
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.model_id = dictionary['model_id']
        self.driver_type = dictionary['driver_type']

        self.filehash = dictionary['filehash']
        self.path = dictionary['path']

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