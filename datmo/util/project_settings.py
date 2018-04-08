import os

from datmo.util.file_storage import JSONKeyValueStore


class ProjectSettings():
    def __init__(self, home):
        self.home = home
        self.driver = JSONKeyValueStore(os.path.join(self.home, '.datmo'
                                                   'project_settings.json'))

    def get(self, key):
        return self.driver.get(key)

    def set(self, key, value):
        return self.driver.save(key, value)
