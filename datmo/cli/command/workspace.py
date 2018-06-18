from datmo.core.util.i18n import get as __
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.spinner import Spinner
from datmo.core.util.misc_functions import mutually_exclusive
from datmo.core.controller.project import ProjectController
from datmo.core.controller.task import TaskController


class WorkspaceCommand(ProjectCommand):
    # NOTE: dal_driver is not passed into the project because it is created
    # first by ProjectController and then passed down to all other Controllers
    def __init__(self, home, cli_helper):
        super(WorkspaceCommand, self).__init__(home, cli_helper)
        self.task_controller = TaskController(home=self.project_controller.home)
        self.spinner = Spinner()

    def notebook(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.workspace.notebook"))
        # Creating input dictionaries
        snapshot_dict = {}

        # Environment
        if kwargs.get("environment_id", None) or kwargs.get(
                "environment_paths", None):
            mutually_exclusive_args = ["environment_id", "environment_paths"]
            mutually_exclusive(mutually_exclusive_args, kwargs, snapshot_dict)

        task_dict = {
            "ports": ["8888:8888"],
            "command_list": ["jupyter", "notebook"],
            "mem_limit": kwargs["mem_limit"]
        }

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
            self.cli_helper.echo(
                __("error", "cli.workspace.notebook", task_obj.id))
            return False
        finally:
            self.spinner.stop()

        self.cli_helper.echo(
            "Ran notebook with task id: %s" % updated_task_obj.id)

        return updated_task_obj
