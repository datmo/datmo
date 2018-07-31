#!/usr/bin/python

from datmo.config import Config
from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import ClassMethodNotFound, PathDoesNotExist
from datmo.cli.parser import get_datmo_parser
from datmo.core.controller.task import TaskController
from datmo.core.util.logger import DatmoLogger
from datmo.core.util.misc_functions import parameterized, parse_paths

class BaseCommand(object):
    def __init__(self, cli_helper):
        self.home = Config().home
        self.cli_helper = cli_helper
        self.logger = DatmoLogger.get_logger(__name__)
        self.parser = get_datmo_parser()

    def parse(self, args):
        try:
            self.display_usage_message(args)
            self.args = self.parser.parse_args(args)
        except SystemExit:
            self.args = True
            pass

    def display_usage_message(self, args):
        """ Checks to see if --help or -h is passed in, and if so it calls our usage()
        if it exists.

        Since argparser thinks it is clever and automatically
        handles [--help, -h] we need a hook to be able to display
        our own usage notes before argparse

        Parameters
        ----------
        args : array[string]
            command arguments
        """

        is_help = -1
        if "--help" in args:
            is_help = args.index("--help")
        if is_help == -1 and "-h" in args:
            is_help = args.index("-h")

        if is_help > -1 and hasattr(self, "usage"):
            self.usage()

    def execute(self):
        """
        Calls the method if it exists on this object, otherwise
        call a default method name (module name)

        Raises
        ------
        ClassMethodNotFound
            If the Class method is not found
        """
        # Sometimes eg(--help) the parser automagically handles the entire response
        # and calls exit.  If this happens, self.args is set to True
        # in base.parse.   Simply return True
        if self.args is True: return True

        if getattr(self.args, "command") is None:
            self.args.command = "datmo"

        command_args = vars(self.args).copy()
        # use command name if it exists,
        # otherwise use the module name
        function_name = None
        method = None

        try:
            if "subcommand" in command_args and command_args['subcommand'] is not None:
                function_name = getattr(self.args, "subcommand",
                                        self.args.command)
                method = getattr(self, function_name)
            else:
                function_name = getattr(self.args, "command",
                                        self.args.command)
                method = getattr(self, function_name)
        except AttributeError:
            raise ClassMethodNotFound(
                __("error", "cli.general.method.not_found",
                   (self.args.command, function_name)))

        # remove extraneous options that the method should need to care about
        if "command" in command_args:
            del command_args["command"]
        if "subcommand" in command_args:
            del command_args["subcommand"]

        if method is None:
            raise ClassMethodNotFound(
                __("error", "cli.general.method.not_found",
                   (self.args.command, method)))

        method_result = method(**command_args)
        return method_result

    def task_run_helper(self, task_dict, snapshot_dict, error_identifier, data_paths=None):
        """
        Run task with given parameters and provide error identifier

        Parameters
        ----------
        task_dict : dict
            input task dictionary for task run controller
        snapshot_dict : dict
            input snapshot dictionary for task run controller
        error_identifier : str
            identifier to print error
        data_paths : list
            list of data paths being passed for task run

        Returns
        -------
        Task or False
            the Task object which completed its run with updated parameters.
            returns False if an error occurs
        """
        self.task_controller = TaskController()
        task_obj = self.task_controller.create()

        updated_task_obj = task_obj
        # Pass in the task
        status = "NOT STARTED"
        try:
            if data_paths:
                try:
                    _, _, task_dict['data_file_path_map'], task_dict['data_directory_path_map'] = \
                        parse_paths(self.task_controller.home, data_paths, '/data')
                except PathDoesNotExist as e:
                    status = "NOT STARTED"
                    workspace = task_dict.get('workspace', None)
                    command = task_dict.get('command', None)
                    command_list = task_dict.get('command_list', None)
                    interactive = task_dict.get('interactive', False)
                    self.task_controller.update(task_obj.id,
                                                workspace=workspace,
                                                command=command,
                                                command_list=command_list,
                                                interactive=interactive)
                    self.cli_helper.echo(__("error", "cli.run.parse.paths", str(e)))
                    return False

            updated_task_obj = self.task_controller.run(
                task_obj.id, snapshot_dict=snapshot_dict, task_dict=task_dict)
            status = "SUCCESS"
            self.cli_helper.echo(__("info", "cli.run.run.stop"))
        except Exception as e:
            status = "FAILED"
            self.logger.error("%s %s" % (e, task_dict))
            self.cli_helper.echo("%s" % e)
            self.cli_helper.echo(__("error", error_identifier, task_obj.id))
            return False
        finally:
            self.task_controller.stop(
                task_id=updated_task_obj.id, status=status)
        self.cli_helper.echo(
            __("info", "cli.run.run.complete", updated_task_obj.id))

        return updated_task_obj


@parameterized
def usage_docs(description):
    # TODO: create an attribute so we can show custom usage notes before
    # argparse displays help
    pass
