import os
from datetime import datetime

from datmo.core.util.json_store import JSONStore
from datmo.core.util.misc_functions import prettify_datetime, printable_object, format_table


class Snapshot():
    """Snapshot is an entity object to represent a version of the model. These snapshots
    are the building blocks upon which models can be shared, deployed, and reproduced.

    Snapshots consist of 5 main components which are represented as well in the attributes
    listed below

    1) Source code
    2) Dependency environment
    3) Large files not included in source code
    4) Configurations of your model, features, data, etc
    5) Performance metrics that evaluate your model

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
        message : str
            long description of snapshot
        code_id : str
            code reference associated with the snapshot
        environment_id : str
            id for environment used to create snapshot
        file_collection_id : str
            file collection associated with the snapshot
        config : dict
            key, value pairs of configurations
        stats : dict
            key, value pairs of metrics and statistics
        task_id : str, optional
            task id associated with snapshot
            (default is None, means no task_id set)
        label : str, optional
            short description of snapshot
            (default is None, means no label set)
        visible : bool, optional
            True if visible to user via list command else False
            (default is True to show users unless otherwise specified)
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
    message : str
        long description of snapshot
    code_id : str
        code reference associated with the snapshot
    environment_id : str
        id for environment used to create snapshot
    file_collection_id : str
        file collection associated with the snapshot
    config : dict
        key, value pairs of configurations
    stats : dict
        key, value pairs of metrics and statistics
    task_id : str or None
        task id associated with snapshot
    label : str or None
        short description of snapshot
    visible : bool
        True if visible to user via list command else False
    created_at : datetime.datetime
    updated_at : datetime.datetime
    """

    def __init__(self, dictionary):
        self.id = dictionary.get('id', None)
        self.model_id = dictionary['model_id']
        self.message = dictionary['message']

        self.code_id = dictionary['code_id']
        self.environment_id = dictionary['environment_id']
        self.file_collection_id = dictionary['file_collection_id']
        self.config = dictionary['config']
        self.stats = dictionary['stats']

        self.task_id = dictionary.get('task_id', None)
        self.label = dictionary.get('label', None)
        self.visible = dictionary.get('visible', True)

        self.created_at = dictionary.get('created_at', datetime.utcnow())
        self.updated_at = dictionary.get('updated_at', self.created_at)

    def __eq__(self, other):
        return self.id == other.id if other else False

    def __str__(self):
        if self.label:
            final_str = '\033[94m' + "snapshot " + self.id + '\033[0m'
            final_str = final_str + '\033[94m' + " (" + '\033[0m'
            final_str = final_str + '\033[93m' + '\033[1m' + "label: " + self.label + '\033[0m'
            final_str = final_str + '\033[94m' + ")" + '\033[0m' + os.linesep
        else:
            final_str = '\033[94m' + "snapshot " + self.id + '\033[0m' + os.linesep
        final_str = final_str + "Date: " + prettify_datetime(
            self.created_at) + os.linesep
        table_data = []
        if self.task_id:
            table_data.append(["Task", "-> " + self.task_id])
        table_data.append(["Visible", "-> " + str(self.visible)])
        # Components
        table_data.append(["Code", "-> " + self.code_id])
        table_data.append(["Environment", "-> " + self.environment_id])
        table_data.append(["Files", "-> " + self.file_collection_id])
        table_data.append(["Config", "-> " + str(self.config)])
        table_data.append(["Stats", "-> " + str(self.stats)])
        final_str = final_str + format_table(table_data)
        final_str = final_str + os.linesep + "    " + self.message + os.linesep + os.linesep
        return final_str

    def __repr__(self):
        return self.__str__()

    def save_config(self, filepath):
        JSONStore(os.path.join(filepath, 'config.json'), self.config)
        return

    def save_stats(self, filepath):
        JSONStore(os.path.join(filepath, 'stats.json'), self.stats)
        return

    def to_dictionary(self, stringify=False):
        attr_dict = self.__dict__
        pruned_attr_dict = {
            attr: val
            for attr, val in attr_dict.items()
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        if stringify:
            for key in ["config", "stats", "message", "label"]:
                pruned_attr_dict[key] = printable_object(pruned_attr_dict[key])
            for key in ["created_at", "updated_at"]:
                pruned_attr_dict[key] = prettify_datetime(
                    pruned_attr_dict[key])
        return pruned_attr_dict
