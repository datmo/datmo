#!/usr/bin/python
from datmo.core.util.i18n import get as __


class InvalidProjectPath(Exception):
    pass


class ProjectNotInitialized(Exception):
    pass


class DatmoModelNotInitialized(Exception):
    pass


class SessionDoesNotExist(Exception):
    pass


class InvalidOperation(Exception):
    pass


class ClassMethodNotFound(Exception):
    pass


class CLIArgumentError(Exception):
    pass


class UnrecognizedCLIArgument(CLIArgumentError):
    pass


class IncorrectType(Exception):
    pass


class InputError(Exception):
    pass


class EntityNotFound(Exception):
    pass


class MoreThanOneEntityFound(Exception):
    pass


class EntityCollectionNotFound(Exception):
    pass


class SaveSettingError(Exception):
    pass


class ArgumentError(Exception):
    pass


class RequiredArgumentMissing(ArgumentError):
    pass


class GitUrlArgumentError(ArgumentError):
    pass


class TooManyArgumentsFound(ArgumentError):
    pass


class GitExecutionError(Exception):
    pass


class GitCommitDoesNotExist(Exception):
    pass


class FileExecutionError(Exception):
    pass


class FileAlreadyExistsError(Exception):
    pass


class DoesNotExist(Exception):
    pass


class EnvironmentDoesNotExist(DoesNotExist):
    pass


class PathDoesNotExist(FileExecutionError):
    pass


class LoggingPathDoesNotExist(PathDoesNotExist):
    pass


class FileIOError(FileExecutionError):
    pass


class FileStructureError(FileExecutionError):
    pass


class EnvironmentImageNotFound(Exception):
    pass


class EnvironmentContainerNotFound(Exception):
    pass


class EnvironmentExecutionError(Exception):
    pass


class EnvironmentRequirementsCreateError(Exception):
    pass


class EnvironmentInitFailed(EnvironmentExecutionError):
    pass


class EnvironmentNotInitialized(EnvironmentExecutionError):
    pass


class TaskRunError(Exception):
    pass


class DatmoFolderInWorkTree(Exception):
    pass


class InvalidArgumentType(Exception):
    pass


class MutuallyExclusiveArguments(Exception):
    pass


class TaskNotComplete(ArgumentError):
    pass


class TaskNoCommandGiven(ArgumentError):
    pass


class TaskInteractiveDetachError(ArgumentError):
    pass


class SnapshotCreateFromTaskArgs(ArgumentError):
    pass


class ValidationFailed(Exception):
    def __init__(self, error_obj):
        self.errors = error_obj
        super(ValidationFailed, self).__init__(
            __("error", "exception.validationfailed", self.get_error_str()))

    def get_error_str(self):
        err_str = ''
        for name in self.errors:
            err_str += "'%s': %s\n" % (name, self.errors[name])
        return err_str


class ValidationSchemaMissing(Exception):
    pass


class GPUSupportNotEnabled(EnvironmentExecutionError):
    pass
