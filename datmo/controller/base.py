import os
from datmo.storage.local.driver.driver_type import DriverType
from datmo.util import get_class_contructor
from datmo.util.project_settings import ProjectSettings
from datmo.util.exceptions import InvalidProjectPathException, \
    DatmoModelNotInitializedException


class BaseController(object):

    def __init__(self, home, dal_driver=None):
        self.home = home
        self.dal_driver = dal_driver
        # property caches and initial values
        self._dal = None
        self._model = None
        self._current_session = None
        self._code_driver = None
        self._file_driver = None
        self._environment_driver = None
        self._is_initialized = False

        if not os.path.isdir(self.home):
            raise InvalidProjectPathException("exception.datmo.project", {
                "home": home,
                "exception": "ProjectCommand path does not exist"
            })

        self.settings = ProjectSettings(self.home)
        # TODO: is_initialized properties should be functions

    @property
    # Controller objects are only in sync if the data drivers are the same between objects
    # TODO: Currently local for differnet controller objects do NOT sync within one session.
    # TODO: Fix local such that it syncs within one session between controller objects
    def dal(self):
        if self._dal == None:
          self._dal = self.dal_instantiate()
        return self._dal

    @property
    def model(self):
        if self._model == None:
            model_id = self.settings.get('model_id')
            self._model = self.dal.model.get_by_id(model_id) if model_id else None
        return self._model

    @property
    def current_session(self):
        if not self.model:
            raise DatmoModelNotInitializedException()
        if self._current_session == None:
          session_id = self.settings.get('current_session_id')
          self._current_session = self.dal.session.get_by_id(session_id) if session_id else None
        return self._current_session

    @property
    def code_driver(self):
        if self._code_driver == None:
            module_details = self.config_loader("controller.code.driver")
            self._code_driver = module_details["constructor"](**module_details["options"])
        return self._code_driver

    @property
    def file_driver(self):
        if self._file_driver == None:
            module_details = self.config_loader("controller.file.driver")
            self._file_driver = module_details["constructor"](**module_details["options"])
        return self._file_driver

    @property
    def environment_driver(self):
        if self._environment_driver == None:
            module_details = self.config_loader("controller.environment.driver")
            self._environment_driver = module_details["constructor"](**module_details["options"])
        return self._environment_driver

    @property
    def is_initialized(self):
        if not self._is_initialized:
          if self.code_driver.is_initialized and \
              self.environment_driver.is_initialized and \
              self.file_driver.is_initialized:
              if self.model:
                  self._is_initialized = True
        return self._is_initialized

    def dal_instantiate(self):
        # first load driver, then create DAL using driver
        if not self.dal_driver:
            dal_driver_dict = self.config_loader("storage.local.driver")
            if type(dal_driver_dict["options"]["driver_type"]) == str or \
                type(dal_driver_dict["options"]["driver_type"]) == unicode:
                dal_driver_dict["options"]["driver_type"] = DriverType[dal_driver_dict["options"]["driver_type"]]
            self.dal_driver = dal_driver_dict["constructor"](**dal_driver_dict["options"])
        # Get DAL, set driver,
        dal_dict = self.config_loader("storage.local")
        dal_dict["options"]["driver"] = self.dal_driver
        return dal_dict["constructor"](**dal_dict["options"])

    def get_or_set_default(self, key, default_value):
        value = self.settings.get(key)
        if value is None:
            self.settings.set(key, default_value)
            value = default_value
        return value

    def config_loader(self, key):
        defaults = self.get_config_defaults()
        module_details = self.get_or_set_default(key, defaults[key])
        module_details["constructor"] = get_class_contructor(module_details["class_constructor"])
        return module_details

    def get_config_defaults(self):
        return {
            "controller.code.driver": {
                "class_constructor": "datmo.controller.code.driver.git.GitCodeManager",
                "options": {
                    "filepath": self.home,
                    "execpath": "git"
                }
            },
            "controller.file.driver": {
                "class_constructor": "datmo.controller.file.driver.local.LocalFileManager",
                "options": {
                    "filepath": self.home
                }
            },
            "controller.environment.driver":{
                "class_constructor": "datmo.controller.environment.driver.dockerenv.DockerEnvironmentManager",
                "options": {
                    "filepath": self.home,
                    "docker_execpath": "docker",
                    "docker_socket": "unix:///var/run/docker.sock"
                }
            },
            "storage.local": {
                "class_constructor": "datmo.storage.local.dal.LocalDAL",
                "options": {
                    "driver": "storage.local.driver"
                }
            },
            "storage.local.driver": {
                "class_constructor": "datmo.storage.local.driver.blitzdb_driver.BlitzDBDataDriver",
                "options": {
                    "driver_type": "FILE",
                    "connection_string": os.path.join(self.home, ".datmo/database")
                }
            },
        }

