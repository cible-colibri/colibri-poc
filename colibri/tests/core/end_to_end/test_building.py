# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import os
import time

# ========================================
# Internal imports
# ========================================

from colibri.utils import data_path
from colibri.core.project import Project
from colibri.models.thermal.SimpleBuilding.simple_building import SimpleBuilding
from colibri.models.utility.weather import Weather

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

def test_building():

    # Save starting time
    starting_time = time.perf_counter()
    # Create a project
    project       = Project()
    # Create a weather (from Weather model) and add it to the project
    weather       = Weather("weather_1")
    weather.weather_file = os.path.join(data_path['weather'], 'epw/Paris.epw')
    project.add(weather)
    # Create a building (from SimpleBuilding model) and add it to the project
    building      = SimpleBuilding("ChezPeter")
    project.add(building)
    # Link temperature and radiation from weather to building
    project.link(weather, "temperature", building, "ext_temperature")
    project.link(weather, "GloHorzRad", building, "radiation")
    # Set time steps
    project.time_steps = 8760
    # Set no loops (runs twice as fast)
    project.iterate    = False
    # Run project
    project.run()
    # Show execution time
    print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")

if __name__ == "__main__":
    test_building()
