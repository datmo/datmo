import datetime

from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.entity.model import Model
from datmo.core.entity.session import Session
from datmo.core.util.exceptions import (SessionDoesNotExistException,
                                        RequiredArgumentMissing)


class ProjectController(BaseController):
    """ProjectController inherits from BaseController and manages business logic related to the
    project. One model is associated with each project currently.

    Parameters
    ----------
    home : str
        home path of the project

    Methods
    -------
    init(name, description)
        Initialize the project repository as a new model or update the existing project
    cleanup()
        Remove all datmo references from the current repository. NOTE: THIS WILL DELETE ALL DATMO WORK
    status()
        Give the user a picture of the status of the project, snapshots, and tasks
    """

    def __init__(self, home):
        super(ProjectController, self).__init__(home)

    def init(self, name, description):
        # Error if name is not given
        if not name:
            raise RequiredArgumentMissing(
                __("error", "controller.project.init.arg", "name"))

        # Create the Model, is it new or update?
        is_new_model = False
        if not self.model:
            _ = self.dal.model.create(
                Model({
                    "name": name,
                    "description": description
                }))
            is_new_model = True
        else:
            self._model = self.dal.model.update({
                "id": self.model.id,
                "name": name,
                "description": description
            })

        # Initialize Code Manager if needed
        if not self.code_driver.is_initialized:
            self.code_driver.init()

        # Initialize File Manager if needed
        if not self.file_driver.is_initialized:
            self.file_driver.init()

        # Initialize Environment Manager if needed
        if not self.environment_driver.is_initialized:
            self.environment_driver.init()

        # Build the initial default Environment (NOT NECESSARY)
        # self.environment_driver.build_image(tag="datmo-" + \
        #                                  self.model.name)

        # Add in Project template files if specified
        # TODO: Add in project template files

        # Create and set current session
        if is_new_model:
            # Create new default session
            _ = self.dal.session.create(
                Session({
                    "name": "default",
                    "model_id": self.model.id,
                    "current": True
                }))
        else:
            if not self.current_session:
                default_session_obj = self.dal.session.query({
                    "name": "default",
                    "model_id": self.model.id
                })
                if not default_session_obj:
                    raise SessionDoesNotExistException(
                        __("error", "controller.project.init"))
                # Update default session to be current
                self.dal.session.update({
                    "id": default_session_obj.id,
                    "current": True
                })
        return True

    def cleanup(self):
        # Obtain image id before cleaning up if exists
        images = self.environment_driver.list_images(name="datmo-" + \
                                                          self.model.name)
        image_id = images[0].id if images else None

        # Remove Datmo code_driver references
        self.code_driver.delete_code_refs_dir()

        # Remove Datmo file structure
        self.file_driver.delete_datmo_file_structure()

        if image_id:
            # Remove image created during init
            self.environment_driver.remove_image(
                image_id_or_name=image_id, force=True)

            # Remove any dangling images (optional)

            # Stop and remove all running environments with image_id
            self.environment_driver.stop_remove_containers_by_term(
                image_id, force=True)

        return True

    def status(self):
        # TODO: Convert pseudocode

        status_dict = {}

        # Ensure structure is good
        status_dict["is_owner"] = True \
            if self.model.user_id == self.logged_in_user_id \
            else False
        status_dict["code_initialized"] = self.code_driver.is_initialized
        status_dict["file_initialized"] = self.file_driver.is_initialized
        status_dict[
            "environment_initialized"] = self.environment_driver.is_initialized

        # Show all project settings
        status_dict["settings"] = self.settings.driver.to_dict()

        # Find the current time
        current_timestamp = datetime.datetime.now()

        # Show the latest snapshot
        latest_snapshot = self.dal.snapshot.get_latest()

        # Show unstaged tasks
        self.dal.task.query("created_at < " + latest_snapshot.created_at)
