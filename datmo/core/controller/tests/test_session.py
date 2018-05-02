"""
Tests for SessionController
"""
import os
import shutil
import tempfile

from datmo.core.controller.project import ProjectController
from datmo.core.controller.session import SessionController
from datmo.core.util.exceptions import EntityNotFound, \
    GitCommitDoesNotExist, SessionDoesNotExistException


class TestSessionController():
    def setup_method(self):
        # provide mountable tmp directory for docker
        tempfile.tempdir = '/tmp'
        test_datmo_dir = os.environ.get('TEST_DATMO_DIR',
                                        tempfile.gettempdir())
        self.temp_dir = tempfile.mkdtemp(dir=test_datmo_dir)

        self.project = ProjectController(self.temp_dir)
        self.project.init("test", "test description")
        self.session = SessionController(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_find_default_session(self):
        sessions = self.session.list()
        has_default = False
        for s in sessions:
            if s.name == 'default':
                has_default = True
                break
        assert has_default

    def test_create_session(self):
        test_sess = self.session.create({"name": "test1"})
        assert test_sess.id
        assert test_sess.model_id == self.project.model.id

    def test_select_session(self):
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
        current_sess = self.session.get_current()
        assert current_sess
        assert current_sess.current == True

    def test_delete_session(self):
        self.session.create({"name": "test3"})
        new_current = self.session.select("test3")
        self.session.delete_by_name("test3")
        entity_exists = False
        try:
            session_still_exists = self.session.findOne({"name": "test3"})
            entity_exists = True
        except:
            pass
        assert not entity_exists
        # current session should be "default"
        assert self.session.get_current().name == 'default'
