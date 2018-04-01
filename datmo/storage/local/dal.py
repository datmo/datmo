from kids.cache import cache
from datmo.entity.model import Model
from datmo.entity.session import Session
from datmo.entity.code import Code
from datmo.entity.environment import Environment
from datmo.entity.file_collection import FileCollection
from datmo.entity.task import Task
from datmo.entity.snapshot import Snapshot
from datmo.entity.user import User
from .entity_methods_crud import EntityMethodsCRUD

class LocalDAL():
    def __init__(self, driver):
        self.driver = driver

    @cache
    @property
    def model(self):
        return  ModelMethods(self.driver)

    @cache
    @property
    def code(self):
        return CodeMethods(self.driver)

    @cache
    @property
    def environment(self):
        return EnvironmentMethods(self.driver)

    @cache
    @property
    def file_collection(self):
        return FileCollectionMethods(self.driver)

    @cache
    @property
    def session(self):
        return SessionMethods(self.driver)

    @cache
    @property
    def task(self):
        return  TaskMethods(self.driver)

    @cache
    @property
    def snapshot(self):
        return  SnapshotMethods(self.driver)

    @cache
    @property
    def user(self):
        return  UserMethods(self.driver)

#
# https://stackoverflow.com/questions/1713038/super-fails-with-error-typeerror-argument-1-must-be-type-not-classobj
#

#
# Datmo Entity methods
#
class ModelMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(ModelMethods, self).__init__(
            'model',
            Model,
            driver)

class CodeMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(CodeMethods, self).__init__(
            'code',
            Code,
            driver)

class EnvironmentMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(EnvironmentMethods, self).__init__(
            'environment',
            Environment,
            driver)

class FileCollectionMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(FileCollectionMethods, self).__init__(
            'file_collection',
            FileCollection,
            driver)

class SessionMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(SessionMethods, self).__init__(
            'session',
            Session,
            driver)

class TaskMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(TaskMethods, self).__init__(
            'task',
            Task,
            driver
        )

class SnapshotMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(SnapshotMethods, self).__init__(
            'snapshot',
            Snapshot,
            driver)

class UserMethods(EntityMethodsCRUD):
    def __init__(self, driver):
        super(UserMethods, self).__init__(
            'user',
            User,
            driver)
