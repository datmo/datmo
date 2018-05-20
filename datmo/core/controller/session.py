from datmo.core.controller.base import BaseController
from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (EntityNotFound, InvalidOperation,
                                        ProjectNotInitialized)
from datmo.core.util.validation import validate


class SessionController(BaseController):
    """SessionController inherits from BaseController and manages business logic related to session

    Parameters
    ----------
    home : str
        home path of the project

    Methods
    -------
    create(dictionary)
        Create a session within the project
    select(name)
        Selects a new current session by name
    get_current()
        Returns the current session
    list(query={})
        Query sessions
    delete_by_name(name)
        Deletes session by name. if session is
        flagged as current, switches to default session

    """

    def __init__(self, home):
        super(SessionController, self).__init__(home)
        if not self.is_initialized:
            raise ProjectNotInitialized(
                __("error", "controller.session.__init__"))

    def create(self, incoming_dictionary):
        # Look for existing session first and return if it exists

        validate("create_session", incoming_dictionary)

        results = self.dal.session.query({
            "model_id": self.model.id,
            "name": incoming_dictionary['name']
        })
        if len(results) == 1: return results[0]

        session_dict = {
            "model_id": self.model.id,
            "name": incoming_dictionary["name"]
        }

        # Create new session and return
        return self.dal.session.create(session_dict)

    def select(self, name):
        # Find session object by name
        next_session = self.dal.session.query({
            "model_id": self.model.id,
            "name": name
        })

        if len(next_session) == 0:
            raise EntityNotFound('session')

        next_session = next_session[0]
        # already current session
        if next_session.current == True:
            return next_session

        current_session = self.dal.session.query({
            "model_id": self.model.id,
            "current": True
        })

        if len(current_session) == 0:
            raise EntityNotFound('current session')

        current_session = current_session[0]
        current_session.current = False
        self.dal.session.update(current_session)

        next_session.current = True
        self.dal.session.update(next_session)
        return next_session

    def get_current(self):
        return self.dal.session.findOne({
            "model_id": self.model.id,
            "current": True
        })

    def list(self, sort_key=None, sort_order=None):
        query = {}
        return self.dal.session.query(query, sort_key, sort_order)

    def delete_by_name(self, name):
        if name == 'default':
            raise InvalidOperation(
                __("error", "controller.session.delete.default"))

        session = self.dal.session.findOne({
            "model_id": self.model.id,
            "name": name
        })

        if session.current == True:
            self.select("default")
        self.dal.session.delete(session.id)

        #  Delete snapshots for this session
        for s in self.dal.snapshot.query({"session_id": session.id}):
            self.dal.snapshot.delete(s.id)

        # Delete tasks for this session
        for t in self.dal.task.query({"session_id": session.id}):
            self.dal.task.delete(t.id)

        return True
