import os

from datmo.config import Config
from datmo.core.util.validation import validate
from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.controller.code.code import CodeController
from datmo.core.controller.environment.environment import EnvironmentController
from datmo.core.controller.file.file_collection import FileCollectionController
from datmo.core.controller.snapshot import SnapshotController
from datmo.core.entity.model import Model
from datmo.core.util.json_store import JSONStore
from datmo.core.util.exceptions import (ProjectNotInitialized,
                                        EnvironmentConnectFailed, FileIOError,
                                        UnstagedChanges, PathDoesNotExist)


class ProjectController(BaseController):
    """ProjectController inherits from BaseController and manages business logic related to the
    project. One model is associated with each project currently.

    Methods
    -------
    init(name, description)
        Initialize the project repository as a new model or update the existing project
    cleanup()
        Remove all datmo references from the current repository. NOTE: THIS WILL DELETE ALL DATMO WORK
    status()
        Give the user a picture of the status of the project, snapshots, and tasks
    """

    def __init__(self):
        super(ProjectController, self).__init__()

    def init(self, name, description):
        """ Initialize the project

        This function will initialize the project or reinitialize it the project is
        already initialized.

        Parameters
        ----------
        name : str
        description : str

        Returns
        -------
        bool
        """
        is_new_model = False
        old_model = self.model
        if not self.model:
            is_new_model = True

        try:
            # Always validate inputs to the init function
            validate("create_project", {
                "name": name,
                "description": description
            })

            # Initialize File Driver if needed
            if not self.file_driver.is_initialized:
                self.file_driver.init()

            # Initialize the dal
            if not self.dal.is_initialized:
                self.dal.init()

            # Initialize Code Driver if needed
            if not self.code_driver.is_initialized:
                self.code_driver.init()

            # Initialize Environment Driver if needed
            if not self.environment_driver.is_initialized:
                self.environment_driver.init()

            # Initialize the config JSON store
            self.config_store = JSONStore(
                os.path.join(self.home,
                             Config().datmo_directory_name, ".config"))

            # Create model if new else update
            if is_new_model:
                _ = self.dal.model.create(
                    Model({
                        "name": name,
                        "description": description
                    }))
            else:
                self._model = self.dal.model.update({
                    "id": self.model.id,
                    "name": name,
                    "description": description
                })

            # Connect Environment Driver if needed
            # (not required but will warn if not present)
            try:
                if not self.environment_driver.is_connected:
                    self.environment_driver.connect()
            except EnvironmentConnectFailed:
                self.logger.warning(
                    __("warn", "controller.general.environment.failed"))

            # Build the initial default Environment (NOT NECESSARY)
            # self.environment_driver.build_image(tag="datmo-" + \
            #                                  self.model.name)
            return True
        except Exception:
            # if any error occurred with new model, ensure no initialize occurs and raise previous error
            # if any error occurred with existing model, ensure no updates were made, raise previous error
            if is_new_model:
                self.cleanup()
            else:
                self._model = self.dal.model.update({
                    "id": old_model.id,
                    "name": old_model.name,
                    "description": old_model.description
                })
            raise

    def cleanup(self):
        """Cleans the project structure completely

        Notes
        -----
        This function will not error out but will gracefully exit, since
        it is used in cases where init fails as a check against mid-initialized
        projects

        Returns
        -------
        bool
        """
        if not self.is_initialized:
            self.logger.warning(
                __("warn", "controller.project.cleanup.not_init"))
        # Remove Datmo environment_driver references, give warning if error
        try:
            # Obtain image id before cleaning up if exists
            images = self.environment_driver.list_images(name="datmo-" + \
                                                              self.model.name)
            image_id = images[0].id if images else None
        except Exception:
            self.logger.warning(
                __("warn", "controller.project.cleanup.environment"))

        # Remove Datmo code_driver references, give warning if error
        try:
            if self.code_driver.is_initialized:
                for ref in self.code_driver.list_refs():
                    self.code_driver.delete_ref(ref)
        except Exception:
            self.logger.warning(__("warn", "controller.project.cleanup.code"))
        try:
            # Remove Hidden Datmo file structure, give warning if error
            self.file_driver.delete_hidden_datmo_file_structure()
        except (FileIOError, PathDoesNotExist):
            self.logger.warning(__("warn", "controller.project.cleanup.files"))

        try:
            if image_id:
                # Remove image created during init
                self.environment_driver.remove_image(
                    image_id_or_name=image_id, force=True)

                # Remove any dangling images (optional)

                # Stop and remove all running environments with image_id
                self.environment_driver.stop_remove_containers_by_term(
                    image_id, force=True)
        except Exception:
            self.logger.warning(
                __("warn", "controller.project.cleanup.environment"))

        return True

    def status(self):
        """Return the project status information if initialized

        Returns
        -------
        status_dict : dict
            dictionary with project metadata and config
        current_snapshot : datmo.core.entity.snapshot.Snapshot
            snapshot object of the current state of the repo if present else None
        latest_snapshot_user_generated : datmo.core.entity.snapshot.Snapshot
            snapshot object of the latest snapshot generated by the user if present else None
        latest_snapshot_auto_generated : datmo.core.entity.snapshot.Snapshot
            snapshot object of the latest snapshot generated automatically by datmo if present else None
        unstaged_code : bool
            True if code has unstaged changes
        unstaged_environment : bool
            True if environment has unstaged changes
        unstaged_files : bool
            True if files have unstaged changes
        """
        if not self.is_initialized:
            raise ProjectNotInitialized(
                __("error", "controller.project.status"))
        # TODO: Add in note when environment is not setup or intialized

        # Add in project metadata
        status_dict = self.model.to_dictionary().copy()

        # Find  all project settings
        status_dict["config"] = self.config_store.to_dict()

        # Find the latest snapshot generated by the user
        descending_snapshots = self.dal.snapshot.query(
            {
                "visible": True
            }, sort_key="created_at", sort_order="descending")
        latest_snapshot_user_generated = descending_snapshots[
            0] if descending_snapshots else None

        # Show the latest snapshot generated automatically by datmo
        descending_snapshots = self.dal.snapshot.query(
            {
                "visible": False
            }, sort_key="created_at", sort_order="descending")
        latest_snapshot_auto_generated = descending_snapshots[
            0] if descending_snapshots else None

        # TODO: add in latest run

        self.code_controller = CodeController()
        try:
            unstaged_code = self.code_controller.check_unstaged_changes()
        except UnstagedChanges:
            unstaged_code = True

        self.environment_controller = EnvironmentController()
        try:
            unstaged_environment = self.environment_controller.check_unstaged_changes(
            )
        except UnstagedChanges:
            unstaged_environment = True

        self.file_collection_controller = FileCollectionController()
        try:
            unstaged_files = self.file_collection_controller.check_unstaged_changes(
            )
        except UnstagedChanges:
            unstaged_files = True

        # If exists, obtain the current snapshot, if unstaged changes, will be None
        self.snapshot_controller = SnapshotController()
        try:
            current_snapshot = self.snapshot_controller.current_snapshot()
        except UnstagedChanges:
            current_snapshot = None

        return status_dict, current_snapshot, latest_snapshot_user_generated, latest_snapshot_auto_generated, \
               unstaged_code, unstaged_environment, unstaged_files
