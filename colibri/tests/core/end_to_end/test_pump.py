# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import time

# ========================================
# Internal imports
# ========================================

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector
from colibri.core.project                    import Project



from colibri.models.hydronics.duct import Duct
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

def test_pump():

    starting_time = time.perf_counter()

    project = Project("project_1")
    # Create a duct (from Duct model) with its parameters (from Parameters model) and initial conditions (from Conditions model)
    duct_1 = Duct("duct_1")
    duct_1.internal_diameter = internal_diameter = 0.009
    duct_1.length = 10.0

    # Set the parameters / characteristics of the duct using the get_input method
    duct_1.inlet_flow_rate = 0.04
    # Set the parameters / characteristics of the duct using the attributes (which is a Variable object)
    duct_1.inlet_flow_rate = 0.05
    # Add duct_1 to project
    project.add(duct_1)
    # Create a pump (from Pump model)
    pump_1 = SimplePump("pump_1")
    pump_1.inlet_flow_rate = 3.0 / 60.0
    pump_1.inlet_pressure = 10_000.0
    pump_1.efficiency = 0.25
    project.add(pump_1)
    # Create a connector
    liquid_flow = FluidFlowConnector()
    # Link duct to pump
    project.link(duct_1, pump_1, liquid_flow)
    # Save project as a json file
    # project.save_as_json(f"{project.name}.json")
    # Run project
    project.run()
    print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")


if __name__ == "__main__":
    test_pump()
