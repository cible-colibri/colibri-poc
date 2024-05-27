# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pytest

# ========================================
# Internal imports
# ========================================

from colibri.core.connectors.hydronics.fluid_flow import FluidFlowConnector
from colibri.core.models.project                    import Project
from colibri.models.hydronics.duct import Duct
from colibri.models.hydronics.simple_pump import SimplePump
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
def test_storage_tank_system():

    # Create a project
    project = Project()
    # Create a duct (from Duct model)
    duct_1 = Duct("duct_1")
    # Set the parameters / characteristics of the duct using the get_input method
    duct_1.get_input("inlet_flow_rate").value = 100
    # Set the parameters / characteristics of the duct using the attributes
    duct_1.inlet_temperature = 40
    # Add duct_1 to project
    project.add(duct_1)
    # Create another duct (from Duct model)
    duct_2 = Duct("duct_2")
    duct_2.inlet_temperature = 40
    project.add(duct_2)
    # Create a connector
    liquid_flow = FluidFlowConnector()
    # Link both ducts
    project.link(duct_1, duct_2, liquid_flow)
    # Add a pump
    pump_1 = SimplePump("pump_1")
    pump_1.inlet_temperature = 40
    project.add(pump_1)
    project.link(duct_2, pump_1, liquid_flow)
    # Alternative for linking models variable by variable
    #project.link("duct-1", "flow", "duct-2", "flow")
    # Create a storage tank
    storage_tank_1 = StorageTank("storage_tank_1")
    # Expand variable list to 3
    storage_tank_1.number_of_nodes = 3
    storage_tank_1.height_node_1 = 0.5
    storage_tank_1.height_node_2 = 0.5
    storage_tank_1.height_node_3 = 0.5
    project.add(storage_tank_1)
    # # Link to pump & ducts
    project.link(pump_1, "outlet_flow_rate", storage_tank_1, "inlet_flow_rate_1")
    project.link(pump_1, "outlet_temperature", storage_tank_1, "inlet_temperature_1")
    project.link(storage_tank_1, "outlet_flow_rate_1", duct_1, "inlet_flow_rate")
    project.link(storage_tank_1, "outlet_temperature_1", duct_1, "inlet_temperature")
    # Save project as a json file
    # TODO: fix project dumping
    # project.save_as_json(f"{project.name}.json")
    # Run project
    project.time_steps = 24
    project.n_max_iterations = 200
    project.add_plot("Temperatures_ducts", duct_1, "outlet_temperature")
    project.add_plot("Temperatures_ducts", duct_2, "outlet_temperature")
    project.add_plot("Temperatures_pump", pump_1, "outlet_temperature")
    project.add_plot("Temperatures_storage", storage_tank_1, "outlet_temperature_1")
    project.run()


if __name__ == "__main__":
    test_storage_tank_system()
