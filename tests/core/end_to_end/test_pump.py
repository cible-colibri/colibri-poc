# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import time

# ========================================
# Internal imports
# ========================================

from core.connectors.hydronics.fluid_flow import FluidFlowConnector
from core.project                    import Project
from core.templates.inputs import Inputs
from core.templates.parameters import Parameters
from core.variables.variable import Variable
from models.hydronics.duct import Duct
from models.hydronics.simple_pump import SimplePump
from utils.enums_utils               import (
                                                Roles,
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

def test_pump():

    starting_time    = time.perf_counter()

    # Parameters
    internal_diameter = Variable("internal_diameter", 0.009, Roles.PARAMETERS, Units.METER)
    tube_length       = Variable("tube_length", 10.0, Roles.PARAMETERS, Units.METER)
    parameters_duct_1 = Parameters().add(internal_diameter).add(tube_length)
    efficiency        = Variable("efficiency", 0.25, Roles.PARAMETERS, Units.METER)
    parameters_pump_1 = Parameters().add(efficiency)
    # Initial conditions
    inlet_flow_rate   = Variable("inlet_flow_rate", 3.0 / 60.0, Roles.INPUTS, Units.KILOGRAM_PER_SECOND, "Flow rate of the pump")
    inlet_pressure    = Variable("inlet_pressure", 10_000.0, Roles.INPUTS, Units.PASCAL, "Pressure drop")
    conditions_pump_1 = Inputs().add(inlet_flow_rate).add(inlet_pressure)
    # Create a project
    project           = Project("project_1")
    # Create a duct (from Duct model) with its parameters (from Parameters model) and initial conditions (from Conditions model)
    duct_1            = Duct("duct_1", parameters = parameters_duct_1)
    # Set the parameters / characteristics of the duct using the get_input method
    duct_1.get_input("inlet_flow_rate").value = 0.04
    # Set the parameters / characteristics of the duct using the attributes (which is a Variable object)
    duct_1.inlet_flow_rate.value = 0.05
    # Add duct_1 to project
    project.add(duct_1)
    # Create a pump (from Pump model)
    pump_1 = SimplePump("pump_1", inputs = conditions_pump_1, parameters = parameters_pump_1)
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
