"""
This module is the core of all models.
"""

import abc
import copy
from typing import Any, List, Optional, Protocol, Union

from colibri.core.variables.inputs import Inputs
from colibri.core.variables.outputs import Outputs
from colibri.core.variables.parameters import Parameters
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import Roles


class ModelUsingMetaModel(Protocol):
    inputs: list
    outputs: list
    parameters: list

    def initialize(self) -> None: ...

    def check_units(self) -> None: ...

    def run(self, time_step: int = 0, n_iteration: int = 0) -> None: ...

    def iteration_done(self, time_step: int = 0) -> None: ...

    def timestep_done(self, time_step: int = 0) -> None: ...

    def simulation_done(self, time_step: int = 0) -> None: ...

    def converged(self, time_step: int = 0, n_iteration: int = 0) -> bool: ...

    def get_variable(self, name: str) -> Variable: ...

    def get_input(self, name: str) -> Variable: ...

    def get_output(self, name: str) -> Variable: ...

    def get_parameter(self, name: str) -> Variable: ...

    def save_time_step(self, time_step: int) -> None: ...

    @staticmethod
    def model_factory(class_name, instance_name): ...


class MetaModel(abc.ABCMeta):
    """Metaclass for defining Abstract Base Class (ABC) for the class Model."""

    def __call__(cls, *args, **kwargs) -> ModelUsingMetaModel:
        # Create an instance (object) of an arbitrary class
        instance: ModelUsingMetaModel = type.__call__(cls, *args, **kwargs)
        # Assign similar instance variables to all objects of a class using
        # the MetaModel
        cls._assign_same_instance_variables(instance)
        # TODO: Verify that the inputs/outputs/parameters do not contain
        # wrong type (paramter inside inputs)
        # Insure that attributes of the instance (object) are grouped inside
        # the
        cls._add_attributes_to_internal_lists(instance)
        #
        instance._expand_variables()
        #
        for variable in instance.inputs + instance.outputs + instance.parameters:
            variable.model = instance
        return instance

    @staticmethod
    def _assign_same_instance_variables(instance: ModelUsingMetaModel) -> None:
        """Assign similar instance variables to all objects of a class using
           the MetaModel if they are not specified by the class __init__ method

        Parameters
        ----------
        instance : object
            Instance of a class

        Returns
        -------
        None

        Raises
        ------
        None
        """
        # Define if the instance of the class has those types of variables
        has_inputs: bool = hasattr(instance, Roles.INPUTS.value)
        has_outputs: bool = hasattr(instance, Roles.OUTPUTS.value)
        has_parameters: bool = hasattr(instance, Roles.PARAMETERS.value)
        # If not, create them
        if has_inputs is False:
            instance.inputs = list()
        if has_outputs is False:
            instance.outputs = list()
        if has_parameters is False:
            instance.parameters = list()

    @staticmethod
    def _add_attributes_to_internal_lists(instance) -> None:
        attributes = [
            attribute
            for _, attribute in instance.__dict__.items()
            if isinstance(attribute, Variable)
        ]
        variable_names = [
            variable.name
            for variable in instance.inputs + instance.outputs + instance.parameters
        ]
        for attribute in attributes:
            if (attribute.role == Roles.INPUTS) and (
                attribute.name not in variable_names
            ):
                instance.inputs.append(attribute)
            elif (attribute.role == Roles.INPUTS) and (
                attribute.name in variable_names
            ):
                index = [
                    index
                    for index, variable in enumerate(instance.inputs)
                    if variable.name == attribute.name
                ][0]
                value = instance.inputs[index].value
                attribute.value = value
                instance.inputs[index] = attribute
            elif (attribute.role == Roles.OUTPUTS) and (
                attribute.name not in variable_names
            ):
                instance.outputs.append(attribute)
            elif (attribute.role == Roles.OUTPUTS) and (
                attribute.name in variable_names
            ):
                index = [
                    index
                    for index, variable in enumerate(instance.outputs)
                    if variable.name == attribute.name
                ][0]
                value = instance.outputs[index].value
                attribute.value = value
                instance.outputs[index] = attribute
            elif (attribute.role == Roles.PARAMETERS) and (
                attribute.name not in variable_names
            ):
                instance.parameters.append(attribute)
            elif (attribute.role == Roles.PARAMETERS) and (
                attribute.name in variable_names
            ):
                index = [
                    index
                    for index, variable in enumerate(instance.parameters)
                    if variable.name == attribute.name
                ][0]
                value = instance.parameters[index].value
                attribute.value = value
                instance.parameters[index] = attribute


class Model(metaclass=MetaModel):
    def __init__(
        self,
        name: str,
        inputs: Inputs = None,
        outputs: Outputs = None,
        parameters: Parameters = None,
    ):
        self.name = name
        self.project = None
        self.inputs = [] if inputs is None else inputs.to_list()
        self.outputs = [] if outputs is None else outputs.to_list()
        self.parameters = [] if parameters is None else parameters.to_list()

    @abc.abstractmethod
    def initialize(self) -> None:
        ...

    # TODO: check_units could/should be the same for all models, not an abstractmethod
    @abc.abstractmethod
    def check_units(self) -> None:
        ...

    @abc.abstractmethod
    def run(self, time_step: int = 0, n_iteration: int = 0) -> None:
        ...

    @abc.abstractmethod
    def iteration_done(self, time_step: int = 0) -> None:
        ...

    @abc.abstractmethod
    def timestep_done(self, time_step: int = 0) -> None:
        ...

    @abc.abstractmethod
    def simulation_done(self, time_step: int = 0) -> None:
        ...

    def converged(self, time_step: int = 0, n_iteration: int = 0) -> bool:
        return None

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

    def _expand_variables(self) -> None:
        variables = self.inputs + self.parameters
        for variable in variables:
            if variable.linked_to:
                for expandable_variable in variable.linked_to:
                    list_name = expandable_variable.role.value
                    expandable_variable_name = expandable_variable.name
                    for index in range(0, int(variable)):
                        new_variable = copy.deepcopy(expandable_variable)
                        new_variable.name = f"{expandable_variable_name}_{index + 1}"
                        list_to_append_to = getattr(self, list_name)
                        if any(
                            [
                                variable
                                for variable in list_to_append_to
                                if variable.name == new_variable.name
                            ]
                        ):
                            variable_index = [
                                index
                                for index, variable in enumerate(list_to_append_to)
                                if variable.name == new_variable.name
                            ][0]
                            list_to_append_to[variable_index] = new_variable
                        else:
                            list_to_append_to.append(new_variable)

    def save_time_step(self, time_step: int) -> None:
        for variable in self.outputs:
            # TODO: Check if we need this: if isinstance(value.value, numbers.Number): Yes, we do, but it's weird
            getattr(self, variable.name + "_series")[time_step] = variable.value

    # allow to create models for a list of modules (["models.emitters.electric_emitter"])
    # this list can be extended each time a new system model is authored
    # only systems from this list will be created automatically
    @staticmethod
    def model_factory(class_name, instance_name):
        import importlib

        for module_name in [
            "colibri.models.emitters.electric_emitter",
            "colibri.models.emitters.hydro_emitter",
        ]:  # TODO: récupérer de manière automatique ? Ou à un autre endroit ?
            module = importlib.import_module(module_name)
            if not module is None and hasattr(module, class_name):
                cls = getattr(module, class_name)
                return cls(instance_name)

        return None

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
