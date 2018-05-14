#!/usr/bin/python

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import ClassMethodNotFound
from datmo.cli.parser import get_datmo_parser
from datmo.core.util.logger import DatmoLogger
from datmo.core.util.misc_functions import parameterized


class BaseCommand(object):
    def __init__(self, home, cli_helper):
        self.home = home
        self.cli_helper = cli_helper
        self.logger = DatmoLogger.get_logger(__name__)
        self.parser = get_datmo_parser()

    def parse(self, args):
        try:
            self.display_usage_message(args)
            self.args = self.parser.parse_args(args)
        except SystemExit:
            self.args = True
            pass

    def display_usage_message(self, args):
        """ Checks to see if --help or -h is passed in, and if so it calls our help()
        if it exists.

        Since argparser thinks it is clever and automatically
        handles [--help, -h] we need a hook to be able to display
        our own usage notes before argparse

        Parameters
        ----------
        args : array[string]
            command arguments
        """

        is_help = -1
        if "--help" in args:
            is_help = args.index("--help")
        if is_help == -1 and "-h" in args:
            is_help = args.index("-h")

        if is_help > -1 and hasattr(self, "usage"):
            self.usage()

    def execute(self):
        """
        Calls the method if it exists on this object, otherwise
        call a default method name (module name)

        Raises
        ------
        ClassMethodNotFound
            If the Class method is not found
        """

        # Sometimes eg(--help) the parser automagically handles the entire response
        # and calls exit.  If this happens, self.args is set to True
        # in base.parse.   Simply return True
        if self.args is True: return True

        if getattr(self.args, 'command') is None:
            self.args.command = 'datmo'

        command_args = vars(self.args).copy()
        # use command name if it exists,
        # otherwise use the module name
        method = None

        if "subcommand" in command_args and command_args['subcommand'] is not None:
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


@parameterized
def usage_docs(description):
    # TODO: create an attribute so we can show custom usage notes before
    # argparse displays help
    pass
