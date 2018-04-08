from datmo.controller.base import BaseController

class ModelController(BaseController):
    """
    ModelController inherits from BaseController and manages business logic related to the
    model.

    # TODO: Enable multiple models per project
    """
    def __init__(self, home, dal_driver=None):
        super(ModelController, self).__init__(home, dal_driver)

    def create(self):
        pass