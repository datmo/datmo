#!/usr/bin/python

import logging
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
            DatmoLogger.get_logger(__name__).info("initalizing")

        @property
        def home(self):
            return self._home

        @home.setter
        def home(self, home_path):
            self._home = home_path

    def __new__(cls):  # __new__ always a classmethod
        if not Config.instance:
            Config.instance = Config.__InternalConfig()
        return Config.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
