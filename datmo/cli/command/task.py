from __future__ import print_function

import shlex
import platform
import prettytable

from datmo.core.util.i18n import get as __
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.task import TaskController


class TaskCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(TaskCommand, self).__init__(home, cli_helper)

        task_parser = self.subparsers.add_parser("task", help="Task module")
        subcommand_parsers = task_parser.add_subparsers(
            title="subcommands", dest="subcommand")

        # Task run arguments
        run = subcommand_parsers.add_parser("run", help="Run task")
        run.add_argument(
            "--gpu",
            dest="gpu",
            action="store_true",
            help="Boolean if you want to run using GPUs")
        run.add_argument(
            "--ports",
            nargs="*",
            dest="ports",
            type=str,
            help="""
            Network port mapping during task (e.g. 8888:8888). Left is the host machine port and right
            is the environment port available during a run.
        """)
        # run.add_argument("--data", nargs="*", dest="data", type=str, help="Path for data to be used during the Task")
        run.add_argument(
            "--env-def",
            dest="environment_definition_filepath",
            default="",
            nargs="?",
            type=str,
            help=
            "Pass in the Dockerfile with which you want to build the environment"
        )
        run.add_argument(
            "--interactive",
            dest="interactive",
            action="store_true",
            help="Run the environment in interactive mode (keeps STDIN open)")
        run.add_argument("cmd", nargs="?", default=None)

        # Task list arguments
        ls = subcommand_parsers.add_parser("ls", help="List tasks")
        ls.add_argument(
            "--session-id",
            dest="session_id",
            default=None,
            nargs="?",
            type=str,
            help="Pass in the session id to list the tasks in that session")

        # Task stop arguments
        stop = subcommand_parsers.add_parser("stop", help="Stop tasks")
        stop.add_argument(
            "--id", dest="id", default=None, type=str, help="Task ID to stop")

        self.task_controller = TaskController(home=home)

    def run(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.task.run"))

        # Create input dictionaries
        snapshot_dict = {
            "environment_definition_filepath":
                kwargs['environment_definition_filepath']
        }

        if not isinstance(kwargs['cmd'], list):
            if platform.system() == "Windows":
                kwargs['cmd'] = kwargs['cmd']
            else:
                kwargs['cmd'] = shlex.split(kwargs['cmd'])

        task_dict = {
            "gpu": kwargs['gpu'],
            "ports": kwargs['ports'],
            "interactive": kwargs['interactive'],
            "command": kwargs['cmd']
        }

        # Create the task object
        task_obj = self.task_controller.create(task_dict)

        # Pass in the task
        try:
            updated_task_obj = self.task_controller.run(
                task_obj.id, snapshot_dict=snapshot_dict)
        except:
            self.cli_helper.echo(__("error", "cli.task.run", task_obj.id))
            return False
        return updated_task_obj

    def ls(self, **kwargs):
        session_id = kwargs.get('session_id',
                                self.task_controller.current_session.id)
        # Get all snapshot meta information
        header_list = ["id", "command", "status", "gpu", "created at"]
        t = prettytable.PrettyTable(header_list)
        task_objs = self.task_controller.list(session_id)
        for task_obj in task_objs:
            t.add_row([
                task_obj.id, task_obj.command, task_obj.status, task_obj.gpu,
                task_obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        self.cli_helper.echo(t)

        return True

    def stop(self, **kwargs):
        task_id = kwargs.get('id', None)
        self.cli_helper.echo(__("info", "cli.task.stop", task_id))
        try:
            result = self.task_controller.stop(task_id)
            if not result:
                self.cli_helper.echo(__("error", "cli.task.stop", task_id))
            return result
        except:
            self.cli_helper.echo(__("error", "cli.task.stop", task_id))
            return False
