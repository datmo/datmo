from datmo import __version__
from datmo.core.util.i18n import get as __
from datmo.cli.command.base import BaseCommand
from datmo.core.controller.project import ProjectController


class ProjectCommand(BaseCommand):
    # NOTE: dal_driver is not passed into the project because it is created
    # first by ProjectController and then passed down to all other Controllers
    def __init__(self, home, cli_helper):
        super(ProjectCommand, self).__init__(home, cli_helper)
        self.project_controller = ProjectController(home=home)

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
                __("info", "cli.project.init.create", {
                    "name": name,
                    "path": self.home
                }))
            if not name:
                name = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.name"))
            if not description:
                description = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.description"))
            try:
                success = self.project_controller.init(name, description)
                if success:
                    self.cli_helper.echo(
                        __("info", "cli.project.init.create.success", {
                            "name": name,
                            "path": self.home
                        }))
            except Exception:
                self.cli_helper.echo(
                    __("info", "cli.project.init.create.failure", {
                        "name": name,
                        "path": self.home
                    }))
                return None
        else:  # Update the current project
            self.cli_helper.echo(
                __("info", "cli.project.init.update", {
                    "name": self.project_controller.model.name,
                    "path": self.home
                }))
            if not name:
                name = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.name"))
            if not description:
                description = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.description"))
            # Update project parameter if given parameter is not falsy and different
            if not name or name == self.project_controller.model.name:
                name = self.project_controller.model.name
            if not description or description == self.project_controller.model.description:
                description = self.project_controller.model.description
            # Update the project with the values given
            try:
                success = self.project_controller.init(name, description)
                if success:
                    self.cli_helper.echo(
                        __("info", "cli.project.init.update.success", {
                            "name": name,
                            "path": self.home
                        }))
            except Exception:
                self.cli_helper.echo(
                    __("info", "cli.project.init.update.failure", {
                        "name": name,
                        "path": self.home
                    }))
                return None

        self.cli_helper.echo("")

        # Print out simple project meta data
        for k, v in self.project_controller.model.to_dictionary().items():
            if k != "config":
                self.cli_helper.echo(str(k) + ": " + str(v))

        return self.project_controller.model

    def version(self):
        return self.cli_helper.echo("datmo version: %s" % __version__)

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
        # Prompt user to ensure they would like to remove all datmo information
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
