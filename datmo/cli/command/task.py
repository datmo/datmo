from __future__ import print_function
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

        run.add_argument('--gpu', dest='gpu', action='store_true',
                         help='Boolean if you want to train the Model leveraging GPUs')
        run.add_argument('--ports', nargs='*', dest='ports', type=str, help='Network port(s) to open during the Task')
        run.add_argument('--data', nargs='*', dest='data', type=str, help='Path for data to be used during the Task')
        run.add_argument('--dockerfile', dest='dockerfile', default='Dockerfile', nargs='?', type=str,
                         help='Pass in the Dockerfile with which you want to build the environment')
        run.add_argument('--interactive', dest='interactive', action='store_true',
                         help='Run the environment in interactive mode (keeps STDIN open)')
        run.add_argument("command", nargs='?', default=None)

        # Task list arguments
        ls = subcommand_parsers.add_parser("ls", help="List tasks")
        ls.add_argument('--session-id', dest='session_id', default=None, nargs='?', type=str,
                         help='Pass in the session id to list the tasks in that session')

        # Task stop arguments
        stop = subcommand_parsers.add_parser("stop", help="Stop tasks")
        stop.add_argument('--id', dest='id', default=None, type=str, help='Task ID to stop')

        self.task_controller = TaskController(home=home,
                                                  dal_driver=self.project_controller.dal_driver)
        if not self.project_controller.is_initialized:
            raise ProjectNotInitializedException(_("error",
                                                   "cli.project",
                                                   self.home))

    def run(self, **kwargs):
        self.cli_helper.echo(_("info", "cli.task.run"))
        task_obj = self.task_controller.create(**kwargs)
        self.task_controller.run(task_obj.id)

    def ls(self, **kwargs):
        print("ls", kwargs)
        session_obj = self.task_controller.current_session
        self.task_controller.list(session_obj.id)

    def stop(self, **kwargs):
        print("stop", kwargs)
        self.task_controller.delete(**kwargs)








