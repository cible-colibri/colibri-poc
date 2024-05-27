"""
This file tests the simple_pump.py module.
"""

import time

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector
from colibri.core.models.project import Project
from colibri.core.variables.inputs import Inputs
from colibri.core.variables.parameters import Parameters
from colibri.core.variables.variable import Variable
from colibri.models.hydronics.duct import Duct
from colibri.models.hydronics.simple_pump import SimplePump
from colibri.utils.enums_utils import Roles, Units


def test_pump(verbose: bool = False) -> None:
    """Test the SimplePump class."""
    # Save starting time
    starting_time: float = time.perf_counter()
    # Define variables and parameters
    internal_diameter: Variable = Variable(
        name="internal_diameter", value=0.009, role=Roles.PARAMETERS, unit=Units.METER
    )
    tube_length: Variable = Variable(
        name="tube_length", value=10.0, role=Roles.PARAMETERS, unit=Units.METER
    )
    parameters_duct_1 = Parameters().add(internal_diameter).add(tube_length)
    efficiency: Variable = Variable(
        name="efficiency", value=0.25, role=Roles.PARAMETERS, unit=Units.METER
    )
    parameters_pump_1: Parameters = Parameters().add(efficiency)
    # Initial conditions
    inlet_flow_rate = Variable(
        "inlet_flow_rate",
        3.0 / 60.0,
        Roles.INPUTS,
        Units.KILOGRAM_PER_SECOND,
        "Flow rate of the pump",
    )
    inlet_pressure: Variable = Variable(
        "inlet_pressure", 10_000.0, Roles.INPUTS, Units.PASCAL, "Pressure drop"
    )
    conditions_pump_1: Inputs = Inputs().add(inlet_flow_rate).add(inlet_pressure)
    # Create a project
    project: Project = Project(name="project_1")
    # Create a duct (from Duct model) with its parameters (from Parameters model) and initial conditions (from Conditions model)
    duct_1: Duct = Duct(name="duct_1", parameters=parameters_duct_1)
    # Set the parameters / characteristics of the duct using the get_input method
    duct_1.get_input(name="inlet_flow_rate").value = 0.04
    # Set the parameters / characteristics of the duct using the attributes (which is a Variable object)
    duct_1.inlet_flow_rate.value = 0.05
    # Add duct_1 to project
    project.add(duct_1)
    # Create a pump (from Pump model)
    pump_1: SimplePump = SimplePump(
        name="pump_1", inputs=conditions_pump_1, parameters=parameters_pump_1
    )
    project.add(pump_1)
    # Create a connector
    liquid_flow: FluidFlowConnector = FluidFlowConnector()
    # Link duct to pump
    project.link(duct_1, pump_1, liquid_flow)
    # Run project
    project.run()
    # Show execution time
    total_time: float = time.perf_counter() - starting_time
    if verbose is True:
        print(f"Simulation time: {total_time:3.2f} seconds")
    assert total_time < 0.1


if __name__ == "__main__":
    test_pump(verbose=True)
