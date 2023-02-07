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
class Roles(enum.Enum):
    INPUTS     = "inputs"
    OUTPUTS    = "outputs"
    PARAMETERS = "parameters"


@enum.unique
class Schema(enum.Enum):
    RE2020 = "re2020"


@enum.unique
class Units(enum.Enum):
    CENTIMETER                              = "cm"
    DEGREE                                  = "°"
    DEGREE_CELSIUS                          = "°C"
    DEGREE_FAHRENHEIT                       = "°F"
    HOUR                                    = "h"
    JOULE                                   = "J"
    JOULE_PER_GRAM_PER_DEGREE_CELCIUS       = "J/(g.°C)"
    KELVIN                                  = "K"
    KILO_JOULE                              = "kJ"
    KILO_JOULE_PER_HOUR                     = "kJ/h"
    KILO_METER                              = "km"
    KILO_WATT                               = "kW"
    KILO_WATT_HOUR                          = "kWh"
    KILOGRAM_PER_HOUR                       = "kg/h"
    KILOGRAM_PER_SECOND                     = "kg/s"
    METER                                   = "m"
    PASCAL                                  = "Pa"
    SQUARE_METER                            = "m²"
    UNITLESS                                = "-"
    WATT                                    = "W"
    WATT_HOUR                               = "Wh"
    WATT_PER_SQUARE_METER                   = "W/m²"
    WATT_PER_SQUARE_METER_PER_KELVIN        = "W/(m².K)"
    WATT_PER_SQUARE_METER_PER_SQUARE_KELVIN = "W/(m².K²)"

# ========================================
# Functions
# ========================================
