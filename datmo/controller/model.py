from .base import BaseController
from datmo.cli.driver.cli_helper import CLIHelper


class ModelController(BaseController):
    def __init__(self, home, cli_helper=CLIHelper()):
        super(ModelController, self).__init__(home, cli_helper)

    def init(self):
        pass