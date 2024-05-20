# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import copy
import operator
import typing

# ========================================
# Internal imports
# ========================================

from colibri.utils.enums_utils import (
                                Roles,
                                Units,
                               )

# ========================================
# Constants
# ========================================

from colibri.config.constants import UNIT_CONVERTER

# ========================================
# Variables
# ========================================

SelfVariable          = typing.TypeVar("SelfVariable", bound = "Variable")
SelfContainerVariable = typing.TypeVar("SelfContainerVariable", bound = "ContainerVariable ")

# ========================================
# Classes
# ========================================


class Variable:

    def __init__(self, name: str, value: typing.Any, role: Roles, unit: Units = Units.UNITLESS, description: str = "Sorry, no description yet.", linked_to: typing.List[SelfVariable] = None, model = None):
        self.name        = name
        self.value       = value
        self.role        = role
        self.unit        = unit
        self.description = description
        self.linked_to   = linked_to
        self.model       = model

    def convert(self, target_unit: Units) -> float:
        return UNIT_CONVERTER.convert(self.value, self.unit, target_unit)

    @property
    def value(self) -> typing.Any:
        return self._value

    @value.setter
    def value(self, value: typing.Any) -> None:
        if hasattr(self, "linked_to") and hasattr(self, "model"):
            if self.linked_to is not None:
                sizing_variable = getattr(self.model, self.name)
                for expandable_variable in sizing_variable.linked_to:
                    expandable_variable_name = expandable_variable.name
                    list_name                = expandable_variable.role.value
                    list_to_remove_from      = getattr(self.model, list_name)
                    for index in range(0, int(sizing_variable)):
                        attribute = getattr(self.model, f"{expandable_variable_name}_{index + 1}")
                        variable  = [variable for variable in list_to_remove_from if variable.name == attribute.name][0]
                        list_to_remove_from.remove(variable)
                        delattr(self.model, variable.name)
                for expandable_variable in sizing_variable.linked_to:
                    expandable_variable_name = expandable_variable.name
                    list_name                = expandable_variable.role.value
                    list_to_append_to        = getattr(self.model, list_name)
                    for index in range(0, int(value)):
                        expandable_variable.name = f"{expandable_variable_name}_{index + 1}"
                        variable = copy.deepcopy(expandable_variable)
                        list_to_append_to.append(variable)
                        setattr(self.model, variable.name, variable)
        self._value = value

    def __add__(self, val2):
        return self.value + val2

    __radd__ = __add__

    def __sub__(self, val2):
        return self.value - val2

    def __rsub__(self, val2):
        return val2 - self.value

    def __mul__(self, val2):
        if type(val2) == Variable: # why is this not required for + or / ???
            return self.value * val2.value
        else:
            return self.value * val2

    def __rmul__(self, val2):
        if type(val2) == Variable:
            return self.value * val2.value
        else:
            return self.value * val2

    #for now variables are scalar only, but this may change quickly if Anthony comes up with another smart idea
    # def __matmul__(self, val2):
    #     return self.value / val2

    def __truediv__(self, val2):
        return operator.truediv(self.value, val2)

    def __rtruediv__(self, val2):
        return operator.truediv(val2, self.value)

    def __floordiv__(self, val2):
        return operator.floordiv(self.value, val2)

    def __rfloordiv__(self, val2):
        return operator.floordiv(val2, self.value)

    def __mod__(self, val2):
        return self.value % val2

    def __rmod__(self, val2):
        return val2 % self.value

    def __divmod__(self, val2):
        return divmod(self.value, val2)

    def __rdivmod__(self, val2):
        return divmod(val2, self.value)

    def __pow__(self, val2):
        return pow(self.value, val2)

    def __rpow__(self, val2):
        return pow(val2, self.value)

    def __lshift__(self, val2):
        return self.value << val2

    def __rlshift__(self, val2):
        return val2 << self.value

    def __rshift__(self, val2):
        return self.value >> val2

    def __rrshift__(self, val2):
        return val2 >> self.value

    def __and__(self, val2):
        return self.value and val2

    def __rand__(self, val2):
        return val2 and self.value

    def __xor__(self, val2):
        return self.value or val2

    __rxor__ = __xor__

    def __or__(self, val2):
        return self.value or val2

    __ror__ = __or__

    def __neg__(self):
        return -self.value

    def __pos__(self):
        return self.value

    def __abs__(self):
        return abs(self.value)

    def __invert__(self):
        return ~self.value

    # rich comparison methods
    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return not (self.value == other)

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    # TODO: add
    #  - augmented assignment methods (__iadd__ et al)
    #  - ALL type Conversion methods (__int__ et al)

    def __int__(self):
        return int(self.value)

    def __float__(self, other):
        return float(self.value)

    def __index__(self):
        return int(self.value)

    # Required for numpy.exp(variable), but
    # create problems with self.zone_setpoint_list[self.heating_season == False] = self.zone_setpoint_cooling
    # if implemented as follows (_array__() takes 1 positional argument but 2 were given)
    #def __array__(self):
    #    return numpy.array(self.value)

    def __iter__(self):
        yield self.value

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
        string_representation = f"{self.__class__.__name__}({self.name}, {self.value}, {self.role}, {self.unit}, {self.description}, {self.linked_to})"
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


# Class to store Variable objects
class ContainerVariables:

    """Class to store Variable objects

    Attributes
    ----------

    Methods
    -------
    add(variable: Variable)
        Add a variable to the container (ContainerVariables)

    Notes
    -----
    None

    Examples
    --------
    >>> variables = ContainerVariables()
    >>> variables.add(Variable("1", 1.0).add(Variable("2", 2.0)
    >>> variables
    >>> 'ContainerVariables().add(Variable(name="1", value=1.0, unit=<Units.UNITLESS: "-">)).add(Variable(name="2", value=2.0, unit=<Units.UNITLESS: "-">))'
    """

    # Add a variable to the container (ContainerVariables)
    def add(self, condition: Variable) -> SelfContainerVariable:
        """Add a variable to the container (ContainerVariables)

        Parameters
        ----------

        Returns
        -------
        Self
            Return the instance itself

        Raises
        ------
        None

        Examples
        --------
        >>> variables = ContainerVariables()
        >>> variables.add(Variable("1", 1.0).add(Variable("2", 2.0)
        """
        setattr(self, condition.name, condition)
        return self

    # Return the ContainerVariables object's attributes (variables) in a list
    def to_list(self) -> list:
        """Return the ContainerVariables object's attributes (variables) in a list

        Parameters
        ----------

        Returns
        -------
        list
            List of ttributes (variables) in a list

        Raises
        ------
        None

        Examples
        --------
        >>> variables = ContainerVariables()
        >>> variables.add(Variable("1", 1.0)
        >>> variables.to_list()
        >>> [Variable(name='1', value=1.0, unit=<Units.UNITLESS: '-'>, description='Sorry, no description yet.']
        """
        return [attribute for attribute in self.__dict__.values()]

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
        join_adds             = f".".join([f"add({condition})" for condition in self.__dict__.values()])
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
