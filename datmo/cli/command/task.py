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

        run.add_argument('--gpu', dest='gpu', const=True, default=False, action='store', nargs='?', type=bool,
                         help='Boolean if you want to train the Model leveraging GPUs')
        run.add_argument('--ports', nargs='*', dest='ports', type=str, help='Network port(s) to open during the Task')
        run.add_argument('--data', nargs='*', dest='data', type=str, help='Path for data to be used during the Task')
        run.add_argument('--dockerfile', dest='dockerfile', default='Dockerfile', nargs='?', type=str,
                         help='Pass in the Dockerfile with which you want to build the environment')
        run.add_argument('--interactive', dest='interactive', const=True, default=False, action='store', nargs='?', type=bool,
                         help='Run the environment in interactive mode (keeps STDIN open)')
        # run.add_argument("command", nargs='?', default=None)
        run.add_argument('--cmd', dest='command', default=None, action='store', nargs='?',
                         type=str, help='Command to be run inside the container')

        # Task list arguments
        ls = subcommand_parsers.add_parser("ls", help="List tasks")
        ls.add_argument('--running', dest='running', const=True, default=False, action='store', nargs='?', type=bool,
                         help='Boolean to filter for running Tasks')
        ls.add_argument('--all', dest='all', const=True, default=False, action='store', nargs='?', type=bool,
                         help='Boolean to filter for running Tasks')

        # Task stop arguments
        stop = subcommand_parsers.add_parser("stop", help="Stop tasks")
        stop.add_argument('--running', dest='running', const=True, default=False, action='store', nargs='?', type=bool,
                          help='Boolean to filter for running Tasks')
        stop.add_argument('--id', dest='id', default=None, type=str, help='Task ID to stop')

        self.snapshot_controller = TaskController(home=home,
                                                  dal_driver=self.project_controller.dal_driver)
        # if not self.project_controller.is_initialized:
        #     raise ProjectNotInitializedException("exception.cli.task", {
        #         "exception": "No project found in the current directory"
        #     })

    def run(self, **kwargs):
        self.cli_helper.echo(_("info", "cli.task.run"))
        print("run", kwargs)

    def ls(self, **kwargs):
        print("ls", kwargs)

    def stop(self, **kwargs):
        print("stop", kwargs)







