from datmo.cli.driver.cli_base_command import CLIBaseCommand
from datmo.cli.driver.cli_argument_parser import CLIArgumentParser
from datmo.controller.snapshot import SnapshotController

from datmo.util.exceptions import ProjectNotInitializedException

def get_parser():
    snapshot_parser = CLIArgumentParser(prog="datmo", usage="%(prog)s snapshot")
    snapshot_parser.add_argument("command", choices=["snapshot"])
    # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
    # example  "subcommand"="create"  or "subcommand"="ls"
    subcommand_parsers = snapshot_parser.add_subparsers(dest="subcommand")

    create = subcommand_parsers.add_parser("create", help="Create snapshot")
    create.add_argument("--message", "-m", dest="message", default="", help="Message to describe snapshot")
    create.add_argument("--label", "-l", dest="label", default="", help="Label snapshots with a category (e.g. best)")
    create.add_argument("--session-id", dest="session_id", default="", help="User given session id")

    create.add_argument("--task-id", dest="task_id", default=None,
                        help="Specify task id to pull information from")

    create.add_argument("--code-id", dest="code_id", default="", help="User provided code id (e.g. git revision for git)")

    create.add_argument("--environment-def-path", dest="environment_def_path", default="", help="Absolute filepath to environment definition file (e.g. /path/to/Dockerfile)")

    create.add_argument("--config-filename", dest="config_filename", default=None, help="Filename to use to search for configuration JSON")
    create.add_argument("--config-filepath", dest="config_filepath", default=None, help="Absolute filepath to use to search for configuration JSON")

    create.add_argument("--stats-filename", dest="stats_filename", default=None, help="Filename to use to search for metrics JSON")
    create.add_argument("--stats-filepath", dest="stats_filepath", default=None, help="Absolute filepath to use to search for metrics JSON")

    create.add_argument("--filepaths", dest="filepaths", default=None, nargs="*",
                        help="Absolute paths to files or folders to include within the files of the snapshot")

    delete = subcommand_parsers.add_parser("delete", help="Delete a snapshot by id")
    delete.add_argument("--id", dest="snapshot_id", help="snapshot id to delete")

    ls = subcommand_parsers.add_parser("ls", help="List snapshots")
    ls.add_argument("--session-id", dest="session_id", default=None, help="Session ID to filter")
    ls.add_argument("--session-name", dest="session_name", default=None, help="Session name to filter")
    ls.add_argument("-a", dest="details", default=True, help="Show detailed Snapshot information")

    checkout = subcommand_parsers.add_parser("checkout", help="Checkout a snapshot by id")
    checkout.add_argument("--id", dest="snapshot_id", default=None, help="Snapshot ID")

    home = subcommand_parsers.add_parser("home", help="Checkout/Reset back to initial state")

    update = subcommand_parsers.add_parser("update", help="Update Snapshot with meta information ")
    update.add_argument("--id", dest="snapshot_id", default=None, help="Snapshot id to edit")
    update.add_argument("--message", "-m", dest="message", default=None, help="Message to describe snapshot")
    update.add_argument("--label", "-l", dest="label", default=None, help="Label snapshots with a category (e.g. best)")

    update.add_argument("--config-filename", dest="config_filename", default=None,
                        help="Filename to use to search for configuration JSON")
    update.add_argument("--config-filepath", dest="config_filepath", default=None,
                        help="Absolute filepath to use to search for configuration JSON")

    update.add_argument("--stats-filename", dest="stats", default=None,
                        help="Filename to use to search for metrics JSON")
    update.add_argument("--stats-filepath", dest="stats", default=None,
                        help="Absolute filepath to use to search for metrics JSON")

    best = subcommand_parsers.add_parser("best", help="Sets the best snapshot for a model")
    best.add_argument("--id", dest="snapshot_id", default=None, help="Snapshot ID")

    #  REMOTE datmo snapshot commands
    #  TODO: decide where these go
    # push = command_parsers.add_parser("push", help="Push snapshot to remote server")
    # push.add_argument("--id", dest="snapshot_id", default=None, help="Push Snapshot data from local to Datmo remote server (use with caution if your weights files are particularly large)")
    #
    # fetch = command_parsers.add_parser("fetch", help="Fetches a snapshot from a remote server")
    # fetch.add_argument("--id", dest="snapshot_ids", nargs="+", default=None, help="Push Snapshot data from local to Datmo remote server (use with caution if your weights files are particularly large)")

    return snapshot_parser

class Snapshot(CLIBaseCommand):
    def __init__(self, home, cli_helper, dal_driver=None):
        self.cli_helper = cli_helper
        self.controller = SnapshotController(home=home,
                                             cli_helper=cli_helper,
                                             dal_driver=dal_driver)
        if not self.controller.is_initialized:
            raise ProjectNotInitializedException("exception.cli.snapshot", {
                "exception": "No project found in the current directory"
            })

        super(Snapshot, self).__init__(self.cli_helper, get_parser())

    def create(self, **kwargs):
        self.controller.create(**kwargs)


    def delete(self, snapshot_id):
        print("delete:"+snapshot_id)
        #project = DatmoProject(os.getcwd())
        #project.delete_snapshot(snapshot_id)

    def ls(self, **kwargs):
        print("ls", kwargs)

    def checkout(self, **kwargs):
        print("checkout", kwargs)

    def home(self, **kwargs):
        print("home", kwargs)

    def update(self, **kwargs):
        print("update", kwargs)

    def best(self, **kwargs):
        print("best", kwargs)








