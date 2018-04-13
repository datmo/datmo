from datmo.util.i18n import get as _
from datmo.controller.base import BaseController
from datmo.util.exceptions import RequiredArgumentMissing, \
    DoesNotExistException


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
    def __init__(self, home, dal_driver=None):
        super(CodeController, self).__init__(home, dal_driver)

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

        ## Required args
        required_args = ["driver_type", "commit_id"]
        traversed_args = []
        for required_arg in required_args:
            # Handle Id if provided or not
            if required_arg == "commit_id":
                create_dict[required_arg] = commit_id if commit_id else \
                    self.code_driver.create_code()
                traversed_args.append(required_arg)
            elif required_arg == "driver_type":
                create_dict[required_arg] = self.code_driver.type
                traversed_args.append(required_arg)

        # Error if required values not present
        if not traversed_args == required_args:
            raise RequiredArgumentMissing(_("error",
                                            "controller.code.create"))

        # Create code and return
        return self.dal.code.create(create_dict)

    def list(self):
        # TODO: Add time filters
        return self.dal.code.query({})

    def delete(self, id):
        """Delete all traces of Code object

        Parameters
        ----------
        id : str
            code object id to remove

        Returns
        -------
        bool
            returns True if success else False

        Raises
        ------
        DoesNotExistException
            if the specified Code does not exist.
        """
        code_obj = self.dal.code.get_by_id(id)
        if not code_obj:
            raise DoesNotExistException(_("error",
                                          "controller.code.delete",
                                          id))
        # Remove code reference
        delete_code_success = self.code_driver.delete_code(code_obj.commit_id)
        # Delete code object
        delete_code_obj_success = self.dal.code.delete(code_obj.id)

        return delete_code_success and delete_code_obj_success