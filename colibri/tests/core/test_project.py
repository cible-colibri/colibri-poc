# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector
from colibri.core.project import Project
from colibri.models.hydronics.duct import Duct

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
def test_project():

    # Create a project
    project = Project()
    # Create ducts
    duct_1 = Duct("duct_1")
    duct_2 = Duct("duct_2")
    duct_3 = Duct("duct_3")
    # Add ducts
    project.add(duct_1)
    project.add(duct_2)
    project.add(duct_3)
    # Create a connector
    liquid_flow = FluidFlowConnector()
    # Link ducts
    project.link(duct_1, duct_2, liquid_flow)
    project.link(duct_2, "inlet_temperature", duct_3, "outlet_temperature")
    project.link(duct_2, "inlet_flow_rate", duct_3, "outlet_flow_rate")

if __name__ == "__main__":
    test_project()
