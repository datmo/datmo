from __future__ import print_function

import os
try:
    basestring
except NameError:
    basestring = str

from datmo.core.util.json_store import JSONStore
from datmo.core.util.exceptions import InvalidArgumentType


class Logger():
    """Logger is a class to enable user to store properties

    Attributes
    ----------
    config : dict
        dictionary containing input or output configs from the run
    results : dict
        dictionary containing output results from the run

    Methods
    -------
    log_config(config)
        Saving the configuration dictionary for the run
    log_results(results)
        Saving the result dictionary for the run

    Raises
    ------
    InvalidArgumentType
    """

    def __init__(self, task_dir="/task"):

        self.task_dir = task_dir

    @classmethod
    def __save_dictionary(self, dictionary, path):
        json_obj = JSONStore(path)
        data = json_obj.to_dict()
        data.update(dictionary)
        json_obj.to_file(data)
        return data

    def log_config(self, config):

        if not isinstance(config, dict):
            raise InvalidArgumentType()

        config_path = os.path.join(self.task_dir, "config.json") \
            if os.path.isdir(self.task_dir) else\
            os.path.join(os.getcwd(), "config.json")

        return self.__save_dictionary(config, config_path)

    def log_result(self, results):
        if not isinstance(results, dict):
            raise InvalidArgumentType()

        results_path = os.path.join(self.task_dir, "stats.json") \
            if os.path.isdir(self.task_dir) else\
            os.path.join(os.getcwd(), "stats.json")

        return self.__save_dictionary(results, results_path)