# -*- coding: utf-8 -*-

from core.project                      import Project
from models.thermal.SimpleBuilding.simple_building import SimpleBuilding
from models.utility.weather import Weather


def test_building():

    project = Project()

    weather = Weather("weather-1")
    project.add(weather)

    building = SimpleBuilding("ChezPeter")
    project.add(building)

    # link temperature and radiation to building
    project.link(weather, "temperature", building, "ext_temperature")
    project.link(weather, "GloHorzRad", building, "radiation")

    project.time_steps = 8760
    project.run()
    pass
