# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import enum

# ========================================
# Internal imports
# ========================================


# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

@enum.unique
class AreaUnits(enum.Enum):
    SQUARE_METER = "m²"


@enum.unique
class EnergyUnits(enum.Enum):
    JOULE          = "J"
    KILO_JOULE     = "kJ"
    KILO_WATT_HOUR = "kWh"
    WATT_HOUR      = "Wh"


@enum.unique
class FlowUnits(enum.Enum):
    KILOGRAM_PER_HOUR   = "kg/h"
    KILOGRAM_PER_SECOND = "kg/s"


@enum.unique
class LengthUnits(enum.Enum):
    CENTIMETER = "cm"
    METER      = "m"
    KILO_METER = "km"


@enum.unique
class PressureUnits(enum.Enum):
    PASCAL = "Pa"


@enum.unique
class Schema(enum.Enum):
    RE2020 = "re2020"


@enum.unique
class TemperatureUnits(enum.Enum):
    DEGREE_CELSIUS    = "°C"
    DEGREE_FAHRENHEIT = "°F"
    KELVIN            = "K"


@enum.unique
class TimeUnits(enum.Enum):
    HOUR = "h"


@enum.unique
class Units(enum.Enum):
    DEGREE                                   = "°"
    JOULE_PER_GRAM_PER_DEGREE_CELCIUS        = "J/(g.°C)"
    KILO_JOULE_PER_HOUR                      = "kJ/h"
    UNITLESS                                 = "-"
    WATT_PER_SQUARE_METER_PER_KELVIN         = "W/(m².K)"
    WATT_PER_SQUARE_METER_PER_SQUARE_KELVIN  = "W/(m².K²)"

# ========================================
# Functions
# ========================================
