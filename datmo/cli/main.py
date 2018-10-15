#!/usr/bin/python

import os
import sys

from datmo.cli.command.base import BaseCommand
from datmo.cli.driver.helper import Helper
from datmo.core.util.exceptions import CLIArgumentError
from datmo.core.util.i18n import get as __
from datmo.core.util.logger import DatmoLogger
from datmo.config import Config


def main():
    cli_helper = Helper()
    # Config is required to run first so it can
    # initialize/find datmo home directory (.datmo)
    # This is required for logging to place the logs in a
    # place for the user.
    config = Config()
    config.set_home(os.getcwd())

    log = DatmoLogger.get_logger(__name__)
    log.info("handling command %s", config.home)

    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    # args = parser.parse_args(sys.argv[1:2])
    if len(sys.argv) > 1 and \
        sys.argv[1] in cli_helper.get_command_choices():
        command_name = sys.argv[1]
        # commands in project.py
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
        elif command_name == "dashboard":
            command_name = "project"
            sys.argv[1] = "dashboard"
        elif command_name == "configure":
            command_name = "project"
            sys.argv[1] = "configure"
        # commands in workspace.py
        elif command_name in ["notebook", "jupyterlab", "terminal", "rstudio"]:
            sys.argv[1] = command_name
            command_name = "workspace"
        # commands in run.py
        elif command_name == "rerun":
            command_name = "run"
            sys.argv[1] = "rerun"
        elif command_name == "run":
            if len(sys.argv) == 2:
                command_name = "run"
                sys.argv.append("--help")
            else:
                command_name = "run"
        elif command_name == "stop":  # stop command in run.py
            if len(sys.argv) == 2:
                command_name = "run"
                sys.argv.append("--help")
            else:
                command_name = "run"
        elif command_name == "ls":  # ls command in run.py
            command_name = "run"
        elif command_name == "delete":  # delete command in run.py
            command_name = "run"
        command_class = cli_helper.get_command_class(command_name)
    elif len(sys.argv) == 1:
        command_name = "datmo_command"
        command_class = cli_helper.get_command_class(command_name)
    else:
        command_class = BaseCommand

    # instantiate the command class
    try:
        command_instance = command_class(cli_helper)
    except TypeError as ex:
        cli_helper.echo(__("error", "cli.general", "%s %s" % (type(ex), ex)))
        return 1

    # parse the command line arguments
    try:
        command_instance.parse(sys.argv[1:])
    except CLIArgumentError as ex:
        cli_helper.echo(__("error", "cli.general", "%s %s" % (type(ex), ex)))
        return 1

    try:
        command_instance.execute()
        return 0
    except Exception as ex:
        cli_helper.echo(__("error", "cli.general", "%s %s" % (type(ex), ex)))
        return 1
