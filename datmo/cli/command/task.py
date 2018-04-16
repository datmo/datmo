from __future__ import print_function

import os
import prettytable

from datmo.util.i18n import get as _
from datmo.cli.command.project import ProjectCommand
from datmo.controller.task import TaskController
from datmo.util.exceptions import ProjectNotInitializedException, EntityNotFound


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
        run.add_argument('--dockerfile', dest='dockerfile', default=os.path.join(self.project_controller.home,
                                                                                 'Dockerfile'),
                         nargs='?', type=str,
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
        task_arg_dict = {
            'command': self.args.command,
            'dockerfile': self.args.dockerfile,
            'interactive': self.args.interactive,
            'gpu': self.args.gpu,
            'ports': self.args.ports,
            'data': self.args.data
        }
        # Create the task object
        task_obj = self.task_controller.create(task_arg_dict)

        # TODO Update after changes in snapshot and task controller
        # Create environment_driver definition
        if self.args.dockerfile:
            env_def_path = self.args.dockerfile
        else:
            env_def_path = os.path.join(self.task_controller.home,
                                        "Dockerfile")
        with open(env_def_path, "w") as f:
            f.write(str("FROM datmo/xgboost:cpu"))

        # Create config
        config_filepath = os.path.join(self.task_controller.home,
                                       "config.json")
        with open(config_filepath, "w") as f:
            f.write(str("{}"))

        # Create stats
        stats_filepath = os.path.join(self.task_controller.home,
                                      "stats.json")
        with open(stats_filepath, "w") as f:
            f.write(str("{}"))

        snapshot_arg_dict = {
            "filepaths": [],
            "environment_definition_filepath": env_def_path,
            "config_filename": config_filepath,
            "stats_filename": stats_filepath,
            "config": {},
            "stats": {}
        }
        # Pass in the task id and snapshot arguments for the run
        self.task_controller.run(task_obj.id, snapshot_arg_dict)

        return task_obj.id

    def ls(self, **kwargs):
        # Get all snapshot meta information
        header_list = ['id', 'command', 'status', 'gpu', 'created_at']
        t = prettytable.PrettyTable(header_list)
        session_obj = self.task_controller.current_session
        task_objs = self.task_controller.list(session_obj.id)
        for task_obj in task_objs:
            t.add_row([task_obj.id, task_obj.command, task_obj.status, task_obj.gpu,
                       task_obj.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        print(t)
        return True

    def stop(self, **kwargs):
        try:
            id = self.args.id
            task_delete_dict = {'id': id}
            self.task_controller.delete(**task_delete_dict)
        except Exception:
            raise EntityNotFound(_("error",
                                   "cli.task.delete"))
        return True







