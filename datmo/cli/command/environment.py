from __future__ import print_function

import prettytable

from datmo.core.util.i18n import get as __
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.util.misc_functions import printable_string
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.exceptions import EnvironmentDoesNotExist


class EnvironmentCommand(ProjectCommand):
    def __init__(self, home, cli_helper):
        super(EnvironmentCommand, self).__init__(home, cli_helper)
        # dest="subcommand" argument will populate a "subcommand" property with the subparsers name
        # example  "subcommand"="create"  or "subcommand"="ls"
        self.environment_controller = EnvironmentController(home=home)

    def environment(self):
        self.parse(["--help"])
        return True

    def setup(self, **kwargs):
        name = kwargs.get("name", None)
        available_environments = self.environment_controller.get_supported_environments(
        )
        if not name:
            name = self.cli_helper.prompt_available_environments(
                available_environments)
        try:
            options = {"name": name}
            environment_obj = self.environment_controller.setup(
                options=options)
            self.cli_helper.echo(
                __("info", "cli.environment.setup.success",
                   (environment_obj.name, environment_obj.id)))
            return environment_obj
        except EnvironmentDoesNotExist:
            self.cli_helper.echo(
                __("error", "cli.environment.setup.argument", name))

    def create(self, **kwargs):
        self.cli_helper.echo(__("info", "cli.environment.create"))
        created_environment_obj = self.environment_controller.create(kwargs)
        environments = self.environment_controller.list()
        for environment_obj in environments:
            if created_environment_obj == environment_obj:
                self.cli_helper.echo(
                    __("info", "cli.environment.create.alreadyexist",
                       created_environment_obj.id))
                return created_environment_obj
        self.cli_helper.echo(
            __("info", "cli.environment.create.success",
               created_environment_obj.id))
        return created_environment_obj

    def delete(self, **kwargs):
        environment_id = kwargs.get('environment_id')
        if self.environment_controller.delete(environment_id):
            self.cli_helper.echo(
                __("info", "cli.environment.delete.success", environment_id))
            return True

    def ls(self):
        environments = self.environment_controller.list()
        header_list = ["id", "created at", "name", "description"]
        t = prettytable.PrettyTable(header_list)
        environment_ids = []
        for environment_obj in environments:
            environment_ids.append(environment_obj.id)
            environment_created_at = printable_string(
                environment_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            environment_name = printable_string(environment_obj.name) \
                if environment_obj.name is not None else ""
            environment_description = printable_string(environment_obj.description) \
                if environment_obj.description is not None else ""
            t.add_row([
                environment_obj.id, environment_created_at, environment_name,
                environment_description
            ])
        self.cli_helper.echo(t)
        return environments
