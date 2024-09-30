"""
Helper classes or functions for the `colibri` package.
"""

from dataclasses import dataclass
from typing import Any, Optional

from colibri.utils.data_utils import turn_format_to_string
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
)
from colibri.utils.exceptions_utils import AttachmentError


@dataclass
class Attachment:
    """Class representing the attachment to a COLIBRI's project object.

    Attributes
    ----------
    category : ColibriProjectObjects
        Category of the colibri object to be attached to
    class_name : Optional[str] = None
        Name of the class when the colibri object is not a direct class
    from_archetype : bool = False
        Specify if the field attached should be taken from an archetype
    from_element_object : Optional[str] = None
        Name of the element object the field is attached to
    description : Optional[str]
        Description of the object being attached
    format : Optional[Any]
        Format of the object being attached

    Methods
    -------
    __post_init__()
        Perform additional initialization/validation of the new Attachment instance.
    """

    category: ColibriProjectObjects
    class_name: Optional[str] = None
    from_archetype: bool = False
    from_element_object: Optional[str] = None
    description: Optional[str] = None
    format: Optional[str] = None
    default_value: Optional[Any] = None

    def __post_init__(self) -> None:
        """Additional initialization/validation of the new Attachment instance."""
        if (self.category is ColibriProjectObjects.BOUNDARY_OBJECT) and (
            self.class_name is None
        ):
            raise AttachmentError("Boundary object must have a class name.")
        # TODO: Check rules with archetypes
        # if (self.from_archetype is True) and (
        #     self.category is not ColibriProjectObjects.BOUNDARY_OBJECT
        # ):
        #     raise AttachmentError(
        #         "Only boundary object's parameters "
        #         "must come from an archetype."
        #     )
        if self.class_name is not None:
            self.class_name = self.class_name.capitalize()
        if self.format is not None:
            self.format = turn_format_to_string(field_format=self.format)
