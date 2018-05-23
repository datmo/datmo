from __future__ import print_function

import shlex
import platform
import prettytable
# https://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility/11301392?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
try:
    basestring
except NameError:
    basestring = str

from datmo.core.util.i18n import get as __
from datmo.core.util.misc_functions import mutually_exclusive, printable_string, prettify_datetime
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.task import TaskController
from datmo.core.util.exceptions import RequiredArgumentMissing


class TaskCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(TaskCommand, self).__init__(home, cli_helper)
        self.task_controller = TaskController(home=home)

    def task(self):
        self.parse(["--help"])
        return True

    def run(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.task.run"))

        # Create input dictionaries
        snapshot_dict = {}
        if kwargs['environment_definition_filepath']:
            snapshot_dict["environment_definition_filepath"] =\
                kwargs['environment_definition_filepath']
        task_dict = {
            "ports": kwargs['ports'],
            "interactive": kwargs['interactive']
        }
        if not isinstance(kwargs['cmd'], list):
            if platform.system() == "Windows":
                task_dict['command'] = kwargs['cmd']
            elif isinstance(kwargs['cmd'], basestring):
                task_dict['command_list'] = shlex.split(kwargs['cmd'])
        else:
            task_dict['command_list'] = kwargs['cmd']

        # Create the task object)
        task_obj = self.task_controller.create()

        # Pass in the task
        try:
            updated_task_obj = self.task_controller.run(
                task_obj.id, snapshot_dict=snapshot_dict, task_dict=task_dict)
        except Exception as e:
            self.logger.error("%s %s" % (e, task_dict))
            self.cli_helper.echo(__("error", "cli.task.run", task_obj.id))
            return False
        self.cli_helper.echo("Ran task id: %s" % updated_task_obj.id)
        return updated_task_obj

    def ls(self, **kwargs):
        session_id = kwargs.get('session_id',
                                self.task_controller.current_session.id)
        # Get all snapshot meta information
        header_list = ["id", "command", "status", "results", "created at"]
        t = prettytable.PrettyTable(header_list)
        task_objs = self.task_controller.list(
            session_id, sort_key='created_at', sort_order='descending')
        for task_obj in task_objs:
            task_results_printable = printable_string(str(task_obj.results))
            t.add_row([
                task_obj.id, task_obj.command, task_obj.status,
                task_results_printable,
                prettify_datetime(task_obj.created_at)
            ])
        self.cli_helper.echo(t)

        return True

    def stop(self, **kwargs):
        input_dict = {}
        mutually_exclusive(["id", "all"], kwargs, input_dict)
        if "id" in input_dict:
            self.cli_helper.echo(__("info", "cli.task.stop", input_dict['id']))
        elif "all" in input_dict:
            self.cli_helper.echo(__("info", "cli.task.stop.all"))
        else:
            raise RequiredArgumentMissing()
        try:
            if "id" in input_dict:
                result = self.task_controller.stop(task_id=input_dict['id'])
                if not result:
                    self.cli_helper.echo(
                        __("error", "cli.task.stop", input_dict['id']))
                else:
                    self.cli_helper.echo(
                        __("info", "cli.task.stop.success", input_dict['id']))
            if "all" in input_dict:
                result = self.task_controller.stop(all=input_dict['all'])
                if not result:
                    self.cli_helper.echo(__("error", "cli.task.stop.all"))
                else:
                    self.cli_helper.echo(
                        __("info", "cli.task.stop.all.success"))
            return result
        except Exception:
            if "id" in input_dict:
                self.cli_helper.echo(
                    __("error", "cli.task.stop", input_dict['id']))
            if "all" in input_dict:
                self.cli_helper.echo(__("error", "cli.task.stop.all"))
            return False
