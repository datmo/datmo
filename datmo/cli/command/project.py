import os

from datmo import __version__
from datmo.core.util.i18n import get as __
from datmo.cli.driver.helper import Helper
from datmo.cli.command.base import BaseCommand
from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import EnvironmentController, EnvironmentDoesNotExist


class ProjectCommand(BaseCommand):
    def __init__(self, cli_helper):
        super(ProjectCommand, self).__init__(cli_helper)
        self.project_controller = ProjectController()

    def init(self, name, description):
        """Initialize command

        Parameters
        ----------
        name : str
            name for the project
        description : str
            description of the project

        Returns
        -------
        datmo.core.entity.model.Model
        """
        # Check if project already exists
        is_new_model = False
        if not self.project_controller.model:
            is_new_model = True

        if is_new_model:  # Initialize a new project
            self.cli_helper.echo(
                __("info", "cli.project.init.create",
                   {"path": self.project_controller.home}))
            if not name:
                _, default_name = os.path.split(self.project_controller.home)
                name = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.name"),
                    default=default_name)
            if not description:
                description = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.description"))
            try:
                success = self.project_controller.init(name, description)
                if success:
                    self.cli_helper.echo(
                        __("info", "cli.project.init.create.success", {
                            "name": name,
                            "path": self.project_controller.home
                        }))
            except Exception:
                self.cli_helper.echo(
                    __("info", "cli.project.init.create.failure", {
                        "name": name,
                        "path": self.project_controller.home
                    }))
                return None
        else:  # Update the current project
            self.cli_helper.echo(
                __(
                    "info", "cli.project.init.update", {
                        "name": self.project_controller.model.name,
                        "path": self.project_controller.home
                    }))
            # Prompt for the name and description and add default if not given
            if not name:
                name = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.name"),
                    default=self.project_controller.model.name)
            if not description:
                description = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.description"),
                    default=self.project_controller.model.description)
            # Update the project with the values given
            try:
                success = self.project_controller.init(name, description)
                if success:
                    self.cli_helper.echo(
                        __("info", "cli.project.init.update.success", {
                            "name": name,
                            "path": self.project_controller.home
                        }))
            except Exception:
                self.cli_helper.echo(
                    __("info", "cli.project.init.update.failure", {
                        "name": name,
                        "path": self.project_controller.home
                    }))
                return None

        self.cli_helper.echo("")

        # Print out simple project meta data
        for k, v in self.project_controller.model.to_dictionary().items():
            if k != "config":
                self.cli_helper.echo(str(k) + ": " + str(v))
        # Ask question if the user would like to setup environment
        environment_setup = self.cli_helper.prompt_bool(
            __("prompt", "cli.project.environment.setup"))
        if environment_setup:
            # Setting up the environment definition file
            self.environment_controller = EnvironmentController()
            available_environments = self.environment_controller.get_supported_environments(
            )
            input_environment_name = self.cli_helper.prompt_available_environments(
                available_environments)
            try:
                options = {"name": input_environment_name}
                environment_obj = self.environment_controller.setup(
                    options=options)
                self.cli_helper.echo(
                    __("info", "cli.environment.setup.success",
                       (environment_obj.name, environment_obj.id)))
            except EnvironmentDoesNotExist:
                self.cli_helper.echo(
                    __("error", "cli.environment.setup.argument",
                       input_environment_name))
        return self.project_controller.model

    def version(self):
        return self.cli_helper.echo("datmo version: %s" % __version__)

    @Helper.notify_no_project_found
    def status(self):
        status_dict, latest_snapshot, ascending_unstaged_tasks = self.project_controller.status(
        )

        # Print out simple project meta data
        for k, v in status_dict.items():
            if k != "config":
                self.cli_helper.echo(str(k) + ": " + str(v))

        self.cli_helper.echo("")

        # Print out project config meta data
        self.cli_helper.echo("config: ")
        self.cli_helper.echo(status_dict['config'])

        self.cli_helper.echo("")

        # Print out latest snapshot info
        self.cli_helper.echo("latest snapshot id: ")
        if latest_snapshot:
            self.cli_helper.echo(latest_snapshot.id)
        else:
            self.cli_helper.echo("no snapshots created yet")

        self.cli_helper.echo("")

        # Print out unstaged tasks
        self.cli_helper.echo("unstaged task ids:")
        if ascending_unstaged_tasks:
            for task in ascending_unstaged_tasks:
                self.cli_helper.echo(task.id)
        else:
            self.cli_helper.echo("no unstaged tasks")

        return status_dict, latest_snapshot, ascending_unstaged_tasks

    def cleanup(self):
        # Prompt user to ensure they would like to remove datmo information along with environment and files folder
        response = self.cli_helper.prompt_bool(
            __("prompt", "cli.project.cleanup.confirm"))

        # Cleanup datmo project if user specifies
        if response:
            self.cli_helper.echo(
                __(
                    "info", "cli.project.cleanup", {
                        "name": self.project_controller.model.name,
                        "path": self.project_controller.home
                    }))
            try:
                success = self.project_controller.cleanup()
                if success:
                    self.cli_helper.echo(
                        __(
                            "info", "cli.project.cleanup.success", {
                                "name": self.project_controller.model.name,
                                "path": self.project_controller.home
                            }))
                return success
            except Exception:
                self.cli_helper.echo(
                    __(
                        "info", "cli.project.cleanup.failure", {
                            "name": self.project_controller.model.name,
                            "path": self.project_controller.home
                        }))
        return False