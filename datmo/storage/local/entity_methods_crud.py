from datetime import datetime
from datmo.util.exceptions import InputException

class EntityMethodsCRUD(object):
    def __init__(self, collection, entity_class, driver):
        self.collection = collection
        self.entity_class = entity_class
        self.driver = driver

    def get_by_id(self, entity_id):
        obj = self.driver.get(self.collection, entity_id)
        return self.entity_class(obj)

    def create(self, datmo_entity):
        # translate datmo_entity to a standard dictionary (document) to be stored
        if hasattr(datmo_entity,'toDictionary'):
            dict_obj = datmo_entity.toDictionary()
        else:
            dict_obj = datmo_entity
            # set created_at if not present
            dict_obj['created_at'] = dict_obj.get('created_at',
                                                  datetime.now()).utcnow()
        response = self.driver.set(self.collection, dict_obj)
        entity_instance = self.entity_class(response)
        return entity_instance

    def update(self, datmo_entity):
        # translate datmo_entity to a standard dictionary (document) to be stored
        if hasattr(datmo_entity, 'toDictionary'):
            dict_obj = datmo_entity.toDictionary()
        else:
            if 'id' not in datmo_entity.keys() or not datmo_entity['id']:
                raise InputException("exception.local.update", {
                    "exception": "Entity id not provided in the input for update"
                })
            # Aggregate original object and new object into dict_obj var
            new_dict_obj = datmo_entity
            original_datmo_entity = self.get_by_id(datmo_entity['id'])
            dict_obj = {}
            for key, value in original_datmo_entity.toDictionary().iteritems():
                if key in new_dict_obj.keys():
                    dict_obj[key] = new_dict_obj[key]
                else:
                    dict_obj[key] = getattr(original_datmo_entity, key)

            # set updated_at if not present
            dict_obj['updated_at'] = datmo_entity.get('updated_at',
                                                      datetime.now()).utcnow()
        response = self.driver.set(self.collection, dict_obj)
        entity_instance = self.entity_class(response)
        return entity_instance

    def delete(self, entity_id):
        return self.driver.delete(self.collection, entity_id)

    def query(self, query_params):
        return [self.entity_class(item) for item in
                self.driver.query(self.collection, query_params)]