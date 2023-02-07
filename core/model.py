# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import abc
import copy
import numbers

# ========================================
# Internal imports
# ========================================

from core.inputs       import Inputs
from core.outputs      import Outputs
from core.parameters   import Parameters
from core.variable     import Variable
from utils.enums_utils import Roles

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

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name       = name
        self.project    = None
        self.inputs     = [] if inputs is None else inputs.to_list()
        self.outputs    = [] if outputs is None else outputs.to_list()
        self.parameters = [] if parameters is None else parameters.to_list()
        self._define_variables()
        self._add_attributes_to_internal_lists()
        self._expand_variables()

    def _define_variables(self) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError("Please, implement me...")

    # TODO: check_units could/should be the same for all models, not an abstractmethod
    @abc.abstractmethod
    def check_units(self) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def run(self, time_step: int = 0) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def iteration_done(self, time_step: int = 0) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def timestep_done(self, time_step: int = 0) -> None:
        raise NotImplementedError("Please, implement me...")

    @abc.abstractmethod
    def simulation_done(self, time_step: int = 0) -> None:
        raise NotImplementedError("Please, implement me...")

    def get_variable(self, name: str) -> Variable:
        variables = self.inputs + self.outputs + self.parameters
        return self._get_variable(name, variables)

    def get_input(self, name: str) -> Variable:
        return self._get_variable(name, self.inputs)

    def get_output(self, name: str) -> Variable:
        return self._get_variable(name, self.outputs)

    def get_parameter(self, name: str) -> Variable:
        return self._get_variable(name, self.parameters)

    @staticmethod
    def _get_variable(name: str, variables: list) -> Variable:
        for variable in variables:
            if variable.name == name:
                return variable
        return None

    def _add_attributes_to_internal_lists(self) -> None:
        attributes     = [attribute for _, attribute in self.__dict__.items() if isinstance(attribute, Variable)]
        variable_names = [variable.name for variable in self.inputs + self.outputs + self.parameters]
        for attribute in attributes:
            if (attribute.role == Roles.INPUTS) and (attribute.name not in variable_names):
                self.inputs.append(attribute)
            elif (attribute.role == Roles.INPUTS) and (attribute.name in variable_names):
                index              = [index for index, variable in enumerate(self.inputs) if variable.name == attribute.name][0]
                value              = self.inputs[index].value
                attribute.value    = value
                self.inputs[index] = attribute
            elif (attribute.role == Roles.OUTPUTS) and (attribute.name not in variable_names):
                self.outputs.append(attribute)
            elif (attribute.role == Roles.OUTPUTS) and (attribute.name in variable_names):
                index              = [index for index, variable in enumerate(self.outputs) if variable.name == attribute.name][0]
                value              = self.outputs[index].value
                attribute.value    = value
                self.outputs[index] = attribute
            elif (attribute.role == Roles.PARAMETERS) and (attribute.name not in variable_names):
                self.parameters.append(attribute)
            elif (attribute.role == Roles.PARAMETERS) and (attribute.name in variable_names):
                index              = [index for index, variable in enumerate(self.parameters) if variable.name == attribute.name][0]
                value              = self.parameters[index].value
                attribute.value    = value
                self.parameters[index] = attribute

    def _expand_variables(self) -> None:
        variables = self.inputs + self.parameters
        for variable in variables:
            if variable.linked_to:
                for expandable_variable in variable.linked_to:
                    list_name                = expandable_variable.role.value
                    expandable_variable_name = expandable_variable.name
                    for index in range(0, int(variable.value)):
                        new_variable      = copy.deepcopy(expandable_variable)
                        new_variable.name = f"{expandable_variable_name}_{index + 1}"
                        list_to_append_to = getattr(self, list_name)
                        if any([variable for variable in list_to_append_to if variable.name == new_variable.name]):
                            variable_index = [index for index, variable in enumerate(list_to_append_to) if variable.name == new_variable.name][0]
                            list_to_append_to[variable_index] = new_variable
                        else:
                            list_to_append_to.append(new_variable)

    def save_time_step(self, time_step: int) -> None:
        for variable in self.outputs:
            # TODO: Check if we need this: if isinstance(value.value, numbers.Number): Yes, we do, but it's weird
            if isinstance(variable.value, numbers.Number):
                getattr(self, variable.name + "_series")[time_step] = variable.value

    def __setattr__(self, name, value):
        if hasattr(self, name):
            variable = getattr(self, name)
            if hasattr(variable, "value"):
                if isinstance(value, Variable):
                    value = value.value
                variable.value = value
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
        string_representation = f"{self.__class__.__name__}(name = '{self.name}')"
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
