# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import time

# ========================================
# Internal imports
# ========================================

from connectors.hydronics.fluid_flow import LiquidFlowConnector
from core.conditions                 import Conditions
from core.project                    import Project
from core.parameters                 import Parameters
from core.variable                   import Variable
from models.hydronics.pump           import Pump
from models.hydronics.pipe           import Pipe
from utils.enums_utils               import Units

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

def test_project():

    starting_time    = time.perf_counter()

    # Parameters
    internal_diameter = Variable("internal_diameter", 0.009, Units.METER)
    tube_length       = Variable("tube_length", 10.0, Units.METER)
    parameters_pipe_1 = Parameters().add(internal_diameter).add(tube_length)
    efficiency        = Variable("efficiency", 0.25, Units.METER)
    parameters_pump_1 = Parameters().add(efficiency)

    # Initial conditions
    inlet_flow_rate   = Variable("inlet_flow_rate", 3.0 / 60.0, Units.KILOGRAM_PER_SECOND, "Flow rate of the pump")
    inlet_pressure    = Variable("inlet_pressure", 10_000.0, Units.PASCAL, "Pressure drop")
    conditions_pump_1 = Conditions().add(inlet_flow_rate).add(inlet_pressure)

    # Create a project
    project           = Project("project_1")

    # Create a pipe (from Pipe model) with its parameters (from Parameters model) and initial conditions (from Conditions model)
    pipe_1            = Pipe("pipe_1", parameters_pipe_1)
    # Set the parameters / characteristics of the pipe using the get_input method
    pipe_1.get_input("inlet_flow_rate").value = 0.04
    # Set the parameters / characteristics of the pipe using the attributes (which is a Variable object)
    pipe_1.inlet_flow_rate.value = 0.05
    # Add pipe_1 to project
    project.add(pipe_1)

    # Create a pump (from Pump model)
    pump_1 = Pump("pump_1", parameters_pump_1,  conditions_pump_1)
    project.add(pump_1)

    # Create a connector
    liquid_flow = LiquidFlowConnector()
    # Link pipe to pump
    project.link(pipe_1, pump_1, liquid_flow)

    # Save project as a json file
    # project.save_as_json(f"{project.name}.json")

    # Run project
    project.run()

    print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")


if __name__ == "__main__":
    test_project()
