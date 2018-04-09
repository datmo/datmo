import os

from datmo.controller.base import BaseController
from datmo.controller.code.code import CodeController
from datmo.controller.file.file_collection import FileCollectionController
from datmo.controller.environment.environment import EnvironmentController
from datmo.util.i18n import get as _
from datmo.util.file_storage import JSONKeyValueStore
from datmo.util.exceptions import RequiredArgumentMissing, \
    FileIOException


class SnapshotController(BaseController):
    """SnapshotController inherits from BaseController and manages business logic related to snapshots

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
    def __init__(self, home, dal_driver=None):
        super(SnapshotController, self).__init__(home, dal_driver)
        self.code = CodeController(home, self.dal.driver)
        self.file_collection = FileCollectionController(home, self.dal.driver)
        self.environment = EnvironmentController(home, self.dal.driver)

    def create(self, dictionary):
        """Create snapshot object

        Parameters
        ----------
        dictionary : dict
            Includes a set of keys defined below:
                filepaths : list
                    list of files or folder paths to include within the snapshot
                environment_definition_filepath : str
                    filepath for the environment definition file (e.g. Dockerfile path for Docker)
                config_filename : str
                    name of file with configuration parameters
                stats_filename : str
                    name of file with metrics and statistics

        Returns
        -------
        SnapshotCommand
            SnapshotCommand object as specified in datmo.entity.snapshot

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
            "session_id": self.current_session.id
        }

        ## Required args
        required_args = ["code_id", "environment_id", "file_collection_id",
                         "config", "stats"]
        for required_arg in required_args:
            # Add in any values that are
            if required_arg in dictionary:
                create_dict[required_arg] = dictionary[required_arg]
            else:
                # Code setup
                if required_arg == "code_id":
                    create_dict['code_id'] = self.code.\
                        create().id
                # File setup
                elif required_arg == "file_collection_id":
                    # transform file paths to file_collection_id
                    if "filepaths" not in dictionary:
                        raise RequiredArgumentMissing(_("error",
                                                        "controller.snapshot.create.arg",
                                                        required_arg))
                    create_dict['file_collection_id'] = self.file_collection.\
                        create(dictionary['filepaths']).id
                # Environment setup
                elif required_arg == "environment_id":
                    if "environment_definition_filepath" not in dictionary:
                        raise RequiredArgumentMissing(_("error",
                                                        "controller.snapshot.create.arg",
                                                        required_arg))
                    create_dict['environment_id'] = self.environment.create({
                        "definition_filepath": dictionary['environment_definition_filepath']
                    }).id
                # Config setup
                elif required_arg == "config":
                    # transform file to config dict
                    if "config_filename" not in dictionary:
                        raise RequiredArgumentMissing(_("error",
                                                        "controller.snapshot.create.arg",
                                                        required_arg))
                    possible_paths = [os.path.join(self.home, dictionary['config_filename'])] + \
                        [os.path.join(self.home, filepath, dictionary['config_filename'])
                         for filepath in dictionary['filepaths'] if os.path.isdir(filepath)]
                    existing_possible_paths = [possible_path for possible_path in possible_paths
                                               if os.path.isfile(possible_path)]
                    if not existing_possible_paths:
                        raise FileIOException(_("error",
                                                "controller.snapshot.create.file_config"))
                    config_json_driver = JSONKeyValueStore(existing_possible_paths[0])
                    create_dict['config'] = config_json_driver.to_dict()
                # Stats setup
                elif required_arg == "stats":
                    # transform stats file to stats dict
                    if "stats_filename" not in dictionary:
                        raise RequiredArgumentMissing(_("error",
                                                        "controller.snapshot.create.arg",
                                                        required_arg))
                    possible_paths = [os.path.join(self.home, dictionary['stats_filename'])] + \
                                     [os.path.join(self.home, filepath, dictionary['stats_filename'])
                                      for filepath in dictionary['filepaths'] if os.path.isdir(filepath)]
                    existing_possible_paths = [possible_path for possible_path in possible_paths
                                               if os.path.isfile(possible_path)]
                    if not existing_possible_paths:
                        raise FileIOException(_("error",
                                                "controller.snapshot.create.file_stat"))
                    stats_json_driver = JSONKeyValueStore(existing_possible_paths[0])
                    create_dict['stats'] = stats_json_driver.to_dict()
                else:
                    raise RequiredArgumentMissing(_("error",
                                                    "controller.snapshot.create.arg",
                                                    required_arg))

        ## Optional args
        optional_args = ["session_id", "task_id", "message", "label"]
        for optional_arg in optional_args:
            if optional_arg in dictionary:
                create_dict[optional_arg] = dictionary[optional_arg]


        # Create snapshot and return
        return self.dal.snapshot.create(create_dict)

    def checkout(self, id):
        # Get snapshot object
        snapshot_obj = self.dal.snapshot.get_by_id(id)

        # Create new code_driver ref to revert back (if needed)
        # TODO: Save this to be reverted to
        current_code_obj = self.code.create()

        # Checkout code_driver to the relevant code_driver ref
        self.code_driver.checkout_code(snapshot_obj.code_id)

        # Pull file collection to the project home
        dst_dirpath = os.path.join(self.home, "datmo_snapshots", id)
        self.file_driver.create(dst_dirpath, dir=True)
        self.file_driver.transfer_collection(snapshot_obj.file_collection_id,
                                             dst_dirpath)
        return True

    def list(self, session_id=None):
        query = {}
        if session_id:
            query['session_id'] = session_id
        return self.dal.snapshot.query(query)

    def delete(self, id):
        return self.dal.snapshot.delete(id)