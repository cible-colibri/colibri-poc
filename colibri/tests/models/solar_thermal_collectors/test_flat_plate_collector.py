# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.models.model                                           import Model
from colibri.models.solar_thermal_collectors.flat_plate_collector import FlatPlateCollector

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

@pytest.mark.short_test
def test_flat_plate_collector():
    collector = FlatPlateCollector("collector_1")
    assert isinstance(collector, FlatPlateCollector)
    assert isinstance(collector, Model)
    collector.initialize()
    collector.check_units()
    time_step = 0
    collector.run(time_step)
    collector.simulation_done(time_step)
    collector.iteration_done(time_step)
    collector.timestep_done(time_step)
    collector.simulation_done(time_step)
    assert collector.__str__() == "FlatPlateCollector(name = 'collector_1')"
    assert collector.__repr__() == collector.__str__()


if __name__ == "__main__":
    test_flat_plate_collector()
