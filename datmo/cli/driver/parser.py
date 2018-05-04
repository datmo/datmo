import sys
import argparse

from datmo.core.util.exceptions import UnrecognizedCLIArgument


class Parser(argparse.ArgumentParser):
    """
    Overwrite the original ArgumentParser

    https://stackoverflow.com/questions/5943249/python-argparse-and-controlling-overriding-the-exit-status-code/5943389

    Methods
    -------
    _get_action_from_name(name)
        Get the Action instance registered with this parser
    error(message)
        Raise a parsing error. Overwrites original ArgumentParser error function

    """

    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if "unrecognized arguments" in message or \
            "argument command: invalid choice" in message:
            raise UnrecognizedCLIArgument(message)

        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(Parser, self).error(message)
