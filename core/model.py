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
        cls._transform_variables_to_attributes(obj)
        return obj

    @staticmethod
    def _transform_variables_to_attributes(obj):
        for variable in obj.inputs + obj.outputs:
            if type(variable) != VariableList:
                setattr(obj, variable.name, variable.value)
        for variable in obj.outputs:
            if type(variable) != VariableList:
                setattr(obj, variable.name + '_series', [])


class Model(metaclass =  MetaModel):

    def __init__(self, name: str):
        self.name    = name
        self.inputs  = []
        self.outputs = []
        self.files   = []
        self.project = None

    @staticmethod
    def get_variable(name: str, variables: list) -> object:
        for v in variables:
            if v.name == name:
                return v


    def get_output(self, name: str):
        return self.get_variable(name, self.outputs)

    def get_input(self, name: str):
        return self.get_variable(name, self.inputs)

    def get_file(self, name: str) -> object:
        for f in self.files:
            if f.name == name:
                return f

    def set(self, variable_name: str, value: float):
        # TODO : set value and expand vectors
        pass

    def get(self, variable_name: str):
        # set value and expand vectors
        v = [v for v in self.inputs + self.outputs if v.name == variable_name]
        if len(v) == 1:
            return v[0]
        else:
            return None

    def save_time_step(self, time_step):
        for variable in self.outputs:
            if type(variable) != VariableList:
                getattr(self, variable.name + '_series').append(getattr(self, variable.name))

    @abc.abstractmethod
    def run(self, time_step=0):
        pass

    def initialize(self):
        pass

    def iteration_done(self, time_step=0):
        pass

    def timestep_done(self, time_step=0):
        pass

    def simulation_done(self, time_step=0):
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
