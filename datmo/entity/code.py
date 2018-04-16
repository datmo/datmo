from datetime import datetime


class Code():
    """Code is an entity object to represent a version of source code

    Attributes
    ----------
    id : str
        the id of the entity
    model_id : str
        the parent model id for the entity
    driver_type : str
        the driver class that created the entity
    commit_id : str
    created_at : datetime, optional
    updated_at : datetime, optional

    """
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.model_id = dictionary['model_id']
        self.driver_type = dictionary['driver_type']

        self.commit_id = dictionary['commit_id']

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