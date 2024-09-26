"""
Variable class that represents any simulation variable.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from colibri.utils.colibri_utils import Attachment
from colibri.utils.data_utils import (
    turn_format_to_string,
    turn_max_min_to_string,
)
from colibri.utils.enums_utils import (
    Roles,
    Units,
)

if TYPE_CHECKING:
    from colibri.interfaces.model import Model


@dataclass
class Field:
    """Class representing a simulation field, that is,
    a simulation variable (either an input or an output) or a parameter.


    Attributes
    ----------
    name : str
        Name of the field
    default_value : Any
        Default value of the field
    unit : Units
        Unit of the field
    description : str
        Description of the field
    format : Any
        Format of the field
    min : Any
        Min value of the field
    max : Any
        Max value of the field
    choices : Optional[List[str]] = None
        Choices when the field is associated with a list of possible values
    attached_to : Optional[Attachment] = None
        Specify which project object the field is attached to
    role : Optional[Roles] = None
        Role of the field
    """

    name: str
    default_value: Any
    unit: Units
    description: str
    format: Any
    min: Any
    max: Any
    choices: Optional[List[str]] = None
    attached_to: Optional[Attachment] = None
    role: Optional[Roles] = None

    def to_scheme(self) -> Dict[str, Any]:
        """Return the variable's scheme

        Returns
        -------
        Dict[str, Any]
            Variable's scheme

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        format_representation: str = turn_format_to_string(
            field_format=self.format,
        )
        max_representation: Any = turn_max_min_to_string(max_or_min=self.max)
        min_representation: Any = turn_max_min_to_string(max_or_min=self.min)
        choices: Union[List[Any], None] = (
            [enum.value for enum in self.choices]
            if inspect.isclass(self.choices) and issubclass(self.choices, Enum)
            else self.choices
        )
        return {
            "description": self.description,
            "format": format_representation,
            "min": min_representation,
            "max": max_representation,
            "unit": self.unit.value,
            "choices": choices,
            "default": self.default_value,
            "attached_to": self.attached_to,
            "required": self.required,
        }


@dataclass
class Parameter(Field):
    """Class representing a parameter (from the project data).

    Attributes
    ----------
    name : str
        Name of the parameter
    default_value : Any
        Default value of the parameter
    unit : Units
        Unit of the parameter
    description : str
        Description of the parameter
    format : Any
        Format of the parameter
    min : Any
        Min value of the parameter
    max : Any
        Max value of the parameter
    choices : Optional[List[str]] = None
        Choices when the parameter is associated with a list of possible values
    attached_to : Optional[Attachment] = None
        Specify which project object the parameter is attached to
    role : Optional[Roles] = None
        Role of the parameter
    required : List[Parameter] = None
        Required parameters that a parameter might need
    """

    required: Optional[List[Parameter]] = None


@dataclass
class SimulationVariable(Field):
    """Class representing a simulation variable (either an input or an output).

    Attributes
    ----------
    name : str
        Name of the simulation variable
    default_value : Any
        Default value of the simulation variable
    unit : Units
        Unit of the simulation variable
    description : str
        Description of the simulation variable
    format : Any
        Format of the simulation variable
    min : Any
        Min value of the simulation variable
    max : Any
        Max value of the simulation variable
    attached_to : Optional[Attachment] = None
        Specify which project object the simulation variable is attached to
    role : Optional[Roles] = None
        Role of the simulation variable
    use_post_initialization: bool = False
        Update value with that of another model after post-initialization
    """

    linked_to: List[SimulationVariable] = field(default_factory=list)
    model: Optional[Model] = None
    check_convergence: bool = False
    convergence_tolerance: float = 0.1
    maximum_number_of_iterations: int = 10
    required: Optional[List[Parameter]] = None
    use_post_initialization: bool = False
