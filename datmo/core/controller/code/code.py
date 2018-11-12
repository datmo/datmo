from datmo.core.util.i18n import get as __
from datmo.core.controller.base import BaseController
from datmo.core.entity.code import Code
from datmo.core.util.exceptions import PathDoesNotExist, EnvironmentInitFailed, ArgumentError, CodeDoesNotExist


class CodeController(BaseController):
    """CodeController inherits from BaseController and manages business logic related to the
    code.

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

    def current_code(self):
        """Get the current code object

        Returns
        -------
        Code
            an object representing the current code reference state

        Raises
        ------
        UnstagedChanges
            if there are unstaged changes error out because no current code
        """
        self.check_unstaged_changes()
        current_commit_id = self.code_driver.current_hash()
        # Return the code object with this hash id
        return self.create(commit_id=current_commit_id)

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
        # Required args for Code entity
        required_args = ["driver_type", "commit_id"]
        for required_arg in required_args:
            # Handle Id if provided or not
            if required_arg == "driver_type":
                create_dict[required_arg] = self.code_driver.type
            elif required_arg == "commit_id":
                create_dict[required_arg] = \
                    self.code_driver.create_ref(commit_id=commit_id)
                # If code object with commit id exists, return it
                results = self.dal.code.query({
                    "commit_id": create_dict[required_arg],
                    "model_id": self.model.id
                })
                if results: return results[0]
            else:
                raise NotImplementedError()

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

    def exists(self, code_id=None, code_commit_id=None):
        """Returns a boolean if the code exists

        Parameters
        ----------
        code_id : str
            code id to check for
        code_commit_id : str
            unique commit id for the code

        Returns
        -------
        bool
            True if exists else False
        """
        if not self.is_initialized:
            return False
        if code_id:
            code_objs = self.dal.code.query({"id": code_id})
        elif code_commit_id:
            code_objs = self.dal.code.query({"commit_id": code_commit_id})
        else:
            raise ArgumentError()
        if code_objs:
            return True
        return False

    def check_unstaged_changes(self):
        """Checks if there exists any unstaged changes for the code in the project.

        Returns
        -------
        bool
            False if it's already staged else error

        Raises
        ------
        CodeNotInitialized
            error if not initialized (must initialize first)
        UnstagedChanges
            error if not there exists unstaged changes in code
        """
        return self.code_driver.check_unstaged_changes()

    def checkout(self, code_id):
        """Checkout to specific code id

        Parameters
        ----------
        code_id : str
            code id to checkout to

        Returns
        -------
        bool
            True if success

        Raises
        ------
        CodeDoesNotExist
            if code id does not exist
        CodeNotInitialized
            error if not initialized (must initialize first)
        UnstagedChanges
            error if not there exists unstaged changes in code

        """
        if not self.exists(code_id):
            raise CodeDoesNotExist(
                __("error", "controller.code.checkout", code_id))
        code_obj = self.dal.code.get_by_id(code_id)
        return self.code_driver.checkout_ref(code_obj.commit_id)
