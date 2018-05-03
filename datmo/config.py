
import os
import logging
from datmo.core.util.misc_functions import find_project_dir, create_project_dir
from datmo.core.util.logger import DatmoLogger

class Config(object):
    """Datmo Config properties

    Parameters
    ----------
    home : string
      project home directory

    logging_level : int
      logging level
    Returns
    -------
    Config
      Config Singleton
    """

    instance = None
    class __InternalConfig:
        def __init__(self):
            self._home = None
            self.logging_level = logging.DEBUG
            self.logging_path = None

            try:
                self._home = find_project_dir()
            except Exception as e:
                self._home = create_project_dir(os.getcwd())
            self.logging_path = os.path.join(self._home, '.datmo','logs')
            self.configure_logging()

        @property
        def home(self):
            return self._home

        @home.setter
        def home(self, home_path):
            self._home = home_path
            self.configure_logging()

        def configure_logging(self):
            self.logging_path = os.path.join(self._home, '.datmo','logs')
            DatmoLogger.configure(self.logging_path, self.logging_level)


    def __new__(cls): # __new__ always a classmethod
        if not Config.instance:
            Config.instance = Config.__InternalConfig()
        return Config.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)


