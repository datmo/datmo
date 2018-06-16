"""
Tests for SessionController
"""
import os
import shutil
import tempfile
import platform

from datmo.config import Config
from datmo.core.controller.project import ProjectController
from datmo.core.controller.session import SessionController
from datmo.core.util.exceptions import InvalidArgumentType, ProjectNotInitialized, InvalidProjectPath, SessionDoesNotExist, InvalidOperation, EntityNotFound


class TestSessionController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = "/tmp" if not platform.system(
        ) == "Windows" else None
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def __setup(self):
        Config().set_home(self.temp_dir)
        self.project_controller = ProjectController()
        self.project_controller.init("test", "test description")
        self.session_controller = SessionController()

    def test_init_fail_project_not_init(self):
        Config().set_home(self.temp_dir)
        failed = False
        try:
            SessionController()
        except ProjectNotInitialized:
            failed = True
        assert failed

    def test_init_fail_invalid_path(self):
        test_home = "some_random_dir"
        Config().set_home(test_home)
        failed = False
        try:
            SessionController()
        except InvalidProjectPath:
            failed = True
        assert failed

    def test_find_default_session(self):
        self.__setup()
        sessions = self.session_controller.list()
        has_default = False
        for s in sessions:
            if s.name == 'default':
                has_default = True
                break
        assert has_default

    def test_create_session(self):
        self.__setup()
        test_sess = self.session_controller.create({"name": "test1"})
        assert test_sess.id
        assert test_sess.model_id == self.project_controller.model.id

    def test_select(self):
        self.__setup()
        session_obj = self.session_controller.create({"name": "test2"})
        # Test success with name
        new_current = self.session_controller.select("test2")
        assert new_current.current == True
        found_old_current = False
        current_was_updated = False
        for sess in self.session_controller.list():
            if sess.current == True and sess.id != new_current.id:
                found_old_current = True
            if sess.current == True and sess.id == new_current.id:
                current_was_updated = True
        assert not found_old_current == True
        assert current_was_updated == True
        # reset to default
        _ = self.session_controller.select("default")
        # Test success with id
        new_current = self.session_controller.select(session_obj.id)
        assert new_current.current == True
        found_old_current = False
        current_was_updated = False
        for sess in self.session_controller.list():
            if sess.current == True and sess.id != new_current.id:
                found_old_current = True
            if sess.current == True and sess.id == new_current.id:
                current_was_updated = True
        assert not found_old_current == True
        assert current_was_updated == True
        # Test failure no session
        failed = False
        try:
            _ = self.session_controller.select("random_name_or_id")
        except SessionDoesNotExist:
            failed = True
        assert failed

    def test_get_current(self):
        self.__setup()
        current_sess = self.session_controller.get_current()
        assert current_sess
        assert current_sess.current == True

    def test_list_session_sort(self):
        self.__setup()
        # Sort ascending
        sessions = self.session_controller.list(
            sort_key='created_at', sort_order='ascending')
        assert sessions[0].created_at <= sessions[-1].created_at

        # Sort descending
        sessions = self.session_controller.list(
            sort_key='created_at', sort_order='descending')
        assert sessions[0].created_at >= sessions[-1].created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.session_controller.list(
                sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.session_controller.list(
                sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_sessions = self.session_controller.list(
            sort_key='created_at', sort_order='ascending')
        sessions = self.session_controller.list(
            sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_sessions]
        ids = [item.id for item in sessions]
        assert set(expected_ids) == set(ids)

    def test_update(self):
        self.__setup()
        # Test successful update
        session_obj = self.session_controller.create({"name": "test3"})
        new_name = "new"
        updated_session_obj = self.session_controller.update(
            session_obj.id, name=new_name)
        same_session_obj = self.session_controller.dal.session.findOne({
            "name": new_name
        })
        assert updated_session_obj == same_session_obj
        assert updated_session_obj.name == new_name
        # Test failure session does not exist
        failed = False
        try:
            self.session_controller.update("random_id")
        except SessionDoesNotExist:
            failed = True
        assert failed
        # Test failure try to update default
        default_session_obj = self.session_controller.dal.session.findOne({
            "name": "default"
        })
        failed = False
        try:
            self.session_controller.update(default_session_obj.id)
        except InvalidOperation:
            failed = True
        assert failed

    def test_delete(self):
        self.__setup()
        # Test successful delete
        session_obj = self.session_controller.create({"name": "test3"})
        _ = self.session_controller.select("test3")
        self.session_controller.delete(session_obj.id)
        entity_does_not_exist = False
        try:
            _ = self.session_controller.dal.session.get_by_id(session_obj.id)
        except EntityNotFound:
            entity_does_not_exist = True
        assert entity_does_not_exist
        # current session should be "default"
        assert self.session_controller.get_current().name == "default"
        # Test failure delete default
        failed = False
        try:
            self.session_controller.delete(
                self.session_controller.get_current().id)
        except InvalidOperation:
            failed = True
        assert failed
        # Test failure does not exist
        failed = False
        try:
            self.session_controller.delete("random_id")
        except SessionDoesNotExist:
            failed = True
        assert failed

    def test_delete_by_name(self):
        self.__setup()
        session_obj = self.session_controller.create({"name": "test3"})
        _ = self.session_controller.select("test3")
        self.session_controller.delete_by_name("test3")
        entity_does_not_exist = False
        try:
            _ = self.session_controller.dal.session.get_by_id(session_obj.id)
        except EntityNotFound:
            entity_does_not_exist = True
        assert entity_does_not_exist
        # current session should be "default"
        assert self.session_controller.get_current().name == "default"
        # Test failure delete default
        failed = False
        try:
            self.session_controller.delete_by_name(
                self.session_controller.get_current().name)
        except InvalidOperation:
            failed = True
        assert failed
        # Test failure does not exist
        failed = False
        try:
            self.session_controller.delete_by_name("random_name")
        except SessionDoesNotExist:
            failed = True
        assert failed
