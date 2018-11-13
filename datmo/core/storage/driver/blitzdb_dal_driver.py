from blitzdb import Document, queryset
from datetime import datetime

from datmo.core.util.exceptions import (
    EntityNotFound, EntityCollectionNotFound, IncorrectType,
    InvalidArgumentType, RequiredArgumentMissing, MoreThanOneEntityFound)
from datmo.core.storage.driver import DALDriver


class BlitzDBDALDriver(DALDriver):
    def __init__(self, driver_type, connection_string):
        super(BlitzDBDALDriver, self).__init__()
        self.database_name = 'datmo_db'
        self.driver_type = driver_type
        self.connection_string = connection_string
        if self.driver_type == "file":
            from blitzdb import FileBackend
            self.backend = FileBackend(self.connection_string)
        elif self.driver_type == "mongo":
            from pymongo import MongoClient
            from blitzdb.backends.mongo import Backend as MongoBackend
            c = MongoClient(self.connection_string)
            #create a new BlitzDB backend using a MongoDB database
            self.backend = MongoBackend(c[self.database_name])

    class ModelDocument(Document):
        class Meta(Document.Meta):
            collection = 'model'

    class CodeDocument(Document):
        class Meta(Document.Meta):
            collection = 'code'

    class EnvironmentDocument(Document):
        class Meta(Document.Meta):
            collection = 'environment'

    class FileCollectionDocument(Document):
        class Meta(Document.Meta):
            collection = 'file_collection'

    class TaskDocument(Document):
        class Meta(Document.Meta):
            collection = 'task'

    class SnapshotDocument(Document):
        class Meta(Document.Meta):
            collection = 'snapshot'

    class UserDocument(Document):
        class Meta(Document.Meta):
            collection = 'user'

    def __reload(self):
        if hasattr(self.backend, "indexes"):
            for _, nested_index in self.backend.indexes.items():
                for index, _ in nested_index.items():
                    # Only load from store if storage exists
                    if nested_index[index]._store:
                        nested_index[index].load_from_store()
            self.__init__(self.driver_type, self.connection_string)

    def get(self, collection, entity_id):
        self.__reload()
        try:
            results = self.backend.filter(collection, {'pk': entity_id})
            if len(results) == 1:
                item_dict = results[0].attributes
                return normalize_entity(item_dict)
            else:
                raise EntityNotFound()
        except AttributeError as err:
            raise EntityCollectionNotFound(err.message)

    def get_by_shortened_id(self, collection, shortened_entity_id):
        self.__reload()
        try:
            results = self.backend.filter(
                collection, {'pk': {
                    '$regex': '^%s' % shortened_entity_id
                }})
            if len(results) == 1:
                item_dict = results[0].attributes
                return normalize_entity(item_dict)
            elif len(results) > 1:
                raise MoreThanOneEntityFound()
            else:
                raise EntityNotFound()
        except AttributeError as err:
            raise EntityCollectionNotFound(err.message)

    def set(self, collection, obj):
        self.__reload()
        compatible_obj = denormalize_entity(obj)
        if collection == 'model':
            item = self.ModelDocument(compatible_obj)
        elif collection == 'code':
            item = self.CodeDocument(compatible_obj)
        elif collection == 'environment':
            item = self.EnvironmentDocument(compatible_obj)
        elif collection == 'file_collection':
            item = self.FileCollectionDocument(compatible_obj)
        elif collection == 'task':
            item = self.TaskDocument(compatible_obj)
        elif collection == 'snapshot':
            item = self.SnapshotDocument(compatible_obj)
        elif collection == 'user':
            item = self.UserDocument(compatible_obj)
        else:
            raise EntityCollectionNotFound(collection)
        self.backend.save(item)
        self.backend.commit()
        return self.get(collection, item.pk)

    def exists(self, collection, entity_id):
        self.__reload()
        results = self.backend.filter(collection, {'pk': entity_id})
        return len(results) == 1

    def query(self, collection, query_params, sort_key=None, sort_order=None):
        self.__reload()
        if query_params.get('id', None) is not None:
            query_params['pk'] = query_params['id']
            del query_params['id']
        if sort_key is not None and sort_order is not None:
            if sort_order == 'ascending':
                return list(
                    map(normalize_entity, [
                        item.attributes.copy() for item in self.backend.filter(
                            collection, query_params).sort(
                                sort_key, queryset.QuerySet.ASCENDING)
                    ]))
            elif sort_order == 'descending':
                return list(
                    map(normalize_entity, [
                        item.attributes.copy() for item in self.backend.filter(
                            collection, query_params).sort(
                                sort_key, queryset.QuerySet.DESCENDING)
                    ]))
            else:
                raise InvalidArgumentType()
        else:
            if sort_key is not None and sort_order is None or \
                sort_key is None and sort_order is not None:
                raise RequiredArgumentMissing()
            return list(
                map(normalize_entity, [
                    item.attributes.copy()
                    for item in self.backend.filter(collection, query_params)
                ]))

    def delete(self, collection, entity_id):
        self.__reload()
        results = self.backend.filter(collection, {'pk': entity_id})
        if len(results) == 1:
            document = results[0]
        else:
            raise EntityNotFound()
        self.backend.delete(document)
        self.backend.commit()
        return True


def normalize_entity(in_dict):
    """Converts BlitzDB Document to standard dictionary

    Parameters
    ----------
    in_dict : dict
        BlitzDB Document-compatible dictionary of values

    Returns
    -------
    dict
        normal dictionary of values, output of to_dictionary function
    """
    out_dict = in_dict.copy()
    if 'pk' in list(in_dict):
        out_dict['id'] = in_dict['pk']
        del out_dict['pk']
    if 'start_time' in list(in_dict):
        out_dict['start_time'] = \
            datetime.strptime(in_dict['start_time'], '%Y-%m-%dT%H:%M:%S.%fZ') \
                if out_dict['start_time'] else None
    if 'end_time' in list(in_dict):
        out_dict['end_time'] = \
            datetime.strptime(in_dict['end_time'], '%Y-%m-%dT%H:%M:%S.%fZ') \
                if out_dict['end_time'] else None
    if 'created_at' in list(in_dict):
        out_dict['created_at'] = datetime.strptime(in_dict['created_at'],
                                                   '%Y-%m-%dT%H:%M:%S.%fZ')
    if 'updated_at' in list(in_dict):
        out_dict['updated_at'] = datetime.strptime(in_dict['updated_at'],
                                                   '%Y-%m-%dT%H:%M:%S.%fZ')
    return out_dict


def denormalize_entity(in_dict):
    """Converts standard dictionary to BlitzDB Document-compatible dictionary

    Parameters
    ----------
    in_dict : dict
        normal dictionary of values, output of to_dictionary function

    Returns
    -------
    dict
        BlitzDB Document-compatible dictionary of values
    """
    out_dict = in_dict.copy()
    if 'id' in list(in_dict):
        out_dict['pk'] = in_dict['id']
        del out_dict['id']
    if 'start_time' in list(in_dict):
        # if not a datetime object, throw error
        if in_dict['start_time'] and not isinstance(in_dict['start_time'],
                                                    datetime):
            raise IncorrectType()
        out_dict['start_time'] = \
            in_dict['start_time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ') \
                if in_dict['start_time'] else None
    if 'end_time' in list(in_dict):
        # if not a datetime object, throw error
        if in_dict['end_time'] and not isinstance(in_dict['end_time'],
                                                  datetime):
            raise IncorrectType()
        out_dict['end_time'] = \
            in_dict['end_time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ') \
                if in_dict['end_time'] else None
    if 'created_at' in list(in_dict):
        # if not a datetime object, throw error
        if not isinstance(in_dict['created_at'], datetime):
            raise IncorrectType()
        out_dict['created_at'] = in_dict['created_at'].strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')
    if 'updated_at' in list(in_dict):
        # if not a datetime object, throw error
        if not isinstance(in_dict['updated_at'], datetime):
            raise IncorrectType()
        out_dict['updated_at'] = in_dict['updated_at'].strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')
    return out_dict
