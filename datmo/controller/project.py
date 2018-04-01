import datetime
from .base import BaseController
from datmo.cli.driver.cli_helper import CLIHelper
from datmo.util.i18n import get as _
from datmo.util.exceptions import SessionDoesNotExistException


class ProjectController(BaseController):
    def __init__(self, home, cli_helper=CLIHelper()):
        super(ProjectController, self).__init__(home, cli_helper)

    def init(self, name, description):
        # Create the Model, is it new or update?
        self.cli_helper.echo(_('setup.init_project'))

        is_new_model = False
        if not self.model:
            model_obj = self.dal.model.create({
                "name": name,
                "description": description
            })

            self.settings.set('model_id', model_obj.id)
            is_new_model = True

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

        # Add template files to the DatmoProject
        self.file_driver.ensure_api_file()
        self.file_driver.ensure_script_file()

        # Create and set current Session
        if is_new_model:
            # Create new Session
            session_obj = self.dal.session.create({
                "name": "default",
                "model_id": self.model.id
            })
            # Set current Session
            self.settings.set('current_session_id', session_obj.id)
        else:
            if not self.current_session:
                session_obj = self.dal.session.query({
                    "name":"default",
                    "model_id": self.model.id
                })
                if not session_obj:
                    raise SessionDoesNotExistException("exception.datmo.project.init", {
                        "exception": "Session does not exist"
                    })
                # Set current Session
                self.settings.set('current_session_id', session_obj.id)

        # Update the settings in the Project
        update_dict = {}
        for k, v in update_dict.iteritems():
            self.settings.set(k, v)

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
            self.environment_driver.remove_image(image_id_or_name=image_id,
                                                 force=True)

            # Remove any dangling images (optional)

            # Stop and remove all running environments with image_id
            self.environment_driver.stop_remove_containers_by_term(image_id,
                                                                   force=True)

        return True


    def status(self):
        # TODO: Convert pseudocode into real code_driver

        status_dict = {}

        # Ensure structure is good
        status_dict["is_owner"] = True \
            if self.model.user_id == self.logged_in_user_id \
            else False
        status_dict["code_initialized"] = self.code_driver.is_initialized
        status_dict["file_initialized"] = self.file_driver.is_initialized
        status_dict["environment_initialized"] = self.environment_driver.is_initialized

        # Show all project settings
        status_dict["settings"] = self.settings.driver.to_dict()

        # Find the current time
        current_timestamp = datetime.datetime.now()

        # Show the latest snapshot
        latest_snapshot = self.dal.snapshot.get_latest()

        # Show unstaged tasks
        self.dal.task.query("created_at < " + latest_snapshot.created_at)


