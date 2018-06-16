from __future__ import print_function

import os
import shlex
import platform
from datetime import datetime
# https://stackoverflow.com/questions/11301138/how-to-check-if-variable-is-string-with-python-2-and-3-compatibility/11301392?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
try:
    basestring
except NameError:
    basestring = str

from datmo.core.util.i18n import get as __
from datmo.core.util.misc_functions import mutually_exclusive, printable_string, prettify_datetime
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.task import TaskController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.util.spinner import Spinner

class ExperimentCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(ExperimentCommand, self).__init__(home, cli_helper)
        self.task_controller = TaskController(home=home)
        self.snapshot_controller = SnapshotController(home=home)
        self.spinner = Spinner()

    def run(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.task.run"))
        # Creating a task controller object
        self.task_controller = TaskController(
            home=self.project_controller.home)
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

        # Pass in the task
        try:
            self.spinner.start()
            # Create the task object
            task_obj = self.task_controller.create()
            updated_task_obj = self.task_controller.run(
                task_obj.id, snapshot_dict=snapshot_dict, task_dict=task_dict)
        except Exception as e:
            self.logger.error("%s %s" % (e, task_dict))
            self.cli_helper.echo("%s" % e)
            self.cli_helper.echo(__("error", "cli.task.run", task_obj.id))
            return False
        finally:
            self.spinner.stop()
            pass

        self.cli_helper.echo(" Ran task id: %s" % updated_task_obj.id)
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
        header_list = ["id", "command", "status", "config", "results", "created at"]
        item_dict_list = []
        for task_obj in task_objs:
            snapshot_id = task_obj.after_snapshot_id if task_obj.after_snapshot_id else task_obj.before_snapshot_id
            snapshot_config = None
            if snapshot_id:
                snapshot_obj = self.snapshot_controller.get(snapshot_id)
                snapshot_config = snapshot_obj.config
            if task_obj.results is None:
                task_results = {}
            else:
                task_results = task_obj.results
            task_results_printable = printable_string(str(task_results))
            snapshot_config_printable = printable_string(str(snapshot_config))
            item_dict_list.append({
                "id": task_obj.id,
                "command": task_obj.command,
                "status": task_obj.status,
                "config": snapshot_config_printable,
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
                    os.getcwd(), "run_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
            return task_objs
        self.cli_helper.print_items(
            header_list, item_dict_list, print_format=print_format)
        return task_objs