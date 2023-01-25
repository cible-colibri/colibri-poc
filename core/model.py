# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import abc

# ========================================
# Internal imports
# ========================================

from core.variable_list import VariableList

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class MetaModel(abc.ABCMeta):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        cls._transform_variables_in_attributes(obj)
        return obj

    @staticmethod
    def _transform_variables_in_attributes(obj):
        for input in obj.inputs:
            setattr(obj, input.name, input)


class Model(metaclass =  MetaModel):

    def __init__(self, name: str):
        self.name    = name
        self.inputs  = []
        self.outputs = []

    @staticmethod
    def get_variable(name: str, variables: list) -> object:
        for v in variables:
            if v.name == name:
                return v


    def get_output(self, name: str):
        return self.get_variable(name, self.outputs)

    def get_input(self, name: str):
        return self.get_variable(name, self.inputs)

    def set(self, variable_name: str, value: float):
        # set value and expand vectors
        pass

    def get(self, variable_name: str):
        # set value and expand vectors
        v = [v for v in self.inputs + self.outputs if v.name == variable_name]
        if len(v) == 1:
            return v[0]
        else:
            return None

    @abc.abstractmethod
    def run(self):
        pass

    def initialize(self):
        pass

    def iteration_done(self):
        pass

    def simulation_done(self):
        pass

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
        string_representation = f"{self.__class__.__name__}('{self.name}')"
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
