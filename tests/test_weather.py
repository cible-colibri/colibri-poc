# -*- coding: utf-8 -*-

from core.project                      import Project
from models.utility.weather import Weather


def test_weather():

    project = Project()

    weather = Weather("weather-1")

    project.add(weather)
    project.run()
    pass
