from __future__ import print_function

import prettytable

from datmo.util.i18n import get as _
from datmo.cli.command.project import ProjectCommand
from datmo.controller.task import TaskController
from datmo.util.exceptions import ProjectNotInitializedException


class TaskCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(TaskCommand, self).__init__(home, cli_helper)

        task_parser = self.subparsers.add_parser("task", help="Task module")
        subcommand_parsers = task_parser.add_subparsers(title="subcommands", dest="subcommand")

        # Task run arguments
        run = subcommand_parsers.add_parser("run", help="Run task")
        run.add_argument("--gpu", dest="gpu", action="store_true",
                         help="Boolean if you want to run using GPUs")
        run.add_argument("--ports", nargs="*", dest="ports", type=str, help="""
            Network port mapping during task (e.g. 8888:8888). Left is the host machine port and right
            is the environment port available during a run.
        """)
        # run.add_argument("--data", nargs="*", dest="data", type=str, help="Path for data to be used during the Task")
        run.add_argument("--env-def", dest="environment_definition_filepath", default="",
                         nargs="?", type=str,
                         help="Pass in the Dockerfile with which you want to build the environment")
        run.add_argument("--interactive", dest="interactive", action="store_true",
                         help="Run the environment in interactive mode (keeps STDIN open)")
        run.add_argument("cmd", nargs="?", default=None)

        # Task list arguments
        ls = subcommand_parsers.add_parser("ls", help="List tasks")
        ls.add_argument("--session-id", dest="session_id", default=None, nargs="?", type=str,
                         help="Pass in the session id to list the tasks in that session")

        # Task stop arguments
        stop = subcommand_parsers.add_parser("stop", help="Stop tasks")
        stop.add_argument("--id", dest="id", default=None, type=str, help="Task ID to stop")

        self.task_controller = TaskController(home=home,
                                                  dal_driver=self.project_controller.dal_driver)
        if not self.project_controller.is_initialized:
            raise ProjectNotInitializedException(_("error",
                                                   "cli.project",
                                                   self.home))

    def run(self, **kwargs):
        self.cli_helper.echo(_("info", "cli.task.run"))

        # Create input dictionaries
        snapshot_dict = {
            "environment_definition_filepath":
                kwargs['environment_definition_filepath']
        }

        task_dict = {
            "gpu": kwargs['gpu'],
            "ports": kwargs['ports'],
            "interactive": kwargs['interactive'],
            "command": kwargs['cmd']
        }

        # Create the task object
        task_obj = self.task_controller.create(task_dict)

        # Pass in the task
        self.task_controller.run(task_obj.id, snapshot_dict=snapshot_dict)

        return task_obj.id

    def ls(self, **kwargs):
        session_id = kwargs.get('session_id',
                                self.task_controller.current_session.id)
        # Get all snapshot meta information
        header_list = ["id", "command", "status", "gpu", "created_at"]
        t = prettytable.PrettyTable(header_list)
        task_objs = self.task_controller.list(session_id)
        for task_obj in task_objs:
            t.add_row([task_obj.id, task_obj.command, task_obj.status, task_obj.gpu,
                       task_obj.created_at.strftime("%Y-%m-%d %H:%M:%S")])
        self.cli_helper.echo(t)
        return True

    def stop(self, **kwargs):
        id = kwargs.get('id', None)
        try:
            task_delete_dict = {"id": id}
            self.task_controller.delete(**task_delete_dict)
        except Exception:
            self.cli_helper.echo(_("error",
                                   "cli.task.delete"))
            return False
        return True







