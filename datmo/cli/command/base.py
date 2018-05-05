#!/usr/bin/python

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import ClassMethodNotFound


class BaseCommand(object):
    def __init__(self, home, cli_helper, parser):
        self.home = home
        self.cli_helper = cli_helper
        self.parser = parser

    def parse(self, args):
        self.args = self.parser.parse_args(args)

    def execute(self):
        """
        Calls the method if it exists on this object, otherwise
        call a default method name (module name)

        Raises
        ------
        ClassMethodNotFound
            If the Class method is not found

        """
        command_args = vars(self.args).copy()
        # use command name if it exists,
        # otherwise use the module name

        if "subcommand" in command_args:
            method = getattr(self,
                             getattr(self.args, "subcommand",
                                     self.args.command))
        else:
            method = getattr(self,
                             getattr(self.args, "command", self.args.command))

        # remove extraneous options that the method should need to care about
        if "command" in command_args:
            del command_args["command"]
        if "subcommand" in command_args:
            del command_args["subcommand"]

        if method is None:
            raise ClassMethodNotFound(
                __("error", "cli.general.method.not_found",
                   (self.args.command, method)))

        method_result = method(**command_args)
        return method_result
