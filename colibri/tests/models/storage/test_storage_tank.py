# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.models.model                  import Model
from colibri.models.storage.storage_tank import StorageTank

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
def test_tank():
    tank = StorageTank("tank_1")
    assert isinstance(tank, StorageTank)
    assert isinstance(tank, Model)
    tank.initialize()
    tank.check_units()
    time_step = 0
    tank.run(time_step)
    tank.simulation_done(time_step)
    tank.iteration_done(time_step)
    tank.timestep_done(time_step)
    tank.simulation_done(time_step)
    assert tank.__str__() == "StorageTank(name = 'tank_1')"
    assert tank.__repr__() == tank.__str__()


if __name__ == "__main__":
    test_tank()
