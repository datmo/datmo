from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class EnvironmentDriver(with_metaclass(ABCMeta, object)):
    """EnvironmentDriver is the parent of all environment drivers. Any child must implement the methods below

    Methods
    -------
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
    def create(self, path=None, output_path=None, language=None):
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
        language : str, optional
            language of the code that is being used in the project
            (default is None, which means if a definition file is not given,
            and a default definition path is not found, and the language is supported
            a definition will automatically be created. If this is not supported
            in the EnvironmentDriver, then it will ignore this)

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
    def build(self, name, path):
        """Build an environment from a definition path

        Parameters
        ----------
        name : str
            name to give to the environment built
        path : str
            absolute path to the definition file

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