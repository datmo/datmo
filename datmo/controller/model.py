from datmo.controller.base import BaseController

class ModelController(BaseController):
    def __init__(self, home, dal_driver=None):
        super(ModelController, self).__init__(home, dal_driver)

    def init(self):
        pass