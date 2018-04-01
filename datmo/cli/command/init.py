import os
from datmo.util.i18n import get as _
from datmo.cli.driver.cli_base_command import CLIBaseCommand
from datmo.controller.project import ProjectController
from datmo.cli.driver.cli_argument_parser import CLIArgumentParser

def get_parser():
    init_parser = CLIArgumentParser(prog='datmo', usage='%(prog)s init')
    init_parser.add_argument("command", choices=['init'])
    init_parser.add_argument("--name")
    init_parser.add_argument("--description", default=None)
    init_parser.add_argument("--path", default=os.getcwd())
    return init_parser

class Init(CLIBaseCommand):
    def __init__(self, cli_helper):
        super(Init, self).__init__(cli_helper, get_parser())

    def init(self, name, description, path):
        self.cli.echo(_('setup.init_project', {"name":name, "path":path}))
        project = ProjectController(path, self.cli)
        project.init(name, description)