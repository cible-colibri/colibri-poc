# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import abc
import copy
import numbers
import typing

# ========================================
# Internal imports
# ========================================

from core.conditions import Conditions
from core.inputs     import Inputs
from core.outputs    import Outputs
from core.parameters import Parameters
from core.variable   import Variable

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class Model(abc.ABC):

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None, conditions: Conditions = None):
        self.name       = name
        self.conditions = conditions.to_list() if conditions is not None else self._define_conditions()
        self.inputs     = inputs.to_list() if inputs is not None else self._define_inputs()
        self.outputs    = outputs.to_list() if outputs is not None else self._define_outputs()
        self.parameters = parameters.to_list() if parameters is not None else self._define_parameters()
        self.project    = None
        self._expand_variables()
        self._transform_variables_to_attributes()
        self._set_conditions()

    @abc.abstractmethod
    def _define_inputs(self) -> list:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def _define_outputs(self) -> list:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def _define_conditions(self) -> list:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def _define_parameters(self) -> list:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def check_units(self) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def run(self, time_step: int = 0) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def iteration_done(self, time_step: int = 0):
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def timestep_done(self, time_step: int = 0):
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def simulation_done(self, time_step: int = 0):
        raise NotImplementedError("Please, implement me...")

    def get_variable(self, name: str) -> object:
        variables = self.inputs + self.outputs + self.parameters
        return self._get_variable(name, variables)

    def get_input(self, name: str):
        return self._get_variable(name, self.inputs)

    def get_output(self, name: str):
        return self._get_variable(name, self.outputs)

    def get_parameter(self, name: str):
        return self._get_variable(name, self.parameters)

    @staticmethod
    def _get_variable(name: str, variables: list) -> object:
        for variable in variables:
            if variable.name == name:
                return variable
        return None

    def _transform_variables_to_attributes(self) -> None:
        for variable in self.inputs + self.outputs + self.parameters:
            setattr(self, variable.name, variable)

    def _set_conditions(self) -> None:
        for variable in self.conditions:
            setattr(self, variable.name, variable)

    def _expand_variables(self) -> None:
        inputs = copy.deepcopy(self.inputs)
        for variable in inputs:
            if variable.linked_to:
                for list_name, expandable_variable in variable.linked_to:
                    expandable_variable_name = expandable_variable.name
                    for index in range(0, int(variable.value)):
                        expandable_variable.name = f"{expandable_variable_name}_{index + 1}"
                        list_to_append_to        = getattr(self, list_name)
                        list_to_append_to.append(copy.deepcopy(expandable_variable))

    def save_time_step(self, time_step: int):
        for variable in self.outputs:
            # TODO: Check if we need this: if isinstance(value.value, numbers.Number): Yes, we do, but it's weird
            if isinstance(variable.value, numbers.Number):
                getattr(self, variable.name + "_series")[time_step] = variable.value

    def __setattr__(self, name, value):
        if hasattr(self, name):
            v = getattr(self, name)
            if hasattr(v, 'value'):
                if type(value) == Variable:
                    value = value.value
                v.value = value
            else:
                self.__dict__[name] = value
        else:
            self.__dict__[name] = value

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
        string_representation = f"{self.__class__.__name__}('{self.name}')"
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
