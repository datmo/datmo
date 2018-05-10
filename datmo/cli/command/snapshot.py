from __future__ import print_function

import prettytable

from datmo.core.util.i18n import get as __
from datmo.core.util.misc_functions import mutually_exclusive
from datmo.core.util.exceptions import (SnapshotCreateFromTaskArgs)
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.snapshot import SnapshotController


class SnapshotCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(SnapshotCommand, self).__init__(home, cli_helper)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        self.snapshot_controller = SnapshotController(home=home)

    def usage(self):
        self.cli_helper.echo(__("argparser", "cli.snapshot.usage"))

    def snapshot(self):
        self.parse(["snapshot", "--help"])
        return True

    def create(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.snapshot.create"))
        task_id = kwargs.get("task_id", None)
        # creating snapshot with task id if it exists
        if task_id is not None:
            excluded_args = [
                "code_id", "commit_id", "environment_id",
                "environment_definition_filepath", "file_collection_id",
                "filepaths", "config_filepath", "config_filename",
                "stats_filepath", "stats_filename"
            ]
            for arg in excluded_args:
                if arg in kwargs and kwargs[arg] is not None:
                    raise SnapshotCreateFromTaskArgs(
                        "error", "cli.snapshot.create.task.args", arg)

            message = kwargs.get("message", None)
            label = kwargs.get("label", None)
            # Create a new core snapshot object
            snapshot_task_obj = self.snapshot_controller.create_from_task(
                message, task_id, label=label)
            self.cli_helper.echo(
                "Created snapshot id: %s" % snapshot_task_obj.id)
            return snapshot_task_obj.id
        else:
            # creating snapshot without task id
            snapshot_dict = {"visible": True}

            # Code
            if kwargs.get("code_id", None) or kwargs.get("commit_id", None):
                mutually_exclusive_args = ["code_id", "commit_id"]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)

            # Environment
            if kwargs.get("environment_id", None) or kwargs.get(
                    "environment_definition_filepath", None):
                mutually_exclusive_args = [
                    "environment_id", "environment_definition_filepath"
                ]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)

            # File
            if kwargs.get("file_collection_id", None) or kwargs.get(
                    "filepaths", None):
                mutually_exclusive_args = ["file_collection_id", "filepaths"]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)

            # Config
            if kwargs.get("config_filepath", None) or kwargs.get(
                    "config_filename", None):
                mutually_exclusive_args = [
                    "config_filepath", "config_filename"
                ]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)

            # Stats
            if kwargs.get("stats_filepath", None) or kwargs.get(
                    "stats_filename", None):
                mutually_exclusive_args = ["stats_filepath", "stats_filename"]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)

            optional_args = ["session_id", "message", "label"]

            for arg in optional_args:
                if arg in kwargs and kwargs[arg] is not None:
                    snapshot_dict[arg] = kwargs[arg]

            snapshot_obj = self.snapshot_controller.create(snapshot_dict)
            self.cli_helper.echo(
                __("info", "cli.snapshot.create.success", snapshot_obj.id))
            return snapshot_obj.id

    def delete(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.snapshot.delete"))
        snapshot_id = kwargs.get("id", None)
        self.cli_helper.echo(
            __("info", "cli.snapshot.delete.success", snapshot_id))
        return self.snapshot_controller.delete(snapshot_id)

    def ls(self, **kwargs):
        session_id = kwargs.get('session_id',
                                self.snapshot_controller.current_session.id)
        # Get all snapshot meta information
        detailed_info = kwargs.get('details', None)
        # List of ids shown
        listed_snapshot_ids = []
        snapshot_objs = self.snapshot_controller.list(
            session_id=session_id,
            visible=True,
            sort_key='created_at',
            sort_order='descending')
        if detailed_info:
            header_list = [
                "id", "created at", "config", "stats", "message", "label",
                "code id", "environment id", "file collection id"
            ]
            t = prettytable.PrettyTable(header_list)
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
        checkout_success = self.snapshot_controller.checkout(snapshot_id)
        if checkout_success:
            self.cli_helper.echo(
                __("info", "cli.snapshot.checkout.success", snapshot_id))
        return self.snapshot_controller.checkout(snapshot_id)
