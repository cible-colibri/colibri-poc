"""
This file contains all the constants at the package level.
"""

from colibri.utils.unit_utils import UnitConverter, get_unit_converter

# Atmospheric air pressure
ATMOSPHERIC_AIR_PRESSURE: int = 101_300  # [Pa]
# Specific heat capacities
CP_AIR: float = 1_006.0  # [J/(kg.K)]
CP_WATER: float = 4_186.0  # [J/(kg.K)]
# Gravitational acceleration
GRAVITATIONAL_ACCELERATION: float = 9.81  # [m/s²]
# Solar constant of the Earth
SOLAR_CONSTANT_OF_THE_EARTH: float = 1_367.0  # [W/m²]
# Object to convert from one unit to another (has all unit conversion factors)
UNIT_CONVERTER: UnitConverter = get_unit_converter()
# Volumetric density
DENSITY_AIR: float = 1.204785775
