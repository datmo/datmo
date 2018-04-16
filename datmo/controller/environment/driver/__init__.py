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
    def create(self, path, output_path):
        """
        Create datmo environment definition

        Parameters
        ----------
        path : str
            absolute input definition file path
        output_path : str
            absolute datmo output defintion file path

        Returns
        -------
        bool
            True if success
        """

    @abstractmethod
    def build(self, name, path):
        """
        Build an environment from a definition path

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
        EnvironmentExecutionException
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
            gpu : bool
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