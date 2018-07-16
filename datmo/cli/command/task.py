from __future__ import print_function

try:
    basestring
except NameError:
    basestring = str

from datmo.cli.command.project import ProjectCommand


class TaskCommand(ProjectCommand):
    def __init__(self, cli_helper):
        super(TaskCommand, self).__init__(cli_helper)

    def task(self):
        self.parse(["task", "--help"])
        return True
