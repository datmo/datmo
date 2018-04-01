import sys
from datmo.util.i18n import get as _
from datmo.cli.driver.cli_helper import CLIHelper
from datmo.cli.driver.cli_argument_parser import CLIArgumentParser
from datmo.util.exceptions import CLIArgumentException

def get_parser():
    parser = CLIArgumentParser(prog='datmo', usage="""datmo COMMAND [SUBCOMMANDS] ARGS 

        Datmo is a command line utility to enable tracking of data science projects. 
        It uses many of the tools you are already familiar with and combines them into a snapshot
        which allows you to keep track of 5 components at once

        1) Source Code
        2) Dependency Environment
        3) Large Files
        4) Project Configurations
        5) Project Metrics
        """)
    parser.add_argument('command', help='Command to run')
    return parser

def main():
    cli_helper = CLIHelper()
    parser = get_parser()
    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    args = parser.parse_args(sys.argv[1:2])

    command_class = \
        cli_helper.get_command_class(args.command)

    try:
        command_instance = command_class(cli_helper)
    except TypeError as ex:
        cli_helper.echo(_("cli.exception", ex.message))
        sys.exit()

    try:
        command_instance.parse(sys.argv[1:])
    except CLIArgumentException as ex:
        cli_helper.echo(_("cli.exception", ex.message))
        sys.exit()

    try:
        command_instance.execute()
    except Exception as ex:
        cli_helper.echo(_("cli.exception", ex.message))

if __name__ == "__main__":
    main()