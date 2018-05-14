from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.util.exceptions import EnvironmentInitFailed


class ModelController(BaseController):
    """ModelController inherits from BaseController and manages business logic related to the
    model.

    Parameters
    ----------
    home : str
        home path of the project

    # TODO: Enable multiple models per project
    """

    def __init__(self, home):
        super(ModelController, self).__init__(home)

    def create(self):
        pass
