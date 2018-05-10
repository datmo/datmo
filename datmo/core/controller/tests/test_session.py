"""
Tests for SessionController
"""
import os
import shutil
import tempfile

from datmo.core.controller.project import ProjectController
from datmo.core.controller.session import SessionController
from datmo.core.util.exceptions import InvalidArgumentType, ProjectNotInitializedException, InvalidProjectPathException


class TestSessionController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def __setup(self):
        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.session = SessionController(self.temp_dir)

    def test_init_fail_project_not_init(self):
        failed = False
        try:
            SessionController(self.temp_dir)
        except ProjectNotInitializedException:
            failed = True
        assert failed

    def test_init_fail_invalid_path(self):
        test_home = "some_random_dir"
        failed = False
        try:
            SessionController(test_home)
        except InvalidProjectPathException:
            failed = True
        assert failed

    def test_find_default_session(self):
        self.__setup()
        sessions = self.session.list()
        has_default = False
        for s in sessions:
            if s.name == 'default':
                has_default = True
                break
        assert has_default

    def test_create_session(self):
        self.__setup()
        test_sess = self.session.create({"name": "test1"})
        assert test_sess.id
        assert test_sess.model_id == self.project.model.id

    def test_select_session(self):
        self.__setup()
        self.session.create({"name": "test2"})
        new_current = self.session.select("test2")
        assert new_current.current == True
        found_old_current = False
        current_was_updated = False
        for s in self.session.list():
            if s.current == True and s.id != new_current.id:
                found_old_current = True
            if s.current == True and s.id == new_current.id:
                current_was_updated = True
        assert not found_old_current == True
        assert current_was_updated == True

    def test_get_current(self):
        self.__setup()
        current_sess = self.session.get_current()
        assert current_sess
        assert current_sess.current == True

    def test_list_session_sort(self):
        self.__setup()
        # Sort ascending
        sessions = self.session.list(
            sort_key='created_at', sort_order='ascending')
        assert sessions[0].created_at <= sessions[-1].created_at

        # Sort descending
        sessions = self.session.list(
            sort_key='created_at', sort_order='descending')
        assert sessions[0].created_at >= sessions[-1].created_at

        # Wrong order being passed in
        failed = False
        try:
            _ = self.session.list(
                sort_key='created_at', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # Wrong key and order being passed in
        failed = False
        try:
            _ = self.session.list(
                sort_key='wrong_key', sort_order='wrong_order')
        except InvalidArgumentType:
            failed = True
        assert failed

        # wrong key and right order being passed in
        expected_sessions = self.session.list(
            sort_key='created_at', sort_order='ascending')
        sessions = self.session.list(
            sort_key='wrong_key', sort_order='ascending')
        expected_ids = [item.id for item in expected_sessions]
        ids = [item.id for item in sessions]
        assert set(expected_ids) == set(ids)

    def test_delete_session(self):
        self.__setup()
        self.session.create({"name": "test3"})
        _ = self.session.select("test3")
        self.session.delete_by_name("test3")
        entity_exists = False
        try:
            _ = self.session.findOne({"name": "test3"})
            entity_exists = True
        except:
            pass
        assert not entity_exists
        # current session should be "default"
        assert self.session.get_current().name == 'default'
