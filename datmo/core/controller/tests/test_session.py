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
from datmo.core.util.exceptions import InvalidArgumentType, ProjectNotInitialized, InvalidProjectPath


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

    def test_select_session(self):
        self.__setup()
        self.session_controller.create({"name": "test2"})
        new_current = self.session_controller.select("test2")
        assert new_current.current == True
        found_old_current = False
        current_was_updated = False
        for s in self.session_controller.list():
            if s.current == True and s.id != new_current.id:
                found_old_current = True
            if s.current == True and s.id == new_current.id:
                current_was_updated = True
        assert not found_old_current == True
        assert current_was_updated == True

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

    def test_delete_session(self):
        self.__setup()
        self.session_controller.create({"name": "test3"})
        _ = self.session_controller.select("test3")
        self.session_controller.delete_by_name("test3")
        entity_exists = False
        try:
            _ = self.session_controller.findOne({"name": "test3"})
            entity_exists = True
        except Exception:
            pass
        assert not entity_exists
        # current session should be "default"
        assert self.session_controller.get_current().name == 'default'
