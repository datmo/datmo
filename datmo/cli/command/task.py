from __future__ import print_function

import os
from datetime import datetime
import shlex
import platform
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

        # Environment
        if kwargs.get("environment_id", None) or kwargs.get(
                "environment_paths", None):
            mutually_exclusive_args = ["environment_id", "environment_paths"]
            mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)
        task_dict = {
            "ports": kwargs['ports'],
            "interactive": kwargs['interactive'],
            "mem_limit": kwargs['mem_limit']
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
        print_format = kwargs.get('format', "table")
        download = kwargs.get('download', None)
        download_path = kwargs.get('download_path', None)
        # Get all task meta information
        task_objs = self.task_controller.list(
            session_id, sort_key='created_at', sort_order='descending')
        header_list = ["id", "command", "status", "results", "created at"]
        item_dict_list = []
        for task_obj in task_objs:
            task_results_printable = printable_string(str(task_obj.results))
            item_dict_list.append({
                "id": task_obj.id,
                "command": task_obj.command,
                "status": task_obj.status,
                "results": task_results_printable,
                "created at": prettify_datetime(task_obj.created_at)
            })
        if download:
            if not download_path:
                # download to current working directory with timestamp
                current_time = datetime.utcnow()
                epoch_time = datetime.utcfromtimestamp(0)
                current_time_unix_time_ms = (
                    current_time - epoch_time).total_seconds() * 1000.0
                download_path = os.path.join(
                    os.getcwd(), "task_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
            return task_objs
        self.cli_helper.print_items(
            header_list, item_dict_list, print_format=print_format)
        return task_objs

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
