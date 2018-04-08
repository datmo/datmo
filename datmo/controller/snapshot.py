import os

from datmo.controller.base import BaseController
from datmo.util.i18n import get as _
from datmo.util.file_storage import JSONKeyValueStore
from datmo.util.exceptions import RequiredArgumentMissing, \
    FileIOException

class SnapshotController(BaseController):
    """
    SnapshotController inherits from BaseController and manages business logic related to snapshots

    Methods
    -------
    create(dictionary)
        Create a snapshot within the project
    checkout(id)
        Checkout to a specific snapshot within the project
    list()
        List all snapshots present within the project
    delete(id)
        Delete the snapshot specified from the project

    """
    def __init__(self, home, dal_driver=None):
        super(SnapshotController, self).__init__(home, dal_driver)

    def create(self, dictionary):
        """
        Create snapshot object

        Parameters
        ----------
        dictionary : dict
            Includes a set of keys defined below:
                filepaths : list
                    List of files or folder paths to include within the snapshot
                config_filename : str
                    Name of file with configuration parameters
                stats_filename : str
                    Name of file with metrics and statistics
        environment_def_path : str
            Filepath for the environment definition file (e.g. Dockerfile path for Docker)

        Returns
        -------
        SnapshotCommand
            SnapshotCommand object as specified in datmo.entity.snapshot

        Raises
        ------
        RequiredArgumentMissing
            If required arguments are not given by the user
        FileIOException
            If files are not present or there is an error in File IO

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
                    create_dict['code_id'] = self.code_driver.\
                        create_code_ref()
                # File setup
                elif required_arg == "file_collection_id":
                    # transform file paths to file_collection_id
                    if "filepaths" not in dictionary:
                        raise RequiredArgumentMissing(_("error",
                                                        "controller.snapshot.create.arg",
                                                        required_arg))
                    create_dict['file_collection_id'] = self.file_driver.\
                        create_collection(dictionary['filepaths'])
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
        self.code_driver.create_code_ref()

        # Checkout code_driver to the relevant code_driver ref
        self.code_driver.checkout_code_ref(snapshot_obj.code_id)

        # Pull file collection to the project home
        dst_dirpath = os.path.join(self.home, "datmo_snapshots", id)
        self.file_driver.create(dst_dirpath, dir=True)
        self.file_driver.transfer_collection(snapshot_obj.file_collection_id,
                                             dst_dirpath)
        return True

    def list(self):
        # Get all snapshot objects for this project
        return self.dal.snapshot.query({})

    def delete(self, id):
        return self.dal.snapshot.delete(id)