import os
from datetime import datetime
from datmo.util.file_storage import JSONKeyValueStore


class Snapshot():
    def __init__(self, dictionary):
        self.id = dictionary['id']
        self.model_id = dictionary['model_id']

        self.code_id = dictionary['code_id']
        self.environment_id = dictionary['environment_id']
        self.file_collection_id = dictionary['file_collection_id']
        self.config = dictionary['config']
        self.stats = dictionary['stats']

        self.session_id = dictionary.get('session_id', "")
        # self.task_id = dictionary.get('task_id', None)

        self.message = dictionary.get('message', "")
        self.label = dictionary.get('label', "")

        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def save_config(self, filepath):
        JSONKeyValueStore(os.path.join(filepath, 'config.json'),
                          self.config)
        return

    def save_stats(self, filepath):
        JSONKeyValueStore(os.path.join(filepath, 'stats.json'),
                          self.stats)
        return

    def toDictionary(self):
        attr_dict = self.__dict__
        pruned_attr_dict = { attr: val
                    for attr, val in attr_dict.iteritems() if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        return pruned_attr_dict


