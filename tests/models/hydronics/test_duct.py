# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from core.model            import Model
from core.models.hydronics.duct import Duct

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
def test_duct():
    duct = Duct("duct_1")
    assert isinstance(duct, Duct)
    assert isinstance(duct, Model)
    duct.initialize()
    duct.check_units()
    time_step = 0
    duct.run(time_step)
    duct.simulation_done(time_step)
    duct.iteration_done(time_step)
    duct.timestep_done(time_step)
    duct.simulation_done(time_step)
    assert duct.__str__() == "Duct(name = 'duct_1')"
    assert duct.__repr__() == duct.__str__()

if __name__ == "__main__":
    test_duct()
