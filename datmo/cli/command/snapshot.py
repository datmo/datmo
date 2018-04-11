from __future__ import print_function

from datmo.util.i18n import get as _
from datmo.cli.command.project import ProjectCommand
from datmo.controller.snapshot import SnapshotController
from datmo.util.exceptions import ProjectNotInitializedException


class SnapshotCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(SnapshotCommand, self).__init__(home, cli_helper)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        snapshot_parser = self.subparsers.add_parser("snapshot", help="Snapshot module")
        subcommand_parsers = snapshot_parser.add_subparsers(title="subcommands", dest="subcommand")

        create = subcommand_parsers.add_parser("create", help="Create snapshot")
        create.add_argument("--message", "-m", dest="message", default="", help="Message to describe snapshot")
        create.add_argument("--label", "-l", dest="label", default="",
                            help="Label snapshots with a category (e.g. best)")
        create.add_argument("--session-id", dest="session_id", default="", help="User given session id")

        create.add_argument("--task-id", dest="task_id", default=None,
                            help="Specify task id to pull information from")

        create.add_argument("--code-id", dest="code_id", default="",
                            help="User provided code id (e.g. git revision for git)")

        create.add_argument("--environment-def-path", dest="environment_def_path", default="",
                            help="Absolute filepath to environment definition file (e.g. /path/to/Dockerfile)")

        create.add_argument("--config-filename", dest="config_filename", default=None,
                            help="Filename to use to search for configuration JSON")
        create.add_argument("--config-filepath", dest="config_filepath", default=None,
                            help="Absolute filepath to use to search for configuration JSON")

        create.add_argument("--stats-filename", dest="stats_filename", default=None,
                            help="Filename to use to search for metrics JSON")
        create.add_argument("--stats-filepath", dest="stats_filepath", default=None,
                            help="Absolute filepath to use to search for metrics JSON")

        create.add_argument("--filepaths", dest="filepaths", default=None, nargs="*",
                            help="Absolute paths to files or folders to include within the files of the snapshot")

        delete = subcommand_parsers.add_parser("delete", help="Delete a snapshot by id")
        delete.add_argument("--id", dest="snapshot_id", help="snapshot id to delete")

        ls = subcommand_parsers.add_parser("ls", help="List snapshots")
        ls.add_argument("--session-id", dest="session_id", default=None, help="Session ID to filter")
        ls.add_argument("--session-name", dest="session_name", default=None, help="Session name to filter")
        ls.add_argument("-a", dest="details", default=True, help="Show detailed SnapshotCommand information")

        checkout = subcommand_parsers.add_parser("checkout", help="Checkout a snapshot by id")
        checkout.add_argument("--id", dest="snapshot_id", default=None, help="SnapshotCommand ID")

        # home = subcommand_parsers.add_parser("home", help="Checkout/Reset back to initial state")

        update = subcommand_parsers.add_parser("update", help="Update SnapshotCommand with meta information ")
        update.add_argument("--id", dest="snapshot_id", default=None, help="SnapshotCommand id to edit")
        update.add_argument("--message", "-m", dest="message", default=None, help="Message to describe snapshot")
        update.add_argument("--label", "-l", dest="label", default=None,
                            help="Label snapshots with a category (e.g. best)")

        update.add_argument("--config-filename", dest="config_filename", default=None,
                            help="Filename to use to search for configuration JSON")
        update.add_argument("--config-filepath", dest="config_filepath", default=None,
                            help="Absolute filepath to use to search for configuration JSON")

        update.add_argument("--stats-filename", dest="stats", default=None,
                            help="Filename to use to search for metrics JSON")
        update.add_argument("--stats-filepath", dest="stats", default=None,
                            help="Absolute filepath to use to search for metrics JSON")

        best = subcommand_parsers.add_parser("best", help="Sets the best snapshot for a model")
        best.add_argument("--id", dest="snapshot_id", default=None, help="SnapshotCommand ID")

        self.snapshot_controller = SnapshotController(home=home,
                                                      dal_driver=self.project_controller.dal_driver)
        if not self.project_controller.is_initialized:
            raise ProjectNotInitializedException("exception.cli.snapshot", {
                "exception": "No project found in the current directory"
            })

    def create(self, **kwargs):
        self.cli_helper.echo(_("info", "cli.snapshot.create"))
        self.snapshot_controller.create(**kwargs)

    def delete(self, snapshot_id):
        self.snapshot_controller.delete(snapshot_id)

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








