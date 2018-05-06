from __future__ import print_function

import prettytable

from datmo.core.util.i18n import get as __
from datmo.core.util.misc_functions import mutually_exclusive
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.snapshot import SnapshotController


class SnapshotCommand(ProjectCommand):
    def __init__(self, home, cli_helper, parser):
        super(SnapshotCommand, self).__init__(home, cli_helper, parser)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        self.snapshot_controller = SnapshotController(home=home)

    def create(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.snapshot.create"))

        snapshot_dict = {"visible": True}

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
        # List of ids shown
        listed_snapshot_ids = []
        if detailed_info:
            header_list = [
                "id", "created at", "config", "stats", "message", "label",
                "code id", "environment id", "file collection id"
            ]
            t = prettytable.PrettyTable(header_list)
            snapshot_objs = self.snapshot_controller.list(
                session_id=session_id,
                visible=True,
                sort_key='created_at',
                sort_order='descending')
            for snapshot_obj in snapshot_objs:
                t.add_row([
                    snapshot_obj.id,
                    snapshot_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    snapshot_obj.config, snapshot_obj.stats,
                    snapshot_obj.message, snapshot_obj.label,
                    snapshot_obj.code_id, snapshot_obj.environment_id,
                    snapshot_obj.file_collection_id
                ])
                listed_snapshot_ids.append(snapshot_obj.id)
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
                listed_snapshot_ids.append(snapshot_obj.id)

        self.cli_helper.echo(t)
        return listed_snapshot_ids

    def checkout(self, **kwargs):
        snapshot_id = kwargs.get("id", None)
        return self.snapshot_controller.checkout(snapshot_id)
