import os

from datmo.core.util.i18n import get as __
from datmo.core.util import get_class_contructor
from datmo.core.util.json_store import JSONStore
from datmo.core.util.exceptions import InvalidProjectPathException, \
    DatmoModelNotInitializedException


class BaseController(object):
    """BaseController is used to setup the repository. It serves as the basis for all other Controller objects

    Parameters
    ----------
    home : str
        home path of the project
    dal_driver : DALDriver
        an instance of a DALDriver to use while accessing the DAL

    Attributes
    ----------
    home : str
        Filepath for the location of the project
    dal_driver : DALDriver object
        This is an instance of a storage DAL driver
    config : JSONStore
        This is the set of configurations used to create a project
    dal
    model
    current_session
    code_driver
    file_driver
    environment_driver
    is_initialized

    Methods
    -------
    dal_instantiate()
        Instantiate a version of the DAL
    get_or_set_default(key, default_value)
        Returns value adn sets to default if no value present
    config_loader(key)
        Return the config dictionary based on key
    get_config_defaults()
        Return the configuration defaults
    """

    def __init__(self, home):
        self.home = home
        if not os.path.isdir(self.home):
            raise InvalidProjectPathException(
                __("error", "controller.base.__init__", home))
        self.config = JSONStore(os.path.join(self.home, ".datmo", ".config"))
        # property caches and initial values
        self._dal = None
        self._model = None
        self._current_session = None
        self._code_driver = None
        self._file_driver = None
        self._environment_driver = None
        self._is_initialized = False

    @property
    # Controller objects are only in sync if the data drivers are the same between objects
    # Currently pass dal_driver down from controller to controller to ensure syncing dals
    # TODO: To fix dal from different controllers so they sync within one session; they do NOT currently
    def dal(self):
        """Property that is maintained in memory

        Returns
        -------
        DAL
        """
        if self._dal == None:
            self._dal = self.dal_instantiate()
        return self._dal

    @property
    def model(self):
        """Property that is maintained in memory

        Returns
        -------
        Model
        """
        if self._model == None:
            models = self.dal.model.query({})
            self._model = models[0] if models else None
        return self._model

    @property
    def current_session(self):
        """Property that is maintained in memory

        Returns
        -------
        Session
        """
        if not self.model:
            raise DatmoModelNotInitializedException(
                __("error", "controller.base.current_session"))
        if self._current_session == None:
            sessions = self.dal.session.query({"current": True})
            self._current_session = sessions[0] if sessions else None
        return self._current_session

    @property
    def code_driver(self):
        """Property that is maintained in memory

        Returns
        -------
        CodeDriver
        """
        if self._code_driver == None:
            module_details = self.config_loader("controller.code.driver")
            self._code_driver = module_details["constructor"](
                **module_details["options"])
        return self._code_driver

    @property
    def file_driver(self):
        """Property that is maintained in memory

        Returns
        -------
        FileDriver
        """
        if self._file_driver == None:
            module_details = self.config_loader("controller.file.driver")
            self._file_driver = module_details["constructor"](
                **module_details["options"])
        return self._file_driver

    @property
    def environment_driver(self):
        """Property that is maintained in memory

        Returns
        -------
        EnvironmentDriver
        """
        if self._environment_driver == None:
            module_details = self.config_loader(
                "controller.environment.driver")
            self._environment_driver = module_details["constructor"](
                **module_details["options"])
        return self._environment_driver

    @property
    def is_initialized(self):
        """Property that is maintained in memory

        Returns
        -------
        bool
            True if the project is property initialized else False
        """
        if not self._is_initialized:
            if self.code_driver.is_initialized and \
                self.environment_driver.is_initialized and \
                    self.file_driver.is_initialized:
                if self.model:
                    self._is_initialized = True
        return self._is_initialized

    def dal_instantiate(self):
        # first load driver, then create DAL using driver
        dal_driver_dict = self.config_loader("storage.driver")
        dal_driver = dal_driver_dict["constructor"](
            **dal_driver_dict["options"])
        # Get DAL, set driver,
        dal_dict = self.config_loader("storage.local")
        dal_dict["options"]["driver"] = dal_driver
        return dal_dict["constructor"](**dal_dict["options"])

    def get_or_set_default(self, key, default_value):
        value = self.config.get(key)
        if value is None:
            self.config.save(key, default_value)
            value = default_value
        return value

    def config_loader(self, key):
        defaults = self.get_config_defaults()
        module_details = self.get_or_set_default(key, defaults[key])
        module_details["constructor"] = get_class_contructor(
            module_details["class_constructor"])
        return module_details

    def get_config_defaults(self):
        return {
            "controller.code.driver": {
                "class_constructor":
                    "datmo.core.controller.code.driver.git.GitCodeDriver",
                "options": {
                    "filepath": self.home,
                    "execpath": "git"
                }
            },
            "controller.file.driver": {
                "class_constructor":
                    "datmo.core.controller.file.driver.local.LocalFileDriver",
                "options": {
                    "filepath": self.home
                }
            },
            "controller.environment.driver": {
                "class_constructor":
                    "datmo.core.controller.environment.driver.dockerenv.DockerEnvironmentDriver",
                "options": {
                    "filepath": self.home,
                    "docker_execpath": "docker"
                }
            },
            "storage.local": {
                "class_constructor": "datmo.core.storage.local.dal.LocalDAL",
                "options": {
                    "driver": "storage.driver"
                }
            },
            "storage.driver": {
                "class_constructor":
                    "datmo.core.storage.driver.blitzdb_dal_driver.BlitzDBDALDriver",
                "options": {
                    "driver_type":
                        "file",
                    "connection_string":
                        os.path.join(self.home, ".datmo/database")
                }
            },
        }
