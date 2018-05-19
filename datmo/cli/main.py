#!/usr/bin/python

import os
import sys

from datmo.cli.command.base import BaseCommand
from datmo.cli.driver.helper import Helper
from datmo.core.util.exceptions import CLIArgumentError
from datmo.core.util.i18n import get as __
from datmo.core.util.logger import DatmoLogger
from datmo.config import Config

#from datmo.core.util.misc_functions import get_logger, create_logger


def main():
    cli_helper = Helper()
    # Config is required to run first so it can
    # initialize/find datmo home directory (.datmo)
    # This is required for logging to place the logs in a
    # place for the user.
    config = Config()

    log = DatmoLogger.get_logger(__name__)
    log.info("handling command %s", config.home)

    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    # args = parser.parse_args(sys.argv[1:2])

    if len(sys.argv) > 1 and \
        sys.argv[1] in cli_helper.get_command_choices():
        command_name = sys.argv[1]
        if command_name == "init":
            command_name = "project"
        elif command_name == "version" or \
            command_name == "--version" or \
            command_name == "-v":
            command_name = "project"
            sys.argv[1] = "version"
        elif command_name == "status":
            command_name = "project"
            sys.argv[1] = "status"
        elif command_name == "cleanup":
            command_name = "project"
            sys.argv[1] = "cleanup"
        command_class = cli_helper.get_command_class(command_name)
    else:
        command_class = BaseCommand

    # instantiate the command class
    try:
        command_instance = command_class(os.getcwd(), cli_helper)
    except TypeError as ex:
        cli_helper.echo(__("error", "cli.general", str(ex)))
        return 1

    # parse the command line arguments
    try:
        command_instance.parse(sys.argv[1:])
    except CLIArgumentError as ex:
        cli_helper.echo(__("error", "cli.general", str(ex)))
        return 1

    try:
        command_instance.execute()
        return 0
    except Exception as ex:
        cli_helper.echo(__("error", "cli.general", str(ex)))
        return 1
