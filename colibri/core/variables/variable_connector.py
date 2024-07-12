# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import typing

# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================

SelfVariableConnector = typing.TypeVar("SelfVariableConnector", bound = "VariableConnector")

# ========================================
# Classes
# ========================================


class VariableConnector:

    def __init__(self):
        self.connections = []

    def add(self, from_variable_name: str, to_variable_name: str) -> SelfVariableConnector:
        self.connections.append((from_variable_name, to_variable_name))
        return self

    # Return the string representation of the object
    def __str__(self) -> str:
        """Return the string representation of the object

        Parameters
        ----------

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
        join_adds             = f".".join([f"add({condition})" for condition in self.__dict__s()])
        string_representation = f"{self.__class__.__name__}().{join_adds}"
        return string_representation

    # Return the object representation as a string
    def __repr__(self) -> str:
        """Return the object representation as a string

        Parameters
        ----------

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

# ========================================
# Functions
# ========================================
