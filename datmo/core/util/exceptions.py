#!/usr/bin/python
from datmo.core.util.i18n import get as __


class ArgumentError(Exception):
    pass


class TaskNotComplete(ArgumentError):
    pass


class TaskNoCommandGiven(ArgumentError):
    pass


class TaskInteractiveDetachError(ArgumentError):
    pass


class SnapshotCreateFromTaskArgs(ArgumentError):
    pass


class RequiredArgumentMissing(ArgumentError):
    pass


class GitUrlArgumentError(ArgumentError):
    pass


class TooManyArgumentsFound(ArgumentError):
    pass


class ProjectException(Exception):
    pass


class InvalidProjectPath(ProjectException):
    pass


class ProjectNotInitialized(ProjectException):
    pass


class DatmoModelNotInitialized(ProjectException):
    pass


class InvalidOperation(Exception):
    pass


class ClassMethodNotFound(Exception):
    pass


class CLIArgumentError(ArgumentError):
    pass


class UnrecognizedCLIArgument(CLIArgumentError):
    pass


class InvalidArgumentType(ArgumentError):
    pass


class MutuallyExclusiveArguments(ArgumentError):
    pass


class ValidationSchemaMissing(ArgumentError):
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


class FileExecutionError(Exception):
    pass


class FileAlreadyExistsError(Exception):
    pass


class DirAlreadyExistsError(Exception):
    pass


class DoesNotExist(Exception):
    pass


class SessionDoesNotExist(DoesNotExist):
    pass


class CodeDoesNotExist(DoesNotExist):
    pass


class EnvironmentDoesNotExist(DoesNotExist):
    pass


class SnapshotDoesNotExist(DoesNotExist):
    pass


class PathDoesNotExist(FileExecutionError):
    pass


class LoggingPathDoesNotExist(PathDoesNotExist):
    pass


class FileIOError(FileExecutionError):
    pass


class FileStructureError(FileExecutionError):
    pass


class FileNotInitialized(FileExecutionError):
    pass


class EnvironmentException(Exception):
    pass


class EnvironmentImageNotFound(EnvironmentException):
    pass


class EnvironmentContainerNotFound(EnvironmentException):
    pass


class EnvironmentExecutionError(EnvironmentException):
    pass


class EnvironmentRequirementsCreateError(EnvironmentException):
    pass


class EnvironmentInitFailed(EnvironmentExecutionError):
    pass


class EnvironmentNotInitialized(EnvironmentExecutionError):
    pass


class TaskRunError(EnvironmentException):
    pass


class GPUSupportNotEnabled(EnvironmentExecutionError):
    pass


class CodeException(Exception):
    pass


class CodeNotInitialized(CodeException):
    pass


class GitExecutionError(CodeException):
    pass


class CommitDoesNotExist(CodeException):
    pass


class CommitFailed(CodeException):
    pass


class InvalidDestinationName(ArgumentError):
    pass


class ValidationFailed(ArgumentError):
    def __init__(self, error_obj):
        self.errors = error_obj
        super(ValidationFailed, self).__init__(
            __("error", "exception.validationfailed", self.get_error_str()))

    def get_error_str(self):
        err_str = ''
        for name in self.errors:
            err_str += "'%s': %s\n" % (name, self.errors[name])
        return err_str


class DatmoFolderInWorkTree(CodeException):
    pass


class UnstagedChanges(Exception):
    def __str__(self):
      return "Unstaged changes exists. Create a snapshot to remove any unstaged changes"


class NothingToStage(Exception):
    pass
