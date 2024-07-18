# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.model                   import Model
from colibri.models.hydronics.simple_pump import SimplePump

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
def test_simple_pump():
    pump = SimplePump("pump_1")
    assert isinstance(pump, SimplePump)
    assert isinstance(pump, Model)
    pump.initialize()
    time_step = 0
    pump.run(time_step)
    pump.simulation_done(time_step)
    pump.iteration_done(time_step)
    pump.timestep_done(time_step)
    pump.simulation_done(time_step)
    assert pump.__str__() == "SimplePump(name = 'pump_1')"
    assert pump.__repr__() == pump.__str__()

if __name__ == "__main__":
    test_simple_pump()
