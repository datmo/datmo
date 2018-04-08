from datmo.controller.base import BaseController

class ModelController(BaseController):
    """
    Model Controller for functions to manage a model.

    # TODO: Enable multiple models per project
    """
    def __init__(self, home, dal_driver=None):
        super(ModelController, self).__init__(home, dal_driver)

    def create(self):
        pass