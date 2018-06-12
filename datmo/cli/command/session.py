from __future__ import print_function

import os
from datetime import datetime

from datmo.core.util.i18n import get as __
from datmo.core.controller.session import SessionController
from datmo.cli.command.project import ProjectCommand


class SessionCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(SessionCommand, self).__init__(home, cli_helper)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        self.session_controller = SessionController(home=home)

    def session(self):
        self.parse(["--help"])
        return True

    def create(self, **kwargs):
        name = kwargs.get('name')
        session_obj = self.session_controller.create(kwargs)
        self.cli_helper.echo(__("info", "cli.session.create", name))
        return session_obj

    def delete(self, **kwargs):
        name = kwargs.get('name')
        if self.session_controller.delete_by_name(name):
            self.cli_helper.echo(__("info", "cli.session.delete", name))
            return True

    def select(self, **kwargs):
        name = kwargs.get("name")
        self.cli_helper.echo(__("info", "cli.session.select", name))
        return self.session_controller.select(name)

    def ls(self, **kwargs):
        print_format = kwargs.get('format', "table")
        download = kwargs.get('download', None)
        download_path = kwargs.get('download_path', None)
        sessions = self.session_controller.list(
            sort_key="created_at", sort_order="descending")
        header_list = ["name", "selected", "tasks", "snapshots"]
        item_dict_list = []
        for session_obj in sessions:
            snapshot_count = len(
                self.session_controller.dal.snapshot.query({
                    "session_id": session_obj.id,
                    "model_id": self.session_controller.model.id
                }))
            task_count = len(
                self.session_controller.dal.task.query({
                    "session_id": session_obj.id,
                    "model_id": self.session_controller.model.id
                }))
            item_dict_list.append({
                "name": session_obj.name,
                "selected": str(session_obj.current),
                "tasks": str(task_count),
                "snapshots": str(snapshot_count)
            })
        if download:
            if not download_path:
                # download to current working directory with timestamp
                current_time = datetime.utcnow()
                epoch_time = datetime.utcfromtimestamp(0)
                current_time_unix_time_ms = (
                    current_time - epoch_time).total_seconds() * 1000.0
                download_path = os.path.join(
                    os.getcwd(),
                    "session_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
            return sessions
        self.cli_helper.print_items(
            header_list, item_dict_list, print_format=print_format)
        return sessions
