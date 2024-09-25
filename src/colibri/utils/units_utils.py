"""
Helper classes orr functions for units.
"""

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any, Dict, List, Union

from colibri.config import data
from colibri.utils.enums_utils import Units
from colibri.utils.exceptions_utils import UnitError


class SingletonMeta(type):
    """Metaclass that ensures only one instance of a class is created."""

    _instances: Dict[type, Any] = dict()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Called when an instance of the class is created.
        If an instance of the class already exists, it returns that instance.
        Otherwise, it creates a new instance and stores it.

        Parameters
        ----------
        *args : Any
            Positional arguments for the class constructor
        **kwargs : Any
            Keyword arguments for the class constructor

        Returns
        -------
        Any
            The singleton instance of the class

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # Check if the instance of the class already exists
        if cls not in cls._instances:
            # Create a new instance and store it
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class Unit:
    """Class representing a unit.

    Attributes
    ----------
    name : str
        Name of the unit
    description : str
        Description of the unit
    addition_factor : float
        Addition factor of the unit
    multiplication_factor : float
        Multiplication factor of the unit
    si_code : str
        SI code of the unit
    """

    name: str
    description: str
    addition_factor: float
    multiplication_factor: float
    si_code: str


@dataclass
class Dimension:
    """Class representing a unit dimension.

    Attributes
    ----------
    name : str
        Name of the dimension
    definition : str
        Definition of the dimension
    base_unit : Union[Dict[str, Any], Unit]
        Base unit of the dimension
    equivalent_units = Union[List[Dict[str, Any]], List[Unit]]
        Equivalent units of the dimension

    Methods
    -------
    __post_init__()
        Perform additional initialization/validation of the new Dimension instance.
    """

    name: str
    definition: str
    base_unit: Union[Dict[str, Any], Unit]
    equivalent_units: Union[List[Dict[str, Any]], List[Unit]]

    def __post_init__(self) -> None:
        """Additional initialization/validation of the new Dimension instance."""
        if isinstance(self.base_unit, dict):
            self.base_unit = Unit(**self.base_unit)
        if self.equivalent_units and (
            isinstance(self.equivalent_units[0], dict)
        ):
            temporary_equivalent_units = self.equivalent_units.copy()
            self.equivalent_units = [
                Unit(**equivalent_unit)
                for equivalent_unit in temporary_equivalent_units
            ]


class UnitConverter(metaclass=SingletonMeta):
    """Class representing a unit converter.

    Attributes
    ----------
    dimensions : Union[List[Dict[str, Any]], List[Dimension]
        Dimensions handled by the unit converter.

    Methods
    -------
    __post_init__()
        Perform additional initialization/validation of the new Dimension instance.
    """

    def __init__(self, dimensions: List[Dict[str, Any]]) -> None:
        """Initialize a new UnitConverter instance."""
        self.dimensions = []
        for dimension in dimensions:
            if isinstance(dimension, dict) is True:
                dimension: Dimension = Dimension(**dimension)
            self.dimensions.append(dimension)

    def get_unit(self, unit: Units):
        for dimension in self.dimensions:
            if dimension.base_unit.name == unit.value:
                return dimension.base_unit
            else:
                for equivalent_unit in dimension.equivalent_units:
                    if equivalent_unit.name == unit.value:
                        return equivalent_unit
        return None

    def convert(self, value: float, unit_from: Units, unit_to: Units) -> float:
        """Convert the value from one unit to another

        Parameters
        ----------
        value : float
            Value to be converted
        unit_from : Units
            Initial unit
        unit_to : Units
            Final unit

        Returns
        -------
        float
            Converted value

        Raises
        ------
        UnitError
            Raise an error if one of the unit cannot be found

        Examples
        --------
        >>> None
        """
        unit_1: Unit = self.get_unit(unit_from)
        if not unit_1:
            raise UnitError(f"Unit {unit_from.value} not found")
        unit_2: Unit = self.get_unit(unit_to)
        if not unit_2:
            raise UnitError(f"Unit {unit_to.value} not found")
        return (
            (value - float(unit_1.addition_factor))
            / float(unit_1.multiplication_factor)
        ) * float(unit_2.multiplication_factor) + float(unit_2.addition_factor)

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
        string_representation = f"{self.__class__.__name__}({self.dimensions})"
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


def get_unit_converter() -> UnitConverter:
    """Return an object to convert from one unit to another (containing all unit conversion factors)

    Returns
    -------
    unit_converter : UnitConverter
        UnitConverter object to convert from one unit to another (containing all unit conversion factors)

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    units_file_path = resources.files(data) / "units" / "units.json"
    with open(units_file_path, mode="r", encoding="utf-8") as _file_descriptor:
        units: Dict[str, List[Dict[str, Any]]] = json.load(_file_descriptor)
    unit_converter = UnitConverter(**units)
    return unit_converter
