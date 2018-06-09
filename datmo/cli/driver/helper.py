from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input

import os
import sys
import importlib
import inspect
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:

    def to_bytes(val):
        return bytes(val)

    to_bytes("test")
except TypeError:

    def to_bytes(val):
        return bytes(val, "utf-8")

    to_bytes("test")

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import ArgumentError


class Helper():
    def __init__(self):
        pass

    def echo(self, value):
        print(to_unicode(value))
        return value

    def input(self, input_msg):
        def input_decorator(func):
            def wrapper(*args, **kwargs):
                with open(os.path.join("input"), "wb") as f:
                    f.write(to_bytes(input_msg))

                with open(os.path.join("input"), "r") as f:
                    sys.stdin = f
                    result = func(*args, **kwargs)
                os.remove(os.path.join("input"))
                return result

            return wrapper

        return input_decorator

    def prompt(self, msg, default=None):
        try:
            if default:
                msg = msg + "[" + str(default) + "]"
            msg = msg + ": "
            return input(msg)
        except EOFError:
            pass

    def prompt_bool(self, msg):
        msg = msg + ": "
        val = input(msg).lower()
        return val in [
            'true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'
        ]

    def prompt_validator(self,
                         msg,
                         validate_function,
                         tries=5,
                         error_message="Invalid input"):
        if not callable(validate_function):
            raise ArgumentError('validate_function argument must be function')
        val = input(msg).lower()
        if not validate_function(val) and tries >= 0:
            tries -= 1
            return self.prompt_validator(msg, validate_function, tries,
                                         error_message)
        if tries == 0:
            self.echo(error_message)
        return val

    def get_command_class(self, command_name):
        command_path = "datmo.cli.command." + command_name

        try:
            command_class = importlib.import_module(command_path)
        except ImportError as ex:
            try:
                command_path = "datmo.cli.command." + command_name + "_command"
                command_class = importlib.import_module(command_path)
            except ImportError as ex:
                self.echo(__("error", "cli.general", ex.message))
                sys.exit()

        all_members = inspect.getmembers(command_class)

        # find class module based on first param passed into command line
        for member in all_members:
            if command_path in member[1].__module__:
                command_class = member
                break

        # command_class[1] == concrete class constructor
        return command_class[1]

    def get_command_choices(self):
        return [
            "init", "version", "--version", "-v", "status", "cleanup",
            "snapshot", "task", "notebook", "environment"
        ]

    def prompt_available_environments(self, available_environments):
        """Prompt user to choose an available environment. Returns the environment name"""
        for idx, environment_name_description in enumerate(
                available_environments):
            environment_name = environment_name_description[0]
            environment_description = environment_name_description[1]
            self.echo("(%s) %s: %s" % (idx + 1, environment_name,
                                       environment_description))
        input_environment_name = self.prompt(
            __("prompt", "cli.environment.setup.name"))
        try:
            name_environment_index = int(input_environment_name)
        except ValueError:
            available_names = [
                name for name, description in available_environments
            ]
            try:
                name_environment_index = available_names.index(
                    input_environment_name) + 1
            except ValueError:
                self.echo(
                    __("error", "cli.environment.setup.argument",
                       input_environment_name))
                return input_environment_name
        if 0 < name_environment_index < len(available_environments):
            input_environment_name = available_environments[
                name_environment_index - 1][0]
        return input_environment_name
