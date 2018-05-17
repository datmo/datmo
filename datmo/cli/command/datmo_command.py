from datmo.core.util.i18n import get as __
from datmo.cli.command.base import BaseCommand


class DatmoCommand(BaseCommand):
    def __init__(self, cli_helper):
        super(DatmoCommand, self).__init__(cli_helper)

    def usage(self):
        self.cli_helper.echo(__("argparser", "cli.datmo.usage"))

    def datmo(self):
        self.parse(["--help"])
        return True
