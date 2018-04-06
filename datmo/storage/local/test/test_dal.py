"""
Tests for Datmo Local
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import shutil
import tempfile
from datetime import datetime

from datmo.storage.local.driver.blitzdb_driver import BlitzDBDataDriver
from datmo.storage.local.driver.driver_type import DriverType
from datmo.storage.local.dal import LocalDAL
from datmo.util.exceptions import EntityNotFound, EntityCollectionNotFound

class TestLocalDAL():
    def setup_class(self):
        self.temp_dir = tempfile.mkdtemp()
        self.datadriver = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)

    def teardown_class(self):
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        dal = LocalDAL(self.datadriver)
        assert dal != None

    def test_get_by_id_unknown_entity(self):
        exp_thrown = False
        dal = LocalDAL(self.datadriver)
        try:
            dal.model.get_by_id('not_found')
        except EntityNotFound:
            exp_thrown = True
        except EntityCollectionNotFound:
            exp_thrown = True
        assert exp_thrown

    def test_property_cache(self):
        """
        Ensures kids.cache caches all DatmoEntityMethod wrapped objects
        """
        dal = LocalDAL(self.datadriver)
        model_methods_1 = dal.model
        model_methods_2 = dal.model
        assert model_methods_1 == model_methods_2

    # Model

    def test_create_model_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        assert model.name == model_name
        assert model.created_at
        assert model.updated_at

    def test_get_by_id_model(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_2'
        model = dal.model.create({'name': model_name})
        result = dal.model.get_by_id(model.id)
        assert model.id == result.id

    def test_get_by_id_model_same_dir(self):
        test_dir = 'test-dir'
        datadriver = BlitzDBDataDriver(DriverType.FILE, test_dir)
        dal = LocalDAL(datadriver)
        model1 = dal.model.create({'name': "test"})
        del datadriver
        del dal
        datadriver = BlitzDBDataDriver(DriverType.FILE, test_dir)
        dal = LocalDAL(datadriver)
        model2 = dal.model.create({'name': "test"})
        del datadriver
        del dal
        datadriver = BlitzDBDataDriver(DriverType.FILE, test_dir)
        dal = LocalDAL(datadriver)
        model3 = dal.model.create({'name': "test"})

        model1 = dal.model.get_by_id(model1.id)
        model2 = dal.model.get_by_id(model2.id)
        model3 = dal.model.get_by_id(model3.id)

        assert model1
        assert model2
        assert model3

        shutil.rmtree(test_dir)

    def test_get_by_id_model_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_3'
        model = dal.model.create({'name': model_name})
        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.model.get_by_id(model.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_model = new_dal_instance.model.get_by_id(model.id)
        assert new_model.id == model.id

    def test_update_model(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_4'
        model = dal.model.create({'name': model_name})

        # Update required and optional parameters
        updated_model_name = 'model_4a'
        updated_model_description = "this is a cool model"
        updated_model = dal.model.update({
            'id': model.id,
            'name': updated_model_name,
            'description': updated_model_description
        })
        assert model.id == updated_model.id and \
            model.updated_at < updated_model.updated_at and \
            updated_model.name == updated_model_name and \
            updated_model.description == updated_model_description


    def test_delete_model(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_4'
        model = dal.model.create({'name': model_name})

        dal.model.delete(model.id)

        deleted = False
        try:
            dal.model.get_by_id(model.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_models(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_5'
        model = dal.model.create({'name': model_name})
        assert len(dal.model.query({'id': model.id})) == 1
        assert len(dal.model.query({'name': model_name})) == 1

    # Code

    def test_create_code_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        code_id = 'id_1'
        code_driver_type = 'git'
        code = dal.code.create({
            'id': code_id,
            'model_id': model.id,
            'driver_type': code_driver_type
        })

        assert code.id == code_id
        assert code.driver_type == code_driver_type
        assert code.created_at
        assert code.updated_at

    def test_get_by_id_code(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        code_id = 'id_2'
        code_driver_type = 'git'
        code = dal.code.create({
            'id': code_id,
            'model_id': model.id,
            'driver_type': code_driver_type
        })

        result = dal.code.get_by_id(code.id)
        assert code.id == result.id

    def test_get_by_id_code_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        code_id = 'id_3'
        code_driver_type = 'git'
        code = dal.code.create({
            'id': code_id,
            'model_id': model.id,
            'driver_type': code_driver_type
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.code.get_by_id(code.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_code = new_dal_instance.code.get_by_id(code.id)
        assert new_code.id == code.id

    def test_update_code(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        code_id = 'id_4'
        code_driver_type = 'git'
        code = dal.code.create({
            'id': code_id,
            'model_id': model.id,
            'driver_type': code_driver_type
        })

        # Update required and optional parameters
        updated_code_driver_type = 'new_driver'
        updated_code_created_at = datetime.utcnow()
        updated_code = dal.code.update({
            'id': code.id,
            'driver_type': updated_code_driver_type,
            'created_at': updated_code_created_at
        })
        assert code.id == updated_code.id and \
               code.updated_at < updated_code.updated_at and \
               updated_code.driver_type == updated_code_driver_type and \
               updated_code.created_at == updated_code_created_at

    def test_delete_code(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        code_id = 'id_5'
        code_driver_type = 'git'
        code = dal.code.create({
            'id': code_id,
            'model_id': model.id,
            'driver_type': code_driver_type
        })

        dal.code.delete(code.id)
        deleted = False
        try:
            dal.code.get_by_id(code.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_codes(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        code_id = 'id_5'
        code_driver_type = 'git'
        code = dal.code.create({
            'id': code_id,
            'model_id': model.id,
            'driver_type': code_driver_type
        })

        assert len(dal.code.query({'id': code.id})) == 1

    # Environment
    # TODO: Add tests for other variables once figured out.

    def test_create_environment_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        environment_id = 'id_1'
        environment_driver_type = 'docker'
        environment_file_collection_id = 'test_file_id'
        environment_definition_filename = 'Dockerfile'
        environment = dal.environment.create({
            'id': environment_id,
            'model_id': model.id,
            'driver_type': environment_driver_type,
            'file_collection_id': environment_file_collection_id,
            'definition_filename': environment_definition_filename
        })

        assert environment.id == environment_id
        assert environment.driver_type == environment_driver_type
        assert environment.file_collection_id == environment_file_collection_id
        assert environment.definition_filename == environment_definition_filename
        assert environment.created_at
        assert environment.updated_at

    def test_get_by_id_environment(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        environment_id = 'id_2'
        environment_driver_type = 'docker'
        environment_file_collection_id = 'test_file_id'
        environment_definition_filename = 'Dockerfile'
        environment = dal.environment.create({
            'id': environment_id,
            'model_id': model.id,
            'driver_type': environment_driver_type,
            'file_collection_id': environment_file_collection_id,
            'definition_filename': environment_definition_filename
        })

        result = dal.environment.get_by_id(environment.id)
        assert environment.id == result.id

    def test_get_by_id_environment_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        environment_id = 'id_3'
        environment_driver_type = 'docker'
        environment_file_collection_id = 'test_file_id'
        environment_definition_filename = 'Dockerfile'
        environment = dal.environment.create({
            'id': environment_id,
            'model_id': model.id,
            'driver_type': environment_driver_type,
            'file_collection_id': environment_file_collection_id,
            'definition_filename': environment_definition_filename
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.environment.get_by_id(environment.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_environment = new_dal_instance.environment.get_by_id(environment.id)
        assert new_environment.id == environment.id

    def test_update_environment(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        environment_id = 'id_4'
        environment_driver_type = 'docker'
        environment_file_collection_id = 'test_file_id'
        environment_definition_filename = 'Dockerfile'
        environment = dal.environment.create({
            'id': environment_id,
            'model_id': model.id,
            'driver_type': environment_driver_type,
            'file_collection_id': environment_file_collection_id,
            'definition_filename': environment_definition_filename
        })

        # Update required and optional parameters
        updated_environment_driver_type = 'new_driver'
        updated_environment_created_at = datetime.utcnow()
        updated_environment = dal.environment.update({
            'id': environment.id,
            'driver_type': updated_environment_driver_type,
            'created_at': updated_environment_created_at
        })
        assert environment.id == updated_environment.id and \
               environment.updated_at < updated_environment.updated_at and \
               updated_environment.driver_type == updated_environment_driver_type and \
               updated_environment.created_at == updated_environment_created_at

    def test_delete_environment(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        environment_id = 'id_5'
        environment_driver_type = 'docker'
        environment_file_collection_id = 'test_file_id'
        environment_definition_filename = 'Dockerfile'
        environment = dal.environment.create({
            'id': environment_id,
            'model_id': model.id,
            'driver_type': environment_driver_type,
            'file_collection_id': environment_file_collection_id,
            'definition_filename': environment_definition_filename
        })

        dal.environment.delete(environment.id)
        deleted = False
        try:
            dal.environment.get_by_id(environment.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_environments(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        environment_id = 'id_5'
        environment_driver_type = 'docker'
        environment_file_collection_id = 'test_file_id'
        environment_definition_filename = 'Dockerfile'
        environment = dal.environment.create({
            'id': environment_id,
            'model_id': model.id,
            'driver_type': environment_driver_type,
            'file_collection_id': environment_file_collection_id,
            'definition_filename': environment_definition_filename
        })

        assert len(dal.environment.query({'id': environment.id})) == 1


    # FileCollection

    def test_create_file_collection_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        file_collection_id = 'id_1'
        file_collection_driver_type = 'local'
        file_collection = dal.file_collection.create({
            'id': file_collection_id,
            'model_id': model.id,
            'driver_type': file_collection_driver_type
        })

        assert file_collection.id == file_collection_id
        assert file_collection.driver_type == file_collection_driver_type
        assert file_collection.created_at
        assert file_collection.updated_at

    def test_get_by_id_file_collection(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        file_collection_id = 'id_2'
        file_collection_driver_type = 'local'
        file_collection = dal.file_collection.create({
            'id': file_collection_id,
            'model_id': model.id,
            'driver_type': file_collection_driver_type
        })

        result = dal.file_collection.get_by_id(file_collection.id)
        assert file_collection.id == result.id

    def test_get_by_id_file_collection_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        file_collection_id = 'id_3'
        file_collection_driver_type = 'local'
        file_collection = dal.file_collection.create({
            'id': file_collection_id,
            'model_id': model.id,
            'driver_type': file_collection_driver_type
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.file_collection.get_by_id(file_collection.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_file_collection = new_dal_instance.file_collection.get_by_id(file_collection.id)
        assert new_file_collection.id == file_collection.id

    def test_update_file_collection(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        file_collection_id = 'id_4'
        file_collection_driver_type = 'local'
        file_collection = dal.file_collection.create({
            'id': file_collection_id,
            'model_id': model.id,
            'driver_type': file_collection_driver_type
        })

        # Update required and optional parameters
        updated_file_collection_driver_type = 'new_driver'
        updated_file_collection_created_at = datetime.utcnow()
        updated_file_collection = dal.file_collection.update({
            'id': file_collection.id,
            'driver_type': updated_file_collection_driver_type,
            'created_at': updated_file_collection_created_at
        })
        assert file_collection.id == updated_file_collection.id and \
               file_collection.updated_at < updated_file_collection.updated_at and \
               updated_file_collection.driver_type == updated_file_collection_driver_type and \
               updated_file_collection.created_at == updated_file_collection_created_at

    def test_delete_file_collection(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        file_collection_id = 'id_5'
        file_collection_driver_type = 'local'
        file_collection = dal.file_collection.create({
            'id': file_collection_id,
            'model_id': model.id,
            'driver_type': file_collection_driver_type
        })

        dal.file_collection.delete(file_collection.id)
        deleted = False
        try:
            dal.file_collection.get_by_id(file_collection.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_file_collections(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        file_collection_id = 'id_5'
        file_collection_driver_type = 'local'
        file_collection = dal.file_collection.create({
            'id': file_collection_id,
            'model_id': model.id,
            'driver_type': file_collection_driver_type
        })

        assert len(dal.file_collection.query({'id': file_collection.id})) == 1

    # Session

    def test_create_session_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        assert session.name == session_name
        assert session.created_at
        assert session.updated_at

    def test_get_by_id_session(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        session_name = 'session_2'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        result = dal.session.get_by_id(session.id)
        assert session.id == result.id

    def test_get_by_id_session_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        session_name = 'session_3'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.session.get_by_id(session.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_session = new_dal_instance.session.get_by_id(session.id)
        assert new_session.id == session.id

    def test_update_session(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        session_name = 'session_4'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        # Update required and optional parameters
        updated_session_name = 'session_yo'
        updated_session_created_at = datetime.utcnow()
        updated_session = dal.session.update({
            'id': session.id,
            'name': updated_session_name,
            'created_at': updated_session_created_at
        })
        assert session.id == updated_session.id and \
               session.updated_at < updated_session.updated_at and \
               updated_session.name == updated_session_name and \
               updated_session.created_at == updated_session_created_at

    def test_delete_session(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        session_name = 'session_4'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        dal.session.delete(session.id)
        deleted = False
        try:
            dal.session.get_by_id(session.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_sessions(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        session_name = 'session_5'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        assert len(dal.session.query({'id': session.id})) == 1
        assert len(dal.session.query({'name': session_name})) == 1

    # Task

    def test_create_task_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        task_command = 'task_1'
        task_code_id = 'code_id'
        task_environment_id = 'environment_id'
        task_file_collection_id = 'file_collection_id'
        task = dal.task.create({
            'model_id': model.id,
            'session_id': session.id,
            'command': task_command,
            'code_id': task_code_id,
            'environment_id': task_environment_id,
            'file_collection_id': task_file_collection_id
        })

        assert task.command == task_command
        assert task.created_at
        assert task.updated_at

    def test_get_by_id_task(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        task_command = 'task_2'
        task_code_id = 'code_id'
        task_environment_id = 'environment_id'
        task_file_collection_id = 'file_collection_id'
        task = dal.task.create({
            'model_id': model.id,
            'session_id': session.id,
            'command': task_command,
            'code_id': task_code_id,
            'environment_id': task_environment_id,
            'file_collection_id': task_file_collection_id
        })

        result = dal.task.get_by_id(task.id)
        assert task.id == result.id

    def test_get_by_id_task_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        task_command = 'task_3'
        task_code_id = 'code_id'
        task_environment_id = 'environment_id'
        task_file_collection_id = 'file_collection_id'
        task = dal.task.create({
            'model_id': model.id,
            'session_id': session.id,
            'command': task_command,
            'code_id': task_code_id,
            'environment_id': task_environment_id,
            'file_collection_id': task_file_collection_id
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.task.get_by_id(task.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_task = new_dal_instance.task.get_by_id(task.id)
        assert new_task.id == task.id

    def test_update_task(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        task_command = 'task_4'
        task_code_id = 'code_id'
        task_environment_id = 'environment_id'
        task_file_collection_id = 'file_collection_id'
        task = dal.task.create({
            'model_id': model.id,
            'session_id': session.id,
            'command': task_command,
            'code_id': task_code_id,
            'environment_id': task_environment_id,
            'file_collection_id': task_file_collection_id
        })

        # Update required and optional parameters
        updated_task_command = "task_new"
        updated_task_ports = [9000]
        updated_task = dal.task.update({
            'id': task.id,
            'command': updated_task_command,
            'ports': updated_task_ports
        })

        assert task.id == updated_task.id and \
               task.updated_at < updated_task.updated_at and \
               updated_task.command == updated_task_command and \
               updated_task.ports == updated_task_ports

    def test_delete_task(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        task_command = 'task_4'
        task_code_id = 'code_id'
        task_environment_id = 'environment_id'
        task_file_collection_id = 'file_collection_id'
        task = dal.task.create({
            'model_id': model.id,
            'session_id': session.id,
            'command': task_command,
            'code_id': task_code_id,
            'environment_id': task_environment_id,
            'file_collection_id': task_file_collection_id
        })

        dal.task.delete(task.id)
        deleted = False
        try:
            dal.task.get_by_id(task.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_tasks(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})
        session_name = 'session_1'
        session = dal.session.create({
            'name': session_name,
            'model_id': model.id
        })

        task_command = 'task_5'
        task_code_id = 'code_id'
        task_environment_id = 'environment_id'
        task_file_collection_id = 'file_collection_id'
        task = dal.task.create({
            'model_id': model.id,
            'session_id': session.id,
            'command': task_command,
            'code_id': task_code_id,
            'environment_id': task_environment_id,
            'file_collection_id': task_file_collection_id
        })

        assert len(dal.task.query({'id': task.id})) == 1
        assert len(dal.task.query({'command': task_command})) == 1

    # Snapshot

    def test_create_snapshot_by_dictionary(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        snapshot_code_id = 'code_id'
        snapshot_enviroment_id= 'environment_id'
        snapshot_file_collection_id = 'file_collection_id'
        snapshot_config = {"test": 0.45}
        snapshot_stats = {"test": 0.98}

        snapshot = dal.snapshot.create({
            'model_id': model.id,
            'code_id': snapshot_code_id,
            'environment_id': snapshot_enviroment_id,
            'file_collection_id': snapshot_file_collection_id,
            'config': snapshot_config,
            'stats': snapshot_stats
        })
        assert snapshot.code_id == snapshot_code_id
        assert snapshot.created_at
        assert snapshot.updated_at

    def test_get_by_id_snapshot(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        snapshot_code_id = 'code_id'
        snapshot_enviroment_id = 'environment_id'
        snapshot_file_collection_id = 'file_collection_id'
        snapshot_config = {"test": 0.45}
        snapshot_stats = {"test": 0.98}

        snapshot = dal.snapshot.create({
            'model_id': model.id,
            'code_id': snapshot_code_id,
            'environment_id': snapshot_enviroment_id,
            'file_collection_id': snapshot_file_collection_id,
            'config': snapshot_config,
            'stats': snapshot_stats
        })

        result = dal.snapshot.get_by_id(snapshot.id)
        assert snapshot.id == result.id

    def test_get_by_id_snapshot_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        snapshot_code_id = 'code_id'
        snapshot_enviroment_id = 'environment_id'
        snapshot_file_collection_id = 'file_collection_id'
        snapshot_config = {"test": 0.45}
        snapshot_stats = {"test": 0.98}

        snapshot = dal.snapshot.create({
            'model_id': model.id,
            'code_id': snapshot_code_id,
            'environment_id': snapshot_enviroment_id,
            'file_collection_id': snapshot_file_collection_id,
            'config': snapshot_config,
            'stats': snapshot_stats
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.snapshot.get_by_id(snapshot.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_snapshot = new_dal_instance.snapshot.get_by_id(snapshot.id)
        assert new_snapshot.id == snapshot.id

    def test_update_snapshot(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        snapshot_code_id = 'code_id'
        snapshot_enviroment_id = 'environment_id'
        snapshot_file_collection_id = 'file_collection_id'
        snapshot_config = {"test": 0.45}
        snapshot_stats = {"test": 0.98}

        snapshot = dal.snapshot.create({
            'model_id': model.id,
            'code_id': snapshot_code_id,
            'environment_id': snapshot_enviroment_id,
            'file_collection_id': snapshot_file_collection_id,
            'config': snapshot_config,
            'stats': snapshot_stats
        })

        # Update required and optional parameters
        updated_snapshot_config = {
            "cool": 0.33
        }
        updated_snapshot_message = "this is really cool"
        updated_snapshot = dal.snapshot.update({
            'id': snapshot.id,
            'config': updated_snapshot_config,
            'message': updated_snapshot_message
        })

        assert snapshot.id == updated_snapshot.id and \
               snapshot.updated_at < updated_snapshot.updated_at and \
               updated_snapshot.config == updated_snapshot_config and \
               updated_snapshot.message == updated_snapshot_message

    def test_delete_snapshot(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        snapshot_code_id = 'code_id'
        snapshot_enviroment_id = 'environment_id'
        snapshot_file_collection_id = 'file_collection_id'
        snapshot_config = {"test": 0.45}
        snapshot_stats = {"test": 0.98}

        snapshot = dal.snapshot.create({
            'model_id': model.id,
            'code_id': snapshot_code_id,
            'environment_id': snapshot_enviroment_id,
            'file_collection_id': snapshot_file_collection_id,
            'config': snapshot_config,
            'stats': snapshot_stats
        })

        dal.snapshot.delete(snapshot.id)
        deleted = False
        try:
            dal.snapshot.get_by_id(snapshot.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_snapshots(self):
        dal = LocalDAL(self.datadriver)
        model_name = 'model_1'
        model = dal.model.create({'name': model_name})

        snapshot_code_id = 'code_id'
        snapshot_enviroment_id = 'environment_id'
        snapshot_file_collection_id = 'file_collection_id'
        snapshot_config = {"test": 0.45}
        snapshot_stats = {"test": 0.98}

        snapshot = dal.snapshot.create({
            'model_id': model.id,
            'code_id': snapshot_code_id,
            'environment_id': snapshot_enviroment_id,
            'file_collection_id': snapshot_file_collection_id,
            'config': snapshot_config,
            'stats': snapshot_stats
        })

        # All snapshots created are the same, 1 is deleted => 5
        assert len(dal.snapshot.query({'id': snapshot.id})) == 1
        assert len(dal.snapshot.query({'code_id': snapshot_code_id})) == 5

    # User

    def test_create_user_by_dictionary(self):
        dal = LocalDAL(self.datadriver)

        user_name = 'user_1'
        user_email = 'test@test.com'

        user = dal.user.create({
            'name': user_name,
            'email': user_email,
        })
        assert user.name == user_name
        assert user.created_at
        assert user.updated_at

    def test_get_by_id_user(self):
        dal = LocalDAL(self.datadriver)

        user_name = 'user_2'
        user_email = 'test@test.com'

        user = dal.user.create({
            'name': user_name,
            'email': user_email,
        })

        result = dal.user.get_by_id(user.id)
        assert user.id == result.id

    def test_get_by_id_user_new_driver_instance(self):
        dal = LocalDAL(self.datadriver)

        user_name = 'user_3'
        user_email = 'test@test.com'

        user = dal.user.create({
            'name': user_name,
            'email': user_email,
        })

        # create new dal with new driver instance (fails)
        new_driver_instance = BlitzDBDataDriver(DriverType.FILE, self.temp_dir)
        new_dal_instance = LocalDAL(new_driver_instance)
        try:
            new_dal_instance.user.get_by_id(user.id)
        except:
            assert True
        # create new dal instance with same driver (success)
        new_dal_instance = LocalDAL(self.datadriver)
        new_user = new_dal_instance.user.get_by_id(user.id)
        assert new_user.id == user.id

    def test_update_user(self):
        dal = LocalDAL(self.datadriver)

        user_name = 'user_4'
        user_email = 'test@test.com'

        user = dal.user.create({
            'name': user_name,
            'email': user_email,
        })

        # Update required and optional parameters
        updated_user_name = "cooldude"
        updated_user_created_at = datetime.utcnow()
        updated_user = dal.user.update({
            'id': user.id,
            'name': updated_user_name,
            'created_at': updated_user_created_at
        })

        assert user.id == updated_user.id and \
               user.updated_at < updated_user.updated_at and \
               updated_user.name == updated_user_name and \
               updated_user.created_at == updated_user_created_at

    def test_delete_user(self):
        dal = LocalDAL(self.datadriver)

        user_name = 'user_4'
        user_email = 'test@test.com'

        user = dal.user.create({
            'name': user_name,
            'email': user_email,
        })

        dal.user.delete(user.id)
        deleted = False
        try:
            dal.user.get_by_id(user.id)
        except EntityNotFound:
            deleted = True
        assert deleted

    def test_query_users(self):
        dal = LocalDAL(self.datadriver)

        user_name = 'user_5'
        user_email = 'test@test.com'

        user = dal.user.create({
            'name': user_name,
            'email': user_email,
        })

        assert len(dal.user.query({'id': user.id})) == 1
        assert len(dal.user.query({'name': user_name})) == 1