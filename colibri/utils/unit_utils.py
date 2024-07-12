# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================
import os
import typing

# ========================================
# Internal imports
# ========================================
from pkg_resources import resource_filename

from colibri.utils.files_utils import read_json_file
from colibri.utils.singleton import Singleton
from colibri.utils.enums_utils import Units

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


class Unit:

    def __init__(self, name: str, description: str, addition_factor: float, multiplication_factor: float, si_code: str):
        self.name                  = name
        self.description           = description
        self.addition_factor       = float(addition_factor)
        self.multiplication_factor = float(multiplication_factor)
        self.si_code               = si_code

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
        string_representation = f"{self.__class__.__name__}({self.name}, {self.description}, {self.addition_factor}, {self.multiplication_factor}, {self.si_code})"
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


class Dimension:

    def __init__(self, name: str, definition: str, base_unit: Unit, equivalent_units: typing.List[Unit]):
        self.name             = name
        self.definition       = definition
        self.base_unit        = Unit(**base_unit)
        self.equivalent_units = []
        for equivalent_unit in equivalent_units:
            unit = Unit(**equivalent_unit)
            self.equivalent_units.append(unit)

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
        string_representation = f"{self.__class__.__name__}({self.name}, {self.definition}, {self.base_unit}, {self.equivalent_units})"
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


class UnitConverter(metaclass=Singleton):

    def __init__(self, dimensions: typing.List[dict]):
        self.dimensions = []
        for dimension_data in dimensions:
            dimension = Dimension(**dimension_data)
            self.dimensions.append(dimension)

    def get_unit(self, unit: Units):
        for dimension in self.dimensions:
            if dimension.base_unit.name == unit:
                return dimension.base_unit
            else:
                for equivalent_unit in dimension.equivalent_units:
                    if equivalent_unit.name == unit:
                        return equivalent_unit
        return None

    def convert(self, value: float, unit_from: Units, unit_to: Units) -> float:
        unit1 = self.get_unit(unit_from)
        if not unit1:
            raise Exception("Unit {unit_from_name} not found")
        unit2 = self.get_unit(unit_to)
        if not unit2:
            raise Exception(f"Unit {unit_to} not found")
        return ((value - unit1.addition_factor) / unit1.multiplication_factor) * unit2.multiplication_factor + unit2.addition_factor

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
        string_representation = f"{self.__class__.__name__}({self.dimensions})"
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


# Return an object to convert from one unit to another (containing all unit conversion factors)
def get_unit_converter() -> UnitConverter:
    """Return an object to convert from one unit to another (containing all unit conversion factors)

    Parameters
    ----------

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
    units_path = resource_filename('colibri', os.path.join('data', 'units'))
    units_file_path = os.path.join(units_path, 'units.json')
    units            = read_json_file(units_file_path, )
    unit_converter   = UnitConverter(**units)
    return unit_converter
