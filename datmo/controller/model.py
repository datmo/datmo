from .base import BaseController
from datmo.cli.driver.cli_helper import CLIHelper


class ModelController(BaseController):
    def __init__(self, home, cli_helper=CLIHelper(), dal_driver=None):
        super(ModelController, self).__init__(home, cli_helper, dal_driver)

    def init(self):
        pass