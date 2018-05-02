import os

from datmo.core.controller.base import BaseController
from datmo.core.controller.code.code import CodeController
from datmo.core.controller.file.file_collection import FileCollectionController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.entity.snapshot import Snapshot
from datmo.core.util.i18n import get as __
from datmo.core.util.json_store import JSONStore
from datmo.core.util.exceptions import FileIOException, RequiredArgumentMissing, \
    ProjectNotInitializedException, SessionDoesNotExistException, EntityNotFound, \
    TaskNotComplete


class SnapshotController(BaseController):
    """SnapshotController inherits from BaseController and manages business logic related to snapshots

    Parameters
    ----------
    home : str
        home path of the project

    Attributes
    ----------
    code : CodeController
    file_collection : FileCollectionController
    environment : EnvironmentController

    Methods
    -------
    create(dictionary)
        Create a snapshot within the project
    checkout(id)
        Checkout to a specific snapshot within the project
    list(session_id=None)
        List all snapshots present within the project based on given filters
    delete(id)
        Delete the snapshot specified from the project

    """

    def __init__(self, home):
        super(SnapshotController, self).__init__(home)
        self.code = CodeController(home)
        self.file_collection = FileCollectionController(home)
        self.environment = EnvironmentController(home)
        if not self.is_initialized:
            raise ProjectNotInitializedException(
                __("error", "controller.snapshot.__init__"))

    def create(self, incoming_dictionary):
        """Create snapshot object

        Parameters
        ----------
        dictionary : dict

            for each of the 5 key components, this function will search for
            one of the variables below starting from the top. Default functionality
            is described below for each component as well for reference if none
            of the variables are given.

            code :
                code_id : str, optional
                    code reference associated with the snapshot; if not
                    provided will look to inputs below for code creation
                commit_id : str, optional
                    commit id provided by the user if already available

                Default
                -------
                commits will be taken and code created via the  CodeController
                and are added to the snapshot at the time of snapshot creation

            environment :
                environment_id : str, optional
                    id for environment used to create snapshot
                environment_definition_filepath : str, optional
                    absolute filepath for the environment definition file
                    (e.g. Dockerfile path for Docker)

                Default
                -------
                default environment files will be searched and environment will
                be created with the EnvironmentController and added to the snapshot
                at the time of snapshot creation

            file_collection :
                file_collection_id : str, optional
                    file collection associated with the snapshot
                filepaths : list, optional
                    list of files or folder paths to include within the snapshot

                Default
                -------
                filepaths will be considered empty ([]), and the FileCollectionController
                will create a blank FileCollection that is empty.

            config :
                config : dict, optional
                    key, value pairs of configurations
                config_filepath : str, optional
                    absolute filepath to configuration parameters file
                config_filename : str, optional
                    name of file with configuration parameters

                Default
                -------
                config will be considered empty ({}) and saved to the snapshot

            stats :
                stats : dict, optional
                    key, value pairs of metrics and statistics
                stats_filepath : str, optional
                    absolute filepath to stats parameters file
                stats_filename : str, optional
                    name of file with metrics and statistics.

                Default
                -------
                stats will be considered empty ({}) and saved to the snapshot

            for the remaining optional arguments it will search for them
            in the input dictionary

                message : str
                    long description of snapshot
                session_id : str, optional
                    session id within which snapshot is created,
                    will overwrite default if given
                task_id : str, optional
                    task id associated with snapshot
                label : str, optional
                    short description of snapshot
                visible : bool, optional
                    True if visible to user via list command else False

        Returns
        -------
        Snapshot
            Snapshot object as specified in datmo.core.entity.snapshot

        Raises
        ------
        RequiredArgumentMissing
            if required arguments are not given by the user
        FileIOException
            if files are not present or there is an error in File IO
        """
        # Validate Inputs
        create_dict = {
            "model_id": self.model.id,
            "session_id": self.current_session.id,
        }

        # Message must be present
        if "message" in incoming_dictionary:
            create_dict['message'] = incoming_dictionary['message']
        else:
            raise RequiredArgumentMissing(
                __("error", "controller.snapshot.create.arg", "message"))

        # Code setup
        self._code_setup(incoming_dictionary, create_dict)

        # Environment setup
        self._env_setup(incoming_dictionary, create_dict)

        # File setup
        self._file_setup(incoming_dictionary, create_dict)

        # Config setup
        self._config_setup(incoming_dictionary, create_dict)

        # Stats setup
        self._stats_setup(incoming_dictionary, create_dict)

        # If snapshot object with required args already exists, return it
        # DO NOT create a new snapshot with the same required arguments
        results = self.dal.snapshot.query({
            "model_id": create_dict["model_id"],
            "code_id": create_dict['code_id'],
            "environment_id": create_dict['environment_id'],
            "file_collection_id": create_dict['file_collection_id'],
            "config": create_dict['config'],
            "stats": create_dict['stats']
        })
        if results: return results[0]

        # Optional args for Snapshot entity
        optional_args = ["task_id", "label", "visible"]
        for optional_arg in optional_args:
            if optional_arg in incoming_dictionary:
                create_dict[optional_arg] = incoming_dictionary[optional_arg]

        # Create snapshot and return
        return self.dal.snapshot.create(Snapshot(create_dict))

    def create_from_task(self, message, task_id):
        """Create snapshot from a completed task.
        # TODO: enable create from task DURING a run

        Parameters
        ----------
        message : str
            long description of snapshot
        task_id : str
            task object to use to create snapshot

        Returns
        -------
        Snapshot
            Snapshot object as specified in datmo.core.entity.snapshot

        Raises
        ------
        TaskNotComplete
            if task specified has not been completed
        """
        task_obj = self.dal.task.get_by_id(task_id)

        if not task_obj.status and not task_obj.after_snapshot_id:
            raise TaskNotComplete(
                __("error", "controller.snapshot.create_from_task",
                   str(task_obj.id)))

        return self.dal.snapshot.update({
            "id": task_obj.after_snapshot_id,
            "message": message,
            "stats": task_obj.results,
            "visible": True
        })

    def checkout(self, snapshot_id):
        # Get snapshot object
        snapshot_obj = self.dal.snapshot.get_by_id(snapshot_id)
        code_obj = self.dal.code.get_by_id(snapshot_obj.code_id)
        file_collection_obj = self.dal.file_collection.\
            get_by_id(snapshot_obj.file_collection_id)

        # Create new code_driver ref to revert back (if needed)
        # TODO: Save this to be reverted to
        current_code_obj = self.code.create()

        # Checkout code_driver to the relevant commit ref
        self.code_driver.checkout_ref(code_obj.commit_id)

        # Pull file collection to the project home
        dst_dirpath = os.path.join("datmo_snapshots", snapshot_id)
        abs_dst_dirpath = self.file_driver.create(dst_dirpath, directory=True)
        self.file_driver.transfer_collection(file_collection_obj.filehash,
                                             abs_dst_dirpath)
        return True

    def list(self, session_id=None, visible=None):
        query = {}
        if session_id:
            try:
                self.dal.session.get_by_id(session_id)
            except EntityNotFound:
                raise SessionDoesNotExistException(
                    __("error", "controller.snapshot.list", session_id))
            query['session_id'] = session_id
        if visible is not None and isinstance(visible, bool):
            query['visible'] = visible

        return self.dal.snapshot.query(query)

    def delete(self, snapshot_id):
        if not snapshot_id:
            raise RequiredArgumentMissing(
                __("error", "controller.snapshot.delete.arg", "snapshot_id"))
        return self.dal.snapshot.delete(snapshot_id)

    def _code_setup(self, incoming_dictionary, create_dict):
        """ Set the code_id by using:
            1. code_id
            2. commit_id string, which creates a new code_id
            3. create a new code id

        Parameters
        ----------
        incoming_dictionary : dict
            dictionary for the create function defined above
        create_dict : dict
            dictionary for creating the Snapshot entity
        """

        if "code_id" in incoming_dictionary:
            create_dict['code_id'] = incoming_dictionary['code_id']
        elif "commit_id" in incoming_dictionary:
            create_dict['code_id'] = self.code.\
                create(commit_id=incoming_dictionary['commit_id']).id
        else:
            create_dict['code_id'] = self.code.create().id

    def _env_setup(self, incoming_dictionary, create_dict):
        """ TODO:

        Parameters
        ----------
        incoming_dictionary : dict
            dictionary for the create function defined above
        create_dict : dict
            dictionary for creating the Snapshot entity
        """

        language = incoming_dictionary.get("language", None)
        if "environment_id" in incoming_dictionary:
            create_dict['environment_id'] = incoming_dictionary[
                'environment_id']
        elif "environment_definition_filepath" in incoming_dictionary:
            create_dict['environment_id'] = self.environment.create({
                "definition_filepath":
                    incoming_dictionary['environment_definition_filepath']
            }).id
        elif language:
            create_dict['environment_id'] = self.environment.\
                create({"language": language}).id
        else:
            # create some default environment
            create_dict['environment_id'] = self.environment.\
                create({}).id

    def _file_setup(self, incoming_dictionary, create_dict):
        """ TODO:

        Parameters
        ----------
        incoming_dictionary : dict
            dictionary for the create function defined above
        create_dict : dict
            dictionary for creating the Snapshot entity
        """

        if "file_collection_id" in incoming_dictionary:
            create_dict['file_collection_id'] = incoming_dictionary[
                'file_collection_id']
        elif "filepaths" in incoming_dictionary:
            # transform file paths to file_collection_id
            create_dict['file_collection_id'] = self.file_collection.\
                create(incoming_dictionary['filepaths']).id
        else:
            # create some default file collection
            create_dict['file_collection_id'] = self.file_collection.\
                create([]).id

    def _config_setup(self, incoming_dictionary, create_dict):
        """ Fills in snapshot config by having one of the following:
            1. config = JSON object
            2. config_filepath = some location where a json file exists
            3. config_filename = just the file nam
        Parameters
        ----------
        incoming_dictionary : dict
            dictionary for the create function defined above
        create_dict : dict
            dictionary for creating the Snapshot entity

        Raises
        ------
        FileIOException
        """
        if "config" in incoming_dictionary:
            create_dict['config'] = incoming_dictionary['config']
        elif "config_filepath" in incoming_dictionary:
            if not os.path.isfile(incoming_dictionary['config_filepath']):
                raise FileIOException(
                    __("error", "controller.snapshot.create.file_config"))
            # If path exists transform file to config dict
            config_json_driver = JSONStore(
                incoming_dictionary['config_filepath'])
            create_dict['config'] = config_json_driver.to_dict()
        elif "config_filename" in incoming_dictionary:
            config_filename = incoming_dictionary['config_filename'] \
                if "config_filename" in incoming_dictionary else "config.json"
            create_dict['config'] = self._find_in_filecollection(
                config_filename, create_dict['file_collection_id'])
        else:
            create_dict['config'] = {}

    def _stats_setup(self, incoming_dictionary, create_dict):
        """Fills in snapshot stats by having one of the following:
            1. stats = JSON object
            2. stats_filepath = some location where a json file exists
            3. stats_filename = just the file name

        Parameters
        ----------
        incoming_dictionary : dict
            dictionary for the create function defined above
        create_dict : dict
            dictionary for creating the Snapshot entity

        Raises
        ------
        FileIOException
        """

        if "stats" in incoming_dictionary:
            create_dict['stats'] = incoming_dictionary['stats']
        elif "stats_filepath" in incoming_dictionary:
            if not os.path.isfile(incoming_dictionary['stats_filepath']):
                raise FileIOException(
                    __("error", "controller.snapshot.create.file_stat"))
            # If path exists transform file to config dict
            stats_json_driver = JSONStore(
                incoming_dictionary['stats_filepath'])
            create_dict['stats'] = stats_json_driver.to_dict()
        elif "stats_filename" in incoming_dictionary:
            stats_filename = incoming_dictionary['stats_filename'] \
                if "stats_filename" in incoming_dictionary else "stats.json"
            create_dict['stats'] = self._find_in_filecollection(
                stats_filename, create_dict['file_collection_id'])
        else:
            create_dict['stats'] = {}

    def _find_in_filecollection(self, file_to_find, file_collection_id):
        """ Attempts to find a file within the file collection

        Returns
        -------
        dict
            output dictionary of the JSON file
        """

        file_collection_obj = self.file_collection.dal.file_collection.\
            get_by_id(file_collection_id)
        file_collection_path = \
            self.file_collection.file_driver.get_collection_path(
                file_collection_obj.filehash)
        # find all of the possible paths it could exist
        possible_paths = [os.path.join(self.home, file_to_find)] + \
                            [os.path.join(self.home, item[0], file_to_find)
                            for item in os.walk(file_collection_path)]
        existing_possible_paths = [
            possible_path for possible_path in possible_paths
            if os.path.isfile(possible_path)
        ]
        if not existing_possible_paths:
            # TODO: Add some info / warning that no file was found
            # create some default stats
            return {}
        else:
            # If any such path exists, transform file to stats dict
            json_file = JSONStore(existing_possible_paths[0])
            return json_file.to_dict()
