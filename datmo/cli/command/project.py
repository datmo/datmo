from datmo import __version__
from datmo.core.util.i18n import get as __
from datmo.cli.command.base import BaseCommand
from datmo.core.controller.project import ProjectController


class ProjectCommand(BaseCommand):
    # NOTE: dal_driver is not passed into the project because it is created
    # first by ProjectController and then passed down to all other Controllers
    def __init__(self, home, cli_helper, parser):
        super(ProjectCommand, self).__init__(home, cli_helper, parser)
        self.project_controller = ProjectController(home=home)

    def init(self, name, description):
        if not name:
            name = self.cli_helper.prompt(
                __("prompt", "cli.project.init.name"))
        if not description:
            description = self.cli_helper.prompt(
                __("prompt", "cli.project.init.description"))
        self.cli_helper.echo(
            __("info", "cli.project.init", {
                "name": name,
                "path": self.home
            }))
        self.project_controller.init(name, description)

    def version(self):
        return self.cli_helper.echo("datmo version: %s" % __version__)