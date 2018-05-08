#!/usr/bin/python


class InvalidProjectPathException(Exception):
    pass


class ProjectNotInitializedException(Exception):
    pass


class DatmoModelNotInitializedException(Exception):
    pass


class SessionDoesNotExistException(Exception):
    pass


class InvalidOperation(Exception):
    pass


class ClassMethodNotFound(Exception):
    pass


class CLIArgumentException(Exception):
    pass


class UnrecognizedCLIArgument(CLIArgumentException):
    pass


class IncorrectTypeException(Exception):
    pass


class InputException(Exception):
    pass


class EntityNotFound(Exception):
    pass


class MoreThanOneEntityFound(Exception):
    pass


class EntityCollectionNotFound(Exception):
    pass


class SaveSettingException(Exception):
    pass


class ArgumentException(Exception):
    pass


class RequiredArgumentMissing(ArgumentException):
    pass


class GitUrlArgumentException(ArgumentException):
    pass


class GitExecutionException(Exception):
    pass


class GitCommitDoesNotExist(Exception):
    pass


class FileExecutionException(Exception):
    pass


class FileAlreadyExistsException(Exception):
    pass


class DoesNotExist(Exception):
    pass


class EnvironmentDoesNotExist(DoesNotExist):
    pass


class PathDoesNotExist(FileExecutionException):
    pass


class LoggingPathDoesNotExist(PathDoesNotExist):
    pass


class FileIOException(FileExecutionException):
    pass


class FileStructureException(FileExecutionException):
    pass


class EnvironmentImageNotFound(Exception):
    pass


class EnvironmentContainerNotFound(Exception):
    pass


class EnvironmentExecutionException(Exception):
    pass


class EnvironmentRequirementsCreateException(Exception):
    pass


class EnvironmentInitFailed(EnvironmentExecutionException):
    pass


class EnvironmentNotInitialized(EnvironmentExecutionException):
    pass


class TaskRunException(Exception):
    pass


class DatmoFolderInWorkTree(Exception):
    pass


class InvalidArgumentType(Exception):
    pass


class MutuallyExclusiveArguments(Exception):
    pass


class TaskNotComplete(ArgumentException):
    pass


class TaskInteractiveDetachException(ArgumentException):
    pass


class SnapshotCreateFromTaskArgs(ArgumentException):
    pass
