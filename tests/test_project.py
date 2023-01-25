# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from connectors.hydronics.fluid_flow   import LiquidFlowConnector
from core.project                      import Project
from models.hydronics.duct             import Duct
from models.storage.storage_tank       import StorageTank

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

    # Create a project
    project = Project()
    # Create a duct (from Duct model)
    duct_1 = Duct("duct_1")
    # Set the parameters / characteristics of the duct using the get_input method
    duct_1.get_input("inlet_flow").value = 100
    duct_1.get_input("inlet_temperature").value = 20
    # Set the parameters / characteristics of the duct using the attributes
    duct_1.inlet_temperature = 21
    # Add duct_1 to project
    project.add(duct_1)
    # Create another duct (from Duct model)
    duct_2 = Duct("duct_2")
    project.add(duct_2)
    # Create a connector
    liquid_flow = LiquidFlowConnector()
    # Link both ducts
    project.link(duct_1, duct_2, liquid_flow)

    # Alternative for linking models variable by variable
    #project.link("duct-1", "flow", "duct-2", "flow")

    # Create a storage tank
    storage_tank_1 = StorageTank("storage tank_1")
    # Define the
    storage_tank_1.set("Number of thermostats", 2) # expands variable list to 2:
    storage_tank_1.set("Height fraction of thermostat-1", 0.0)
    storage_tank_1.get_input("Height fraction of thermostat-2").value = 0.5
    project.add(storage_tank_1)
    # Link both ducts
    project.link(duct_2, storage_tank_1, liquid_flow)
    # Save project as a json file
    # TODO: fix project dumping
    # project.save_as_json(f"{project.name}.json")
    # Run project
    project.run()
