# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from core.variable import Variable

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

# TODO: Make Conditions and Parameters extend from a parent class (maybe ContainerVariables) to avoid repetitions
class Parameters:

    def add(self, parameter: Variable):
        setattr(self, parameter.name, parameter)
        return self

    # Return the string representation of the object
    def __str__(self):
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
        join_adds             = f".".join([f"add({parameter})" for parameter in self.__dict__.values()])
        string_representation = f"{self.__class__.__name__}().{join_adds}"
        return string_representation

    # Return the object representation as a string
    def __repr__(self):
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
