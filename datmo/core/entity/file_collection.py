from datetime import datetime

class FileCollection():
    """FileCollection is an entity object to represent a collection of files

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
        filehash : str
            hash of file collection contents
        path : str
            path to collection relative to project root
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
    filehash : str
        hash of file collection contents
    path : str
        path to collection relative to project root
    file_path_map: list
        list of tuple, mapping the source absolute file path to destination relative file path
    directory_path_map: list
        list of tuple, mapping the source absolute directory path to destination relative directory path
    created_at : datetime.datetime
    updated_at : datetime.datetime
    """

    def __init__(self, dictionary):
        self.id = dictionary.get('id', None)
        self.model_id = dictionary['model_id']
        self.driver_type = dictionary['driver_type']

        self.filehash = dictionary['filehash']
        self.path = dictionary['path']

        self.file_path_map = dictionary.get('file_path_map', None)
        self.directory_path_map = dictionary.get('directory_path_map', None)

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
