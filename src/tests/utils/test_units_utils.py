"""
Tests for the `units_utils.py` module.
"""

import pytest

from colibri.utils.enums_utils import Units
from colibri.utils.exceptions_utils import UnitError
from colibri.utils.units_utils import (
    Dimension,
    Unit,
    UnitConverter,
    get_unit_converter,
)


def test_unit() -> None:
    """Test the Unit class."""
    unit: Unit = Unit(
        name="K",
        description="A measure of TEMPERATURE in the SI unit system",
        addition_factor=0.0,
        multiplication_factor=1.0,
        si_code="K",
    )
    assert unit.name == "K"
    assert unit.description == "A measure of TEMPERATURE in the SI unit system"
    assert unit.addition_factor == 0.0
    assert unit.multiplication_factor == 1.0
    assert unit.si_code == "K"


def test_dimension() -> None:
    """Test the Dimension class."""
    dimension: Dimension = Dimension(
        name="Specific Thermal Capacitance",
        definition="The product of specific heat and density",
        base_unit={
            "name": "kJ/m3.K",
            "description": "",
            "addition_factor": "0",
            "multiplication_factor": "1",
            "si_code": "-",
        },
        equivalent_units=[],
    )
    assert dimension.name == "Specific Thermal Capacitance"
    assert dimension.definition == "The product of specific heat and density"
    temperature_unit: Unit = Unit(
        name="K",
        description="A measure of TEMPERATURE in the SI unit system",
        addition_factor=0.0,
        multiplication_factor=1.0,
        si_code="K",
    )
    dimension_2: Dimension = Dimension(
        name="Temperature",
        definition="This is a base magnitude.",
        base_unit=temperature_unit,
        equivalent_units=[
            {
                "name": "°C",
                "description": "A unit of TEMPERATURE in the SI unit system:////K = C + 273.15//",
                "addition_factor": "-273.15",
                "multiplication_factor": "1.0",
                "si_code": "K",
            }
        ],
    )
    assert dimension_2.name == "Temperature"
    assert dimension_2.base_unit == temperature_unit
    assert isinstance(dimension_2.equivalent_units[0], Unit)


def test_get_unit_converter() -> None:
    """Test the get_unit_converter function."""
    unit_converter: UnitConverter = get_unit_converter()
    assert isinstance(unit_converter, UnitConverter) is True
    unit_converter_2: UnitConverter = get_unit_converter()
    assert unit_converter is unit_converter_2


def test_unit_converter() -> None:
    """Test the UnitConverter class."""
    unit_converter: UnitConverter = get_unit_converter()
    kelvin_unit: Unit = unit_converter.get_unit(unit=Units.KELVIN)
    assert isinstance(kelvin_unit, Unit)
    assert kelvin_unit.name == "K"
    assert kelvin_unit.si_code == "K"
    assert isinstance(unit_converter.dimensions, list)
    assert isinstance(unit_converter.dimensions[0], Dimension)
    assert (
        unit_converter.convert(
            value=20, unit_from=Units.DEGREE_CELSIUS, unit_to=Units.KELVIN
        )
        == 293.15
    )
    with pytest.raises(UnitError) as exception_information:
        unit_converter.convert(
            value=20,
            unit_from=Units.CO2_KILO_GRAM_EQUIVALENT,
            unit_to=Units.KELVIN,
        )
    assert exception_information.typename == UnitError.__name__
    assert "Unit kgCO2 not found" in str(exception_information.value)
    with pytest.raises(UnitError) as exception_information:
        unit_converter.convert(
            value=20,
            unit_from=Units.DEGREE_CELSIUS,
            unit_to=Units.CO2_KILO_GRAM_EQUIVALENT,
        )
    assert exception_information.typename == UnitError.__name__
    assert "Unit kgCO2 not found" in str(exception_information.value)
    assert str(unit_converter) == repr(unit_converter)


if __name__ == "__main__":
    test_unit()
    test_dimension()
    test_get_unit_converter()
    test_unit_converter()
