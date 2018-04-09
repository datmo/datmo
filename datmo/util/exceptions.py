class InvalidProjectPathException(Exception):
    pass

class ProjectNotInitializedException(Exception):
    pass

class DatmoModelNotInitializedException(Exception):
    pass

class SessionDoesNotExistException(Exception):
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

class DoesNotExistException(FileExecutionException):
    pass

class FileIOException(FileExecutionException):
    pass

class FileStructureException(FileExecutionException):
    pass

class EnvironmentExecutionException(Exception):
    pass

class EnvironmentInitFailed(EnvironmentExecutionException):
    pass

class EnvironmentNotInitialized(EnvironmentExecutionException):
    pass

class TaskRunException(Exception):
    pass