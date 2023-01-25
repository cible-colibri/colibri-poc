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
class Schema(enum.Enum):
    RE2020 = "re2020"


# TODO: Split Units by theme to avoid something too long (like EnergyUnits, etc.)
@enum.unique
class Units(enum.Enum):
    DEGREE_CELCIUS      = "°C"
    KILOGRAM_PER_SECOND = "kg/s"
    METER               = "m"
    PASCAL              = "Pa"
    UNITLESS            = "-"


@enum.unique
class EnergyUnits(enum.Enum):
    JOULE          = "J"
    KILO_JOULE     = "kJ"
    KILO_WATT_HOUR = "kWh"
    WATT_HOUR      = "Wh"



# ========================================
# Functions
# ========================================
