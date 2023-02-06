# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from core.link             import Link
from core.model            import Model
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
def test_links():
    duct_1 = Duct("duct_1")
    duct_2 = Duct("duct_2")
    link_1 = Link(duct_1, "inlet_temperature", duct_2, "outlet_temperature")
    link_2 = Link(duct_1, "inlet_flow_rate", duct_2, "outlet_flow_rate")
    assert isinstance(link_1, Link)
    assert isinstance(link_2, Link)
    assert hasattr(link_1, "from_model")
    assert hasattr(link_1, "from_variable")
    assert hasattr(link_1, "to_model")
    assert hasattr(link_1, "to_variable")
    assert isinstance(link_1.from_model, Model)
    assert link_1.__str__() == "Link(from_model=Duct(name = 'duct_1'), from_variable='inlet_temperature', to_model=Duct(name = 'duct_2'), to_variable='outlet_temperature')"
    assert link_1.__repr__() == link_1.__str__()
    assert link_2.__repr__() == link_2.__str__()


if __name__ == "__main__":
    test_links()
