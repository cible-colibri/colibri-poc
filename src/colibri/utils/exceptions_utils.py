"""
Exceptions for the `colibri` package.
"""

from colibri.utils.enums_utils import ErrorMessages


class ColibriException(Exception):
    """Base class for COLIBRI exceptions."""

    def __init__(self, error_message: str = None):
        error_message: str = (
            self.description if error_message is None else error_message
        )
        super().__init__(error_message)


class AttachmentError(ColibriException):
    """Exception when an attachment is not valid."""

    description: str = ErrorMessages.ATTACHMENT_ERROR.value


class ColibriModuleNotFoundError(ColibriException):
    """Exception when COLIBRI module is not found."""

    description: str = ErrorMessages.COLIBRI_MODULE_NOT_FOUND_ERROR.value


class LinkError(ColibriException):
    """Exception when there is a link error
    (e.g., an input variable is linked more than once."""

    description: str = ErrorMessages.LINK_ERROR.value


class UnauthorizedColibriModule(ColibriException):
    """Exception when COLIBRI module is not authorized (wrong interface)."""

    description: str = ErrorMessages.UNAUTHORIZED_COLIBRI_MODULE_ERROR.value


class UnitError(ColibriException):
    """Exception when there is a unit error."""

    description: str = ErrorMessages.UNIT_ERROR.value


class UserInputError(ColibriException):
    """Exception when there is a user input error."""

    description: str = ErrorMessages.USER_INPUT_ERROR.value
