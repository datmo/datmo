"""
# https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
"""
import importlib


def get_class_contructor(class_location):
    mod_path = class_location[:class_location.rfind('.')]
    class_name = class_location[class_location.rfind('.') + 1:]
    module = importlib.import_module(mod_path)
    # return class constructor
    return getattr(module, class_name)
