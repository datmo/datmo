import os
import sys

from datmo.core.util.i18n import get as __
from datmo.cli.driver.helper import Helper
from datmo.cli.command.base import BaseCommand
from datmo.core.util.exceptions import CLIArgumentException


def main():
    cli_helper = Helper()

    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    # args = parser.parse_args(sys.argv[1:2])

    if len(sys.argv) > 1 and \
        sys.argv[1] in cli_helper.get_command_choices():
        command_name = sys.argv[1]
        if command_name == "init":
            command_name = "project"
        command_class = \
            cli_helper.get_command_class(command_name)
    else:
        command_class = BaseCommand

    try:
        command_instance = command_class(os.getcwd(), cli_helper)
    except TypeError as ex:
        cli_helper.echo(__("error", "cli.general", str(ex)))
        sys.exit()

    try:
        command_instance.parse(sys.argv[1:])
    except CLIArgumentException as ex:
        cli_helper.echo(__("error", "cli.general", str(ex)))
        sys.exit()

    try:
        command_instance.execute()
    except Exception as ex:
        cli_helper.echo(__("error", "cli.general", str(ex)))


if __name__ == "__main__":
    main()
