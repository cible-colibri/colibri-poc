"""
ClassMixin class, which is a mixin for providing functionalities
related to Python classes for the `colibri` package.
"""

from typing import Any, Dict, List

from colibri.config.constants import SLOTS


class ClassMixin:
    """Class providing functionalities related to Python classes."""

    def __str__(self) -> str:
        """Return the string representation of the object

        Returns
        -------
        string_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        instance_variables: List[str] = []
        variables: Dict[str, Any] = {
            name: value
            for name, value in self.__dict__.items()
            if not name.startswith("_")
        }
        if (not variables) and (hasattr(self, SLOTS)):
            variables = {name: getattr(self, name) for name in self.__slots__}
        if (not variables) and (not hasattr(self, SLOTS)):
            variables = dict()
        for name, value in variables.items():
            if isinstance(value, str):
                instance_variable = "{name}='{value}'".format(
                    name=name, value=value
                )
            else:
                instance_variable = "{name}={value}".format(
                    name=name, value=value
                )
            instance_variables.append(instance_variable)
        formatted_instance_variables: str = ", ".join(instance_variables)
        string_representation = (
            f"{self.__class__.__name__}({formatted_instance_variables})"
        )
        return string_representation

    def __repr__(self) -> str:
        """Return the object representation as a string


        Returns
        -------
        object_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        object_representation = self.__str__()
        return object_representation
