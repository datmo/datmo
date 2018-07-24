from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class EnvironmentDriver(with_metaclass(ABCMeta, object)):
    """EnvironmentDriver is the parent of all environment drivers. Any child must implement the methods below

    Methods
    -------
    setup(output_path)
        create environment definition
    create(path, output_path)
        create datmo environment definition
    build(name, path)
        build the environment
    run(name, options, log_filepath)
        run the built environment
    stop(run_id, force=False)
        stop the run created with the environment
    remove(name, force=False)
        remove the environment
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def init(self):
        """Initialize the environment driver

        Returns
        -------
        bool
            returns True if success else False

        Raises
        ------
        EnvironmentInitFailed
        """

    @abstractmethod
    def get_environment_types(self):
        """Get the environment types

        Returns
        -------
        list
            List of supported environment types
        """

    @abstractmethod
    def get_supported_frameworks(self, environment_type):
        """Get all the supported frameworks

        Parameters
        ----------
        environment_type : str
            the type of environment

        Returns
        -------
        list
            List of available environment frameworks and their information
        """

    @abstractmethod
    def get_supported_languages(self, environment_type, environment_framework):
        """Get all the supported environment languages

        Parameters
        ----------
        environment_type : str
            the type of environment
        environment_framework : str
            the framework for the environment

        Returns
        -------
        list
            List of available languages for these environment options
        """

    @abstractmethod
    def setup(self, options, definition_path):
        """Create the supported environment definition file in given path

        Parameters
        ----------
        options : dict
            can include the following values:

            name : str
                the name of environment to be used for the environment definition file
        definition_path : str, optional
            absolute output path for environment definition file
            (default is None, which sets up the file in the project environment directory,
            e.g. `Dockerfile` in `datmo_environment` folder)


        Returns
        -------
        bool
            True is success

        Raises
        ------
        PathDoesNotExist
            if the definition_path given does not exist
        """

    @abstractmethod
    def create(self, path=None, output_path=None, workspace=None):
        """Create datmo environment definition

        Parameters
        ----------
        path : str, optional
            absolute input definition file path
            (default is None, which searches for standard filename in project root,
            e.g. `Dockerfile` in project root for docker driver)
        output_path : str, optional
            absolute datmo output definition file path
            (default is None, which creates a name of above file with `datmo` prefixed
            in the same directory as `path`. e.g. `datmoDockerfile` in
            the project root for the default above for docker driver)
        workspace : str, optional
            workspace being used while running the task
        Returns
        -------
        tuple
            success : bool
                True if success
            path : str
                absolute path for original definition
            output_path : str
                absolute path for datmo definition
        """

    @abstractmethod
    def build(self, name, path, workspace):
        """Build an environment from a definition path

        Parameters
        ----------
        name : str
            name to give to the environment built
        path : str
            absolute path to the definition file
        workspace : str


        Returns
        -------
        bool
            True if success

        Raises
        ------
        EnvironmentExecutionError
        """
        pass

    @abstractmethod
    def extract_workspace_url(self, container_name, workspace=None):
        """Extract workspace url from the container

        Parameters
        ----------
        container_name : str
            name of the container being run
        workspace : str
            workspace being used for the run

        Returns
        -------
        str
            web url for the workspace being run, None if it doesn't exist
        """
        pass

    @abstractmethod
    def run(self, name, options, log_filepath):
        """Run and log an instance of the environment with the options given

        Parameters
        ----------
        name : str
            name of the built environment
        options : dict
            can include the following values:

            command : list
            ports : list
                Here are some example ports used for common applications.
                   *  'jupyter notebook' - 8888
                   *  flask API - 5000
                   *  tensorboard - 6006
            name : str
            volumes : dict
            detach : bool
            stdin_open : bool
            tty : bool
        log_filepath : str
            filepath to the log file

        Returns
        -------
        return_code : int
            system return code for container and logs
        run_id : str
            identification for run of the environment
        logs : str
            string version of output logs for the container
        """
        pass

    @abstractmethod
    def stop(self, run_id, force=False):
        """Stop and remove a run that is currently running

        Parameters
        ----------
        run_id : str
            run id returned by the run command
        force : bool, optional
            force stop of container

        Returns
        -------
        bool
            True if success
        """
        pass

    @abstractmethod
    def remove(self, name, force=False):
        """Remove built environment from driver memory

        Parameters
        ----------
        name : str
            name of the built environment
        force : bool, optional
            force removal of built environment

        Returns
        -------
        bool
            True if success
        """
        pass

    @staticmethod
    @abstractmethod
    def create_default_definition(directory, language="python3"):
        """Create default definition within the given directory and return full path

        Parameters
        ----------
        directory : str
            directory to create default definition file within
        language : str, optional
            language of the environment to support
            (default is "python3")

        Returns
        -------
        str
            full path of the created default definition path
        """

    @abstractmethod
    def get_default_definition_filename(self):
        """Get default definition path to read the file from

        Returns
        -------
        str
            file names of the default definition file
        """

    @abstractmethod
    def get_datmo_definition_filenames(self):
        """Get the filenames of datmo definition files

        Returns
        -------
        list
            list of file names of the datmo definition file
        """

    @staticmethod
    @abstractmethod
    def create_datmo_definition(input_definition_path,
                                output_definition_path,
                                workspace=None):
        """Create a datmo version of the definition

        Parameters
        ----------
        input_definition_path : str
            input original definition path to read from
        output_definition_path : str
            output datmo definition path to write to
        workspace : str, optional
            workspace being used while running the task
        Returns
        -------
        bool
            True is success
        """
