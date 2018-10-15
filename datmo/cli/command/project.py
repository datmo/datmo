import os

from datmo import __version__
from datmo.core.util.i18n import get as __
from datmo.core.util.json_store import JSONStore
from datmo.cli.driver.helper import Helper
from datmo.cli.command.base import BaseCommand
from datmo.core.controller.project import ProjectController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.dashboard.app import app


class ProjectCommand(BaseCommand):
    def __init__(self, cli_helper):
        super(ProjectCommand, self).__init__(cli_helper)
        self.project_controller = ProjectController()

    def init(self, name, description, force):
        """Initialize command

        Parameters
        ----------
        name : str
            name for the project
        description : str
            description of the project
        force : bool
            Boolean to force initialization without prompts

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
                if not force:
                    name = self.cli_helper.prompt(
                        __("prompt", "cli.project.init.name"),
                        default=default_name)
                else:
                    name = default_name
            if not description:
                if not force:
                    description = self.cli_helper.prompt(
                        __("prompt", "cli.project.init.description"))
                else:
                    description = ""
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
            if not name and not force:
                name = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.name"),
                    default=self.project_controller.model.name)
            elif force:
                name = self.project_controller.model.name
            if not description and not force:
                description = self.cli_helper.prompt(
                    __("prompt", "cli.project.init.description"),
                    default=self.project_controller.model.description)
            elif force:
                description = self.project_controller.model.description
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
            __("prompt",
               "cli.project.environment.setup")) if not force else False
        if environment_setup:
            # TODO: remove business logic from here and create common helper
            # Setting up the environment definition file
            self.environment_controller = EnvironmentController()
            environment_types = self.environment_controller.get_environment_types(
            )
            environment_type = self.cli_helper.prompt_available_options(
                environment_types, option_type="type")
            available_environment_frameworks = self.environment_controller.get_supported_frameworks(
                environment_type)
            environment_framework = self.cli_helper.prompt_available_options(
                available_environment_frameworks, option_type="framework")
            available_environment_languages = self.environment_controller.get_supported_languages(
                environment_type, environment_framework)
            environment_language = self.cli_helper.prompt_available_options(
                available_environment_languages, option_type="language")
            options = {
                "environment_type": environment_type,
                "environment_framework": environment_framework,
                "environment_language": environment_language
            }
            environment_obj = self.environment_controller.setup(
                options=options)
            self.cli_helper.echo(
                __("info", "cli.environment.setup.success",
                   (environment_obj.name, environment_obj.id)))
        else:
            self.cli_helper.echo(
                "there was no environment setup. you can get information"
                " here: https://datmo.readthedocs.io/en/latest/env-setup.html")

        return self.project_controller.model

    def version(self):
        return self.cli_helper.echo("datmo version: %s" % __version__)

    def configure(self):
        """
        Configure datmo installation
        """
        # General setup
        setup_remote_bool = self.cli_helper.prompt_bool(
            "Would you like to setup your remote credentials? [yN]")

        if setup_remote_bool:
            datmo_api_key = None
            master_server_ip = None

            while not datmo_api_key:
                datmo_api_key = self.cli_helper.prompt(
                    "---> Enter API key for Datmo Deployment")

            while not master_server_ip:
                master_server_ip = self.cli_helper.prompt(
                    "---> Enter master server IP address for Datmo Deployment")

            # Create a config file
            self.datmo_config = JSONStore(
                os.path.join(os.path.expanduser("~"), ".datmo", "config"))

            config = dict()
            if master_server_ip and datmo_api_key:
                config["MASTER_SERVER_IP"] = master_server_ip
                config["DATMO_API_KEY"] = datmo_api_key
                self.datmo_config.to_file(config)
            else:
                self.cli_helper.echo(
                    "Remote credentials could not be saved because they weren't input correctly. Please try again"
                )

        # Setup project specific things
        if self.project_controller.model:
            pass
        else:
            self.cli_helper.echo(
                "No datmo project found. Skipping configuration for project.")

    @Helper.notify_no_project_found
    def status(self):
        status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files = \
            self.project_controller.status()
        # Print out simple project meta data
        for k, v in status_dict.items():
            if k != "config":
                self.cli_helper.echo(str(k) + ": " + str(v))

        self.cli_helper.echo("")

        # Print out any unstaged changes else print out the latest snapshot state of the repository
        if not unstaged_code and not unstaged_environment and not unstaged_files:
            self.cli_helper.echo(
                "all changes have been saved, no unstaged changes")
            self.cli_helper.echo("")
            self.cli_helper.echo("current snapshot state of the repository: ")
            if current_snapshot:
                self.cli_helper.echo(current_snapshot)
        else:
            # Print out the unstaged components if unstaged
            self.cli_helper.echo("unstaged changes since latest snapshot:")
            if unstaged_code:
                self.cli_helper.echo("code has been changed")
            if unstaged_environment:
                self.cli_helper.echo("environment has been changed")
            if unstaged_files:
                self.cli_helper.echo("files have been changed")

        # Print out info for the latest snapshot (the most recent first, and state if autogenerated or by user)
        if latest_snapshot_user_generated and not latest_snapshot_auto_generated:
            self.cli_helper.echo("latest snapshot generated by the user: ")
            self.cli_helper.echo(latest_snapshot_user_generated)
            self.cli_helper.echo("no snapshot autogenerated by datmo")
        elif latest_snapshot_auto_generated and not latest_snapshot_user_generated:
            self.cli_helper.echo("latest snapshot autogenerated by datmo: ")
            self.cli_helper.echo(latest_snapshot_auto_generated)
            self.cli_helper.echo("no snapshot generated by the user")
        elif not latest_snapshot_user_generated and not latest_snapshot_auto_generated:
            self.cli_helper.echo("no snapshots created yet")
        elif latest_snapshot_user_generated.created_at > latest_snapshot_auto_generated.created_at:
            self.cli_helper.echo("latest snapshot generated by the user: ")
            self.cli_helper.echo(latest_snapshot_user_generated)
            self.cli_helper.echo("latest snapshot autogenerated by datmo: ")
            self.cli_helper.echo(latest_snapshot_auto_generated)
        elif latest_snapshot_user_generated.created_at < latest_snapshot_auto_generated.created_at:
            self.cli_helper.echo("latest snapshot autogenerated by datmo: ")
            self.cli_helper.echo(latest_snapshot_auto_generated)
            self.cli_helper.echo("latest snapshot generated by the user: ")
            self.cli_helper.echo(latest_snapshot_user_generated)

        return status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, unstaged_code, unstaged_environment, unstaged_files

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

    def dashboard(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.join(dir_path, "../../dashboard"))
        app.run(host='0.0.0.0')
        return True
