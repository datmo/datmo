import os

from datmo.core.util.i18n import get as __
from datmo.core.util.logger import DatmoLogger
from datmo.core.util import get_class_contructor
from datmo.core.util.json_store import JSONStore
from datmo.core.util.exceptions import (InvalidProjectPath)
from datmo.config import Config


class BaseController(object):
    """BaseController is used to setup the repository. It serves as the basis for all other Controller objects

    Parameters
    ----------
    home : str, optional
        directory for the project, default is to pull from config

    Attributes
    ----------
    home : str
        absolute filepath for the location of the project
    config : JSONStore
        this is the set of configurations used to create a project
    dal : datmo.core.storage.DAL
    model : datmo.core.entity.model.Model
    code_driver : datmo.core.controller.code.driver.CodeDriver
    file_driver : datmo.core.controller.file.driver.FileDriver
    environment_driver : datmo.core.controller.environment.driver.EnvironmentDriver
    is_initialized : bool

    Methods
    -------
    dal_instantiate()
        Instantiate a version of the DAL
    set_config_value(key, default_value)
        Returns value adn sets to default if no value present
    config_loader(key)
        Return the config dictionary based on key
    get_config_defaults()
        Return the configuration defaults
    """

    def __init__(self, home=None):
        self.home = Config().home if not home else home
        if not os.path.isdir(self.home):
            raise InvalidProjectPath(
                __("error", "controller.base.__init__", self.home))
        self.logger = DatmoLogger.get_logger(__name__)
        # property caches and initial values
        self._is_initialized = False
        self._dal = None
        self._model = None
        self._code_driver = None
        self._file_driver = None
        self._environment_driver = None

    @property
    def file_driver(self):
        if self._file_driver == None:
            module_details = self.config_loader("controller.file.driver")
            self._file_driver = module_details["constructor"](
                **module_details["options"])
        return self._file_driver

    @property
    # Controller objects are only in sync if the data drivers are the same between objects
    # Currently pass dal_driver down from controller to controller to ensure syncing dals
    # TODO: To fix dal from different controllers so they sync within one session; they do NOT currently
    def dal(self):
        if self._dal == None:
            dal_dict = self.config_loader("storage.local")
            self._dal = dal_dict["constructor"](**dal_dict["options"])
        return self._dal

    @property
    def code_driver(self):
        if self._code_driver == None:
            module_details = self.config_loader("controller.code.driver")
            self._code_driver = module_details["constructor"](
                **module_details["options"])
        return self._code_driver

    @property
    def environment_driver(self):
        if self._environment_driver == None:
            module_details = self.config_loader(
                "controller.environment.driver")
            self._environment_driver = module_details["constructor"](
                **module_details["options"])
        return self._environment_driver

    @property
    def is_initialized(self):
        if not self._is_initialized:
            if self.file_driver.is_initialized and \
                self.dal.is_initialized and \
                self.code_driver.is_initialized and \
                self.environment_driver.is_initialized and \
                self.model:
                self._is_initialized = True
        return self._is_initialized

    @property
    def model(self):
        if not self.dal.is_initialized:
            self._model = None
        else:
            models = self.dal.model.query({})
            self._model = models[0] if models else None
        return self._model

    def config_loader(self, key):
        defaults = self.get_config_defaults()
        module_details = defaults[key]
        module_details["constructor"] = get_class_contructor(
            module_details["class_constructor"])
        return module_details

    def get_config_defaults(self):
        return {
            "controller.code.driver": {
                "class_constructor":
                    "datmo.core.controller.code.driver.file.FileCodeDriver",
                "options": {
                    "root": self.home,
                    "datmo_directory_name": Config().datmo_directory_name
                }
            },
            "controller.file.driver": {
                "class_constructor":
                    "datmo.core.controller.file.driver.local.LocalFileDriver",
                "options": {
                    "root": self.home,
                    "datmo_directory_name": Config().datmo_directory_name
                }
            },
            "controller.environment.driver": {
                "class_constructor":
                    "datmo.core.controller.environment.driver.dockerenv.DockerEnvironmentDriver",
                "options": {
                    "root": self.home,
                    "datmo_directory_name": Config().datmo_directory_name,
                    "docker_execpath": "docker"
                }
            },
            "storage.local": {
                "class_constructor": "datmo.core.storage.local.dal.LocalDAL",
                "options": {
                    "driver_type": "blitzdb",
                    "driver_options": {
                        "driver_type":
                            "file",
                        "connection_string":
                            os.path.join(self.home,
                                         Config().datmo_directory_name,
                                         "database")
                    }
                }
            },
        }
