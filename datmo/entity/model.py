from datetime import datetime


class Model():
    """
    Model is an entity object that encapsulates other entities

    Attributes
    ----------
    id : str
    name : str
    description : str
    created_at : datetime
    updated_at : datetime

    """
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.name = dictionary['name']
        # TODO: figure out User object and handling of owner in Project
        # self.owner_id = dictionary['owner_id']

        self.description = dictionary.get('description', "")
        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)


        # self.best_snapshot_id = best_snapshot_id
        # self.owner_id = owner_id
        # self.base_model_id = base_model_id
        # self.family_id = family_id

    def __eq__(self, other):
        return self.id == other.id if other else False

    def toDictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = { attr: val
                    for attr, val in attr_dict.items() if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict