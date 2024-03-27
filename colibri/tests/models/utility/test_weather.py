# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import time
import os

# ========================================
# Internal imports
# ========================================

from colibri.core.project           import Project
from colibri.models.utility.weather import Weather
from colibri.utils import data_path


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

def test_weather():

    # Save starting time
    starting_time = time.perf_counter()
    # Create a project
    project       = Project()
    # Create a weather (from Weather model)
    weather       = Weather("weather_1")
    weather.weather_file = os.path.join(data_path['weather'], 'epw/Paris.epw')
    # Add weather to project
    project.add(weather)
    # Run project
    project.run()
    # Show execution time
    print(f"Simulation time: {(time.perf_counter() - starting_time):3.2f} seconds")


if __name__ == "__main__":
    test_weather()
