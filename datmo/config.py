#!/usr/bin/python

import logging
import os
import datetime
from datmo.core.util.logger import DatmoLogger
from datmo.core.util.json_store import JSONStore
from datmo.core.util.misc_functions import parameterized


class Config(object):
    """Datmo Config properties

    Parameters
    ----------
    home : str
        project home directory
    damto_directory_name : str
        datmo directory name
    remote_credentials : tuple

    Returns
    -------
    Config
      Config Singleton
    """

    instance = None

    class __InternalConfig:
        def __init__(self):
            self._home = None
            self.datmo_directory_name = ".datmo"
            self.logging_level = logging.DEBUG
            DatmoLogger.get_logger(__name__).info("initializing")
            self.data_cache = JSONStore(
                os.path.join(os.path.expanduser("~"), ".datmo", "cache.json"))
            self.docker_cli = '/usr/bin/docker'

        @property
        def home(self):
            return self._home

        @property
        def remote_credentials(self):
            """
            Returns credentials if present

            Returns
            -------
            MASTER_SERVER_IP : str
                return if present else None
            DATMO_API_KEY : str
                return if present else None
            END_POINT : str
                return if present else None
            """
            # 1) Load from the environment if datmo config not already saved globally
            MASTER_SERVER_IP = os.environ.get('MASTER_SERVER_IP', None)
            DATMO_API_KEY = os.environ.get('DATMO_API_KEY', None)

            # 2) loading the datmo config if present
            datmo_config_filepath = os.path.join(
                os.path.expanduser("~"), ".datmo", "config")
            if os.path.isfile(datmo_config_filepath):
                datmo_config = JSONStore(datmo_config_filepath)
                config_dict = datmo_config.to_dict()
                if MASTER_SERVER_IP is None:
                    MASTER_SERVER_IP = config_dict.get('MASTER_SERVER_IP',
                                                       None)
                if DATMO_API_KEY is None:
                    DATMO_API_KEY = config_dict.get('DATMO_API_KEY', None)

            if MASTER_SERVER_IP:
                END_POINT = 'http://' + MASTER_SERVER_IP + ':2083/api/v1'
            else:
                END_POINT = None

            return MASTER_SERVER_IP, DATMO_API_KEY, END_POINT

        def set_home(self, home_path):
            self._home = home_path

        def get_cache_item(self, key):
            cache_expire_key = 'cache_key_expires.' + key
            cache_key = 'cache_key.' + key
            cache_expire_val = self.data_cache.get(cache_expire_key)
            # no cache expire val, it's not stored
            if cache_expire_val == None:
                return None
            # return value if item has not expired
            elif int(cache_expire_val) > int(
                    datetime.datetime.now().strftime('%s')):
                return self.data_cache.get(cache_key)
            # expire item and return None
            else:
                self.data_cache.remove(cache_expire_key)
                self.data_cache.remove(cache_key)
                return None

        def set_cache_item(self, key, value, duration=60):
            cache_expire_key = 'cache_key_expires.' + key
            cache_key = 'cache_key.' + key
            expire_val = (duration * 60) + int(
                datetime.datetime.now().strftime('%s'))
            self.data_cache.save(cache_expire_key, expire_val)
            self.data_cache.save(cache_key, value)

    def __new__(cls):  # __new__ always a classmethod
        if not Config.instance:
            Config.instance = Config.__InternalConfig()
        return Config.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)

    @staticmethod
    @parameterized
    def cache_setting(method, key=None, expires_min=60, ignore_values=[]):
        name = key if key is not None else method.__module__ + '.' + method.__name__
        config = Config()

        def fn(*args, **kw):
            cached_val = config.get_cache_item(name)
            if cached_val is not None:
                return cached_val
            result = method(*args, **kw)
            if not result in ignore_values:
                config.set_cache_item(name, result, expires_min)
            return result

        return fn
