from datmo.util.i18n import get as _
from datmo.cli.driver.cli_base_command import CLIBaseCommand
from datmo.controller.project import ProjectController
from datmo.cli.driver.cli_argument_parser import CLIArgumentParser

def get_parser():
    init_parser = CLIArgumentParser(prog='datmo', usage='%(prog)s init')
    init_parser.add_argument("command", choices=['init'])
    init_parser.add_argument("--name")
    init_parser.add_argument("--description", default=None)
    return init_parser

class Init(CLIBaseCommand):
    # NOTE: dal_driver is not passed into the project because it is created
    # first by ProjectController and then passed down to all other Controllers
    def __init__(self, home, cli_helper):
        self.cli_helper = cli_helper
        self.controller = ProjectController(home=home,
                                            cli_helper=self.cli_helper)
        super(Init, self).__init__(self.cli_helper, get_parser())

    def init(self, name, description):
        self.cli_helper.echo(_('setup.init_project', {"name":name, "path": self.controller.home}))
        self.controller.init(name, description)