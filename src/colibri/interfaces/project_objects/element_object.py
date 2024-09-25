"""
ElementObject class, which is the parent class of each element object
(project object associated to a boundary object) for the `colibri` package.
"""

from __future__ import annotations

from typing import Any, Dict, List

from colibri.config.constants import SLOTS
from colibri.mixins import ClassMixin, MetaFieldMixin


class ElementObject(ClassMixin, MetaFieldMixin):
    """Class representing an element object, that is,
    a project object associated to a boundary object."""

    def __init__(self, **kwargs):
        """Initialize a new ElementObject instance."""
        super().__init__()
        for attribute_name, attribute_value in kwargs.items():
            setattr(self, attribute_name, attribute_value)

    @classmethod
    def create_instance(
        cls, class_name: str, fields: Dict[str, Any]
    ) -> ElementObject:
        """Create an instance of a class (given its name), which will inherit
        from the ElementObject class

        Parameters
        ----------
        fields: Dict[str, Any]
            Fields to be set to the new object

        Returns
        -------
        ElementObject
            Instance of a new class (given its name) inheriting from
            the ElementObject class

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        attribute_names: Dict[str, List[str]] = {
            SLOTS: [field for field in fields]
        }
        new_class: type = type(
            class_name.capitalize(), (ElementObject,), attribute_names
        )
        new_instance: ElementObject = new_class(**fields)
        return new_instance


if __name__ == "__main__":
    from colibri.config.constants import LOGGER

    element_object: ElementObject = ElementObject()
    LOGGER.debug(f"{element_object = }")
    other_object: ElementObject = ElementObject.create_instance(
        class_name="layer", fields={"x": 2, "y": 3}
    )
    LOGGER.debug(f"{other_object = }")
    LOGGER.debug(f"{other_object.x = }")
