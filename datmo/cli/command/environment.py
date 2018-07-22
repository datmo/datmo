from __future__ import print_function

import os
from datetime import datetime

from datmo.core.util.i18n import get as __
from datmo.cli.driver.helper import Helper
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.cli.command.project import ProjectCommand
from datmo.core.util.exceptions import EnvironmentDoesNotExist
from datmo.core.util.misc_functions import printable_object, prettify_datetime


class EnvironmentCommand(ProjectCommand):
    def __init__(self, cli_helper):
        super(EnvironmentCommand, self).__init__(cli_helper)

    def environment(self):
        self.parse(["environment", "--help"])
        return True

    @Helper.notify_no_project_found
    def setup(self, **kwargs):
        self.environment_controller = EnvironmentController()
        environment_type = kwargs.get("type", None)
        environment_framework = kwargs.get("framework", None)
        environment_language = kwargs.get("language", None)
        # TODO: remove business logic from here and create common helper
        # environment types
        environment_types = self.environment_controller.get_environment_types()
        if environment_types and environment_type not in environment_types:
            environment_type = self.cli_helper.prompt_available_options(
                environment_types, option_type="type")
        # environment frameworks
        available_framework_details = self.environment_controller.get_supported_frameworks(
            environment_type)
        available_frameworks = [
            item[0] for item in available_framework_details
        ]
        if available_frameworks and environment_framework not in available_frameworks:
            environment_framework = self.cli_helper.prompt_available_options(
                available_framework_details, option_type="framework")
        # environment languages
        available_environment_languages = self.environment_controller.get_supported_languages(
            environment_type, environment_framework)
        if available_environment_languages and environment_language not in available_environment_languages:
            environment_language = self.cli_helper.prompt_available_options(
                available_environment_languages, option_type="language")
        try:
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
            return environment_obj
        except EnvironmentDoesNotExist:
            self.cli_helper.echo(
                __("error", "cli.environment.setup.argument",
                   "%s:%s-%s" % (environment_framework, environment_type,
                                 environment_language)))

    @Helper.notify_no_project_found
    def create(self, **kwargs):
        self.environment_controller = EnvironmentController()
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

    @Helper.notify_no_project_found
    def update(self, **kwargs):
        self.environment_controller = EnvironmentController()
        environment_id = kwargs.get('id')
        name = kwargs.get('name', None)
        description = kwargs.get("description", None)
        result = self.environment_controller.update(
            environment_id, name=name, description=description)
        return result

    @Helper.notify_environment_active(EnvironmentController)
    @Helper.notify_no_project_found
    def delete(self, **kwargs):
        self.environment_controller = EnvironmentController()
        environment_id = kwargs.get('id')
        if self.environment_controller.delete(environment_id):
            self.cli_helper.echo(
                __("info", "cli.environment.delete.success", environment_id))
            return True

    @Helper.notify_no_project_found
    def ls(self, **kwargs):
        self.environment_controller = EnvironmentController()
        print_format = kwargs.get('format', "table")
        download = kwargs.get('download', None)
        download_path = kwargs.get('download_path', None)
        environment_objs = self.environment_controller.list()
        header_list = ["id", "created at", "name", "description"]
        item_dict_list = []
        for environment_obj in environment_objs:
            environment_obj_name = printable_object(environment_obj.name)
            environment_obj_description = printable_object(
                environment_obj.description)
            item_dict_list.append({
                "id": environment_obj.id,
                "created at": prettify_datetime(environment_obj.created_at),
                "name": environment_obj_name,
                "description": environment_obj_description
            })
        if download:
            if not download_path:
                # download to current working directory with timestamp
                current_time = datetime.utcnow()
                epoch_time = datetime.utcfromtimestamp(0)
                current_time_unix_time_ms = (
                    current_time - epoch_time).total_seconds() * 1000.0
                download_path = os.path.join(
                    self.environment_controller.home,
                    "environment_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
            return environment_objs
        self.cli_helper.print_items(
            header_list, item_dict_list, print_format=print_format)
        return environment_objs
