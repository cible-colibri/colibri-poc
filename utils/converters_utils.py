# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pandas

# ========================================
# Internal imports
# ========================================

from utils.enums_utils import (
                                EnergyUnits,
                                Units,
                               )

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


# ========================================
# Functions
# ========================================

# Return unit conversion factors as a dataframe (index = si unit, columns = other units)
def get_unit_conversion_factors() -> pandas.DataFrame:
    """Return unit conversion factors as a dataframe (index = si unit, columns = other units)

    Parameters
    ----------

    Returns
    -------
    unit_conversion_factors : pandas.DataFrame
        Dataframe containing unit conversion factors (index = si unit, columns = other units)

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    data                            = {
                                       "si_units":                 [EnergyUnits.JOULE],
                                       EnergyUnits.KILO_JOULE:     [1_000],
                                       EnergyUnits.KILO_WATT_HOUR: [1.0 / 3_600_000.0],
                                       EnergyUnits.WATT_HOUR:      [1.0 / 3_600.0],
                                       }
    unit_conversion_factors         = pandas.DataFrame.from_dict(data)
    unit_conversion_factors.set_index(["si_units"], inplace = True)
    return unit_conversion_factors
