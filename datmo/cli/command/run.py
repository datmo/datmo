from __future__ import print_function

import os
import sys
import shlex
import platform
from datetime import datetime
# https://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility/11301392?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
try:
    basestring
except NameError:
    basestring = str

from datmo.core.util.i18n import get as __
from datmo.core.util.misc_functions import mutually_exclusive, printable_object
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.task import TaskController
from datmo.core.controller.snapshot import SnapshotController
from datmo.cli.driver.helper import Helper
from datmo.core.entity.run import Run
from datmo.core.util.exceptions import RequiredArgumentMissing
from datmo.core.util.misc_functions import prettify_datetime


class RunCommand(ProjectCommand):
    def __init__(self, cli_helper):
        super(RunCommand, self).__init__(cli_helper)

    @Helper.notify_environment_active(TaskController)
    @Helper.notify_no_project_found
    def run(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.run.run"))
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

        data_paths = kwargs['data']
        # Run task and return Task object result
        task_obj = self.task_run_helper(
            task_dict, snapshot_dict, "cli.run.run", data_paths=data_paths)
        if not task_obj:
            return False
        # Creating the run object
        run_obj = Run(task_obj)
        return run_obj

    @Helper.notify_no_project_found
    def ls(self, **kwargs):
        print_format = kwargs.get('format', "table")
        download = kwargs.get('download', None)
        download_path = kwargs.get('download_path', None)
        # Get all task meta information
        self.task_controller = TaskController()
        task_objs = self.task_controller.list(
            sort_key="created_at", sort_order="descending")
        header_list = [
            "id", "command", "type", "status", "config", "results",
            "created at"
        ]
        item_dict_list = []
        run_obj_list = []
        for task_obj in task_objs:
            # Create a new Run Object from Task Object
            run_obj = Run(task_obj)
            task_results_printable = printable_object(run_obj.results)
            snapshot_config_printable = printable_object(run_obj.config)
            item_dict_list.append({
                "id": run_obj.id,
                "command": run_obj.command,
                "type": run_obj.type,
                "status": run_obj.status,
                "config": snapshot_config_printable,
                "results": task_results_printable,
                "created at": prettify_datetime(run_obj.created_at)
            })
            run_obj_list.append(run_obj)
        if download:
            if not download_path:
                # download to current working directory with timestamp
                current_time = datetime.utcnow()
                epoch_time = datetime.utcfromtimestamp(0)
                current_time_unix_time_ms = (
                    current_time - epoch_time).total_seconds() * 1000.0
                download_path = os.path.join(
                    os.getcwd(), "run_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
            return task_objs
        self.cli_helper.print_items(
            header_list, item_dict_list, print_format=print_format)
        return run_obj_list

    @Helper.notify_environment_active(TaskController)
    @Helper.notify_no_project_found
    def rerun(self, **kwargs):
        self.task_controller = TaskController()
        # Get task id
        task_id = kwargs.get("id", None)
        self.cli_helper.echo(__("info", "cli.run.rerun", task_id))
        # Create the task_obj
        task_obj = self.task_controller.get(task_id)
        # Create the run obj
        run_obj = Run(task_obj)
        # Select the initial snapshot if it's a script else the final snapshot
        initial = True if run_obj.type == 'script' else False
        environment_id = run_obj.environment_id
        command = task_obj.command_list
        snapshot_id = run_obj.core_snapshot_id if not initial else run_obj.before_snapshot_id

        # Checkout to the core snapshot id before rerunning the task
        self.snapshot_controller = SnapshotController()
        try:
            checkout_success = self.snapshot_controller.checkout(snapshot_id)
        except Exception:
            self.cli_helper.echo(__("error", "cli.snapshot.checkout.failure"))
            sys.exit(1)

        if checkout_success:
            self.cli_helper.echo(
                __("info", "cli.snapshot.checkout.success", snapshot_id))

        # Rerunning the task
        # Create input dictionary for the new task
        snapshot_dict = {}
        snapshot_dict["environment_id"] = environment_id
        task_dict = {
            "ports": task_obj.ports,
            "interactive": task_obj.interactive,
            "mem_limit": task_obj.mem_limit,
            "command_list": command,
            "data_file_path_map": task_obj.data_file_path_map,
            "data_directory_path_map": task_obj.data_directory_path_map,
            "workspace": task_obj.workspace
        }
        # Run task and return Task object result
        new_task_obj = self.task_run_helper(task_dict, snapshot_dict,
                                            "cli.run.run")
        if not new_task_obj:
            return False
        # Creating the run object
        new_run_obj = Run(new_task_obj)
        return new_run_obj

    @Helper.notify_environment_active(TaskController)
    @Helper.notify_no_project_found
    def stop(self, **kwargs):
        self.task_controller = TaskController()
        input_dict = {}
        mutually_exclusive(["id", "all"], kwargs, input_dict)
        if "id" in input_dict:
            self.cli_helper.echo(__("info", "cli.run.stop", input_dict['id']))
        elif "all" in input_dict:
            self.cli_helper.echo(__("info", "cli.run.stop.all"))
        else:
            raise RequiredArgumentMissing()
        try:
            if "id" in input_dict:
                result = self.task_controller.stop(task_id=input_dict['id'])
                if not result:
                    self.cli_helper.echo(
                        __("error", "cli.run.stop", input_dict['id']))
                else:
                    self.cli_helper.echo(
                        __("info", "cli.run.stop.success", input_dict['id']))
            if "all" in input_dict:
                result = self.task_controller.stop(all=input_dict['all'])
                if not result:
                    self.cli_helper.echo(__("error", "cli.run.stop.all"))
                else:
                    self.cli_helper.echo(
                        __("info", "cli.run.stop.all.success"))
            return result
        except Exception:
            if "id" in input_dict:
                self.cli_helper.echo(
                    __("error", "cli.run.stop", input_dict['id']))
            if "all" in input_dict:
                self.cli_helper.echo(__("error", "cli.run.stop.all"))
            return False

    @Helper.notify_environment_active(TaskController)
    @Helper.notify_no_project_found
    def delete(self, **kwargs):
        self.task_controller = TaskController()
        task_id = kwargs.get("id", None)
        if task_id:
            self.cli_helper.echo(__("info", "cli.run.delete", task_id))
        else:
            raise RequiredArgumentMissing()
        try:
            # Delete the task for the run
            result = self.task_controller.delete(task_id)
            if result:
                self.cli_helper.echo(
                    __("info", "cli.run.delete.success", task_id))
            return result
        except Exception:
            self.cli_helper.echo(__("error", "cli.run.delete", task_id))
            return False
