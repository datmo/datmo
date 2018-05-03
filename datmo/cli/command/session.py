from __future__ import print_function

import prettytable

from datmo.core.util.i18n import get as __
from datmo.core.controller.session import SessionController
from datmo.cli.command.project import ProjectCommand


class SessionCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(SessionCommand, self).__init__(home, cli_helper)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        snapshot_parser = self.subparsers.add_parser(
            "session", help="Session module")
        subcommand_parsers = snapshot_parser.add_subparsers(
            title="subcommands", dest="subcommand")

        create = subcommand_parsers.add_parser("create", help="Create session")
        create.add_argument(
            "--name", "-m", dest="name", default="", help="Session name")
        create.add_argument(
            "--current",
            dest="current",
            action="store_false",
            help="Boolean if you want to switch to this session")

        delete = subcommand_parsers.add_parser(
            "delete", help="Delete a snapshot by id")
        delete.add_argument(
            "--name", dest="name", help="Name of session to delete")

        ls = subcommand_parsers.add_parser("ls", help="List sessions")

        checkout = subcommand_parsers.add_parser(
            "select", help="Select a session")
        checkout.add_argument(
            "--name", dest="name", help="Name of session to select")

        self.session_controller = SessionController(home=home)

    def create(self, **kwargs):
        name = kwargs.get('name')
        self.session_controller.create(kwargs)
        self.cli_helper.echo(__("info", "cli.session.create", name))
        return True

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
        sessions = self.session_controller.list()
        header_list = ["name", "selected", "tasks", "snapshots"]
        t = prettytable.PrettyTable(header_list)
        for sess in sessions:
            snapshot_count = len(
                self.session_controller.dal.snapshot.query({
                    "session_id": sess.id,
                    "model_id": self.session_controller.model.id
                }))
            task_count = len(
                self.session_controller.dal.task.query({
                    "session_id": sess.id,
                    "model_id": self.session_controller.model.id
                }))
            t.add_row([sess.name, sess.current, task_count, snapshot_count])

        self.cli_helper.echo(t)

        return True
