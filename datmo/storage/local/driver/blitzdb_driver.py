from blitzdb import Document
from datetime import datetime

from datmo.util.exceptions import EntityNotFound, \
    EntityCollectionNotFound, IncorrectTypeException
from datmo.storage.local.driver.driver_type import DriverType


class BlitzDBDALDriver():
    def __init__(self, driver_type, connection_string):
        # super().__init__()
        self.database_name = 'datmo_db'

        if driver_type == DriverType.FILE:
            from blitzdb import FileBackend
            self.backend = FileBackend(connection_string)
        else:
            from pymongo import MongoClient
            from blitzdb.backends.mongo import Backend as MongoBackend
            c = MongoClient(connection_string)
            #create a new BlitzDB backend using a MongoDB database
            self.backend = MongoBackend(c[self.database_name])

    class ModelDocument(Document):
        class Meta(Document.Meta):
            collection = 'model'

    class CodeDocument(Document):
        class Meta(Document.Meta):
            collection =  'code'

    class EnvironmentDocument(Document):
        class Meta(Document.Meta):
            collection = 'environment'

    class FileCollectionDocument(Document):
        class Meta(Document.Meta):
            collection = 'file_collection'

    class SessionDocument(Document):
        class Meta(Document.Meta):
            collection = 'session'

    class TaskDocument(Document):
        class Meta(Document.Meta):
            collection = 'task'

    class SnapshotDocument(Document):
        class Meta(Document.Meta):
            collection = 'snapshot'

    class UserDocument(Document):
        class Meta(Document.Meta):
            collection = 'user'

    def get(self, collection, entity_id):
        try:
            results = self.backend.filter(collection, {'pk': entity_id})
            if len(results) == 1:
                item_dict = results[0].attributes
                return normalize_entity(item_dict)
            else:
                raise EntityNotFound()
        except AttributeError as err:
            raise EntityCollectionNotFound(err.message)

    def set(self, collection, obj):
        compatible_obj = denormalize_entity(obj)
        if collection == 'model':
            item = self.ModelDocument(compatible_obj)
        elif collection == 'code':
            item = self.CodeDocument(compatible_obj)
        elif collection == 'environment':
            item = self.EnvironmentDocument(compatible_obj)
        elif collection == 'file_collection':
            item = self.FileCollectionDocument(compatible_obj)
        elif collection == 'session':
            item = self.SessionDocument(compatible_obj)
        elif collection == 'task':
            item = self.TaskDocument(compatible_obj)
        elif collection == 'snapshot':
            item = self.SnapshotDocument(compatible_obj)
        elif collection == 'user':
            item = self.UserDocument(compatible_obj)
        else:
            raise EntityCollectionNotFound()
        self.backend.save(item)
        self.backend.commit()
        return self.get(collection, item.pk)

    def exists(self, collection, entity_id):
        results = self.backend.filter(collection, {'pk': entity_id})
        return len(results) == 1

    def query(self, collection, query_params):
        if query_params.get('id', None) != None:
            query_params['pk'] = query_params['id']
            del query_params['id']
        return list(map(normalize_entity, [item.attributes.copy()
                                           for item in self.backend.filter(collection, query_params)]))

    def delete(self, collection, entity_id):
        results = self.backend.filter(collection, {'pk': entity_id})
        if len(results) == 1:
            document = results[0]
        else:
            raise EntityNotFound()
        self.backend.delete(document)
        self.backend.commit()
        return True

def normalize_entity(in_dict):
    """ Converts BlitzDB Document to standard dictionary

    Arguments:
        [dictionary] -- [BlitzDB Document-compatible dictionary of values]

    Returns:
        [dictionary] -- [normal dictionary of values, output of toDictionary function]
    """
    out_dict = in_dict.copy()
    if 'pk' in list(in_dict):
        out_dict['id'] = in_dict['pk']
        del out_dict['pk']
    if 'created_at' in list(in_dict):
        out_dict['created_at'] = datetime.strptime(in_dict['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if 'updated_at' in list(in_dict):
        out_dict['updated_at'] = datetime.strptime(in_dict['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    return out_dict

def denormalize_entity(in_dict):
    """ Converts standard dictionary to BlitzDB Document-compatible dictionary

    Arguments:
        [dictionary] -- [normal dictionary of values, output of toDictionary function]

    Returns:
        [dictionary] -- [BlitzDB Document-compatible dictionary of values]
    """
    out_dict = in_dict.copy()
    if 'id' in list(in_dict):
        out_dict['pk'] = in_dict['id']
        del out_dict['id']
    if 'created_at' in list(in_dict):
        # if not a datetime object, throw error
        if type(in_dict['created_at']) != datetime:
            raise IncorrectTypeException()
        out_dict['created_at'] = in_dict['created_at'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    if 'updated_at' in list(in_dict):
        # if not a datetime object, throw error
        if type(in_dict['updated_at']) != datetime:
            raise IncorrectTypeException()
        out_dict['updated_at'] = in_dict['updated_at'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return out_dict

