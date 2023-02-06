# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from core.plot import Plot
from models.hydronics.duct import Duct

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
def test_plot():
    duct_1 = Duct("duct_1")
    plot = Plot("plot_1", duct_1, "outlet_temparature")
    assert isinstance(plot, Plot)
    assert hasattr(plot, "name")
    assert hasattr(plot, "model")
    assert hasattr(plot, "variable_name")
    assert plot.__str__() == "Plot(name='plot_1', model=Duct(name = 'duct_1'), variable_name='outlet_temparature')"
    assert plot.__repr__() == plot.__str__()


if __name__ == "__main__":
    test_plot()
