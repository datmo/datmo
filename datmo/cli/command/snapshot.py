from __future__ import print_function

import prettytable

from datmo.core.util.i18n import get as __
from datmo.core.util.misc_functions import mutually_exclusive
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.snapshot import SnapshotController


class SnapshotCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(SnapshotCommand, self).__init__(home, cli_helper)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        snapshot_parser = self.subparsers.add_parser(
            "snapshot", help="Snapshot module")
        subcommand_parsers = snapshot_parser.add_subparsers(
            title="subcommands", dest="subcommand")

        create = subcommand_parsers.add_parser(
            "create", help="create snapshot")
        create.add_argument(
            "--message",
            "-m",
            dest="message",
            default=None,
            help="message to describe snapshot")
        create.add_argument(
            "--label",
            "-l",
            dest="label",
            default=None,
            help="Label snapshots with a category (e.g. best)")
        create.add_argument(
            "--session-id",
            dest="session_id",
            default=None,
            help="user given session id")

        create.add_argument(
            "--task-id",
            dest="task_id",
            default=None,
            help="Specify task id to pull information from")

        create.add_argument(
            "--code-id",
            dest="code_id",
            default=None,
            help="code id from code object")
        create.add_argument(
            "--commit-id",
            dest="commit_id",
            default=None,
            help="commit id from source control")

        create.add_argument(
            "--environment-id",
            dest="environment_id",
            default=None,
            help="environment id from environment object")
        create.add_argument(
            "--environment-def-path",
            dest="environment_def_path",
            default=None,
            help=
            "absolute filepath to environment definition file (e.g. /path/to/Dockerfile)"
        )

        create.add_argument(
            "--file-collection-id",
            dest="file_collection_id",
            default=None,
            help="file collection id for file collection object")
        create.add_argument(
            "--filepaths",
            dest="filepaths",
            default=None,
            nargs="*",
            help=
            "absolute paths to files or folders to include within the files of the snapshot"
        )

        create.add_argument(
            "--config-filename",
            dest="config_filename",
            default=None,
            help="filename to use to search for configuration JSON")
        create.add_argument(
            "--config-filepath",
            dest="config_filepath",
            default=None,
            help="absolute filepath to use to search for configuration JSON")

        create.add_argument(
            "--stats-filename",
            dest="stats_filename",
            default=None,
            help="filename to use to search for metrics JSON")
        create.add_argument(
            "--stats-filepath",
            dest="stats_filepath",
            default=None,
            help="absolute filepath to use to search for metrics JSON")

        delete = subcommand_parsers.add_parser(
            "delete", help="Delete a snapshot by id")
        delete.add_argument("--id", dest="id", help="snapshot id to delete")

        ls = subcommand_parsers.add_parser("ls", help="List snapshots")
        ls.add_argument(
            "--session-id",
            dest="session_id",
            default=None,
            help="Session ID to filter")
        ls.add_argument(
            "--all",
            "-a",
            dest="details",
            action="store_true",
            help="Show detailed snapshot information")

        checkout = subcommand_parsers.add_parser(
            "checkout", help="Checkout a snapshot by id")
        checkout.add_argument(
            "--id", dest="id", default=None, help="Snapshot ID")

        self.snapshot_controller = SnapshotController(home=home)

    def create(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.snapshot.create"))

        snapshot_dict = {}

        # Code
        mutually_exclusive_args = ["code_id", "commit_id"]
        mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)

        # Environment
        mutually_exclusive_args = ["environment_id", "environment_def_path"]
        mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)

        # File
        mutually_exclusive_args = ["file_collection_id", "filepaths"]
        mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)

        # Config
        mutually_exclusive_args = ["config_filepath", "config_filename"]
        mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)

        # Stats
        mutually_exclusive_args = ["stats_filepath", "stats_filename"]
        mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)

        optional_args = ["session_id", "task_id", "message", "label"]

        for arg in optional_args:
            if arg in kwargs and kwargs[arg] is not None:
                snapshot_dict[arg] = kwargs[arg]

        snapshot_obj = self.snapshot_controller.create(snapshot_dict)

        return snapshot_obj.id

    def delete(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.snapshot.delete"))
        snapshot_id = kwargs.get("id", None)
        return self.snapshot_controller.delete(snapshot_id)

    def ls(self, **kwargs):
        session_id = kwargs.get('session_id',
                                self.snapshot_controller.current_session.id)
        # Get all snapshot meta information
        detailed_info = kwargs.get('details', None)
        if detailed_info:
            header_list = [
                "id", "created at", "config", "stats", "message", "label",
                "code id", "environment id", "file collection id"
            ]
            t = prettytable.PrettyTable(header_list)
            snapshot_objs = self.snapshot_controller.list(
                session_id=session_id, visible=True)
            for snapshot_obj in snapshot_objs:
                t.add_row([
                    snapshot_obj.id,
                    snapshot_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    snapshot_obj.config, snapshot_obj.stats,
                    snapshot_obj.message, snapshot_obj.label,
                    snapshot_obj.code_id, snapshot_obj.environment_id,
                    snapshot_obj.file_collection_id
                ])
        else:
            header_list = [
                "id", "created at", "config", "stats", "message", "label"
            ]
            t = prettytable.PrettyTable(header_list)
            snapshot_objs = self.snapshot_controller.list(
                session_id=session_id, visible=True)
            for snapshot_obj in snapshot_objs:
                t.add_row([
                    snapshot_obj.id,
                    snapshot_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    snapshot_obj.config, snapshot_obj.stats,
                    snapshot_obj.message, snapshot_obj.label
                ])

        self.cli_helper.echo(t)
        return True

    def checkout(self, **kwargs):
        snapshot_id = kwargs.get("id", None)
        return self.snapshot_controller.checkout(snapshot_id)
