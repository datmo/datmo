from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.entity.code import Code
from datmo.core.util.exceptions import PathDoesNotExist, EnvironmentInitFailed


class CodeController(BaseController):
    """CodeController inherits from BaseController and manages business logic related to the
    code.

    Parameters
    ----------
    home : str
        home path of the project

    Methods
    -------
    create(code_id=None)
        create a code object within the project
    list()
        list all code objects within the project
    delete(id)
        delete the specified code object from the project
    """

    def __init__(self):
        try:
            super(CodeController, self).__init__()
        except EnvironmentInitFailed:
            self.logger.warning(
                __("warn", "controller.general.environment.failed"))

    def create(self, commit_id=None):
        """Create a Code object

        Parameters
        ----------
        commit_id : str, optional
            if commit_id is already present, will not make a new reference and commit

        Returns
        -------
        Code
            an object representing the code reference created

        Raises
        ------
        RequiredArgumentMissing
            if any arguments above are not provided.
        """
        # Validate Inputs

        create_dict = {
            "model_id": self.model.id,
        }

        create_dict["driver_type"] = self.code_driver.type

        if commit_id:
            create_dict["commit_id"] = commit_id
        else:
            create_dict["commit_id"] = self.code_driver.create_ref()
        # If code object with commit id exists, return it
        results = self.dal.code.query({
            "commit_id": create_dict["commit_id"],
            "model_id": self.model.id
        })
        if results: return results[0]

        # Create code and return
        return self.dal.code.create(Code(create_dict))

    def list(self):
        # TODO: Add time filters
        return self.dal.code.query({"model_id": self.model.id})

    def delete(self, code_id):
        """Delete all traces of Code object

        Parameters
        ----------
        code_id : str
            code object id to remove

        Returns
        -------
        bool
            returns True if success else False

        Raises
        ------
        PathDoesNotExist
            if the specified Code does not exist.
        """
        code_obj = self.dal.code.get_by_id(code_id)
        if not code_obj:
            raise PathDoesNotExist(
                __("error", "controller.code.delete", code_id))
        # Remove code reference
        delete_code_success = self.code_driver.delete_ref(code_obj.commit_id)
        # Delete code object
        delete_code_obj_success = self.dal.code.delete(code_obj.id)

        return delete_code_success and delete_code_obj_success
