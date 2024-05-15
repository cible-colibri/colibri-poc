"""
This file tests the simple_building.py module.
"""

import time
from importlib import resources

from colibri.core.project import Project
from colibri.data.weather import epw

# TODO: Rename SimpleBuilding directory to simple_building or something similar
from colibri.models.thermal.SimpleBuilding.simple_building import SimpleBuilding
from colibri.models.utility.weather import Weather


def test_building(verbose: bool = False) -> None:
    """Test the SimpleBuilding class."""
    # Save starting time
    starting_time: float = time.perf_counter()
    # Create a project
    project: Project = Project()
    # Create a weather (from Weather model) and add it to the project
    weather: Weather = Weather("weather_1")
    weather.weather_file = resources.files(epw) / "Paris.epw"
    project.add(weather)
    # Create a building (from SimpleBuilding model) and add it to the project
    building: SimpleBuilding = SimpleBuilding("ChezPeter")
    project.add(building)
    # Link temperature and radiation from weather to building
    project.link(weather, "temperature", building, "ext_temperature")
    project.link(weather, "GloHorzRad", building, "radiation")
    # Set time steps
    project.time_steps = 8760
    # Set no loops (runs twice as fast)
    project.iterate = False
    # Run project
    project.run()
    # Show execution time
    total_time: float = time.perf_counter() - starting_time
    if verbose is True:
        print(f"Simulation time: {total_time:3.2f} seconds")
    assert total_time < 0.5


if __name__ == "__main__":
    test_building(verbose=True)
