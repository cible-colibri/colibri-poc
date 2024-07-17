import os

from pkg_resources import resource_filename

from colibri.core.processing.building.building_data import BuildingData
from colibri.core.project import Project
from colibri.models.example_archi.InfinitePowerGenerator import InfinitePowerGenerator
from colibri.models.example_archi.LayerWallLosses import LayerWallLosses
from colibri.models.example_archi.LimitedGenerator import LimitedGenerator
from colibri.models.example_archi.SimplifiedWallLosses import SimplifiedWallLosses
from colibri.models.example_archi.ThermalSpace import ThermalSpaceSimplified
from colibri.models.utility.weather import Weather

def test_run_example_project():

    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    file_name = 'house_1.json'
    weather_file = 'Paris.epw'
    time_zone = 'Europe/Paris'
    building_file = os.path.join(building_path, file_name)

    # Create a project
    project = Project()

    project.iterate = False
    project.time_steps = 168
    project.verbose = False

    # weather
    weather = Weather("weather")
    weather.constant_ground_temperature = 10.
    weather.weather_file = weather_file
    weather.time_zone = time_zone
    project.add(weather)

    building_data = BuildingData(building_file)
    project.add(building_data)

    # TODO : explain why we want this in real-life applications
    #project.create_envelop()
    #project.create_systems()


    wall_losses = SimplifiedWallLosses("M1a")
    project.add(wall_losses)
    project.link(building_data, 'Boundaries', wall_losses, 'Boundaries')
    project.link(wall_losses, 'Qwall', building_data , 'Qwall')

    # wall_losses = LayerWallLosses("M1b")
    # project.add(wall_losses)
    # project.link(building_data, 'Boundaries', wall_losses, 'Boundaries')
    # project.link(wall_losses, 'Qwall', building_data , 'Qwall')

    project.link(weather, 'Text', wall_losses, 'Text')

    # power_generator = InfinitePowerGenerator("IM_2")
    # project.add(power_generator)
    # project.link(building_data, 'Spaces', power_generator, 'Spaces')

    limited_power_generator = LimitedGenerator("IM_2b")
    project.add(limited_power_generator)
    project.link(building_data, 'Spaces', limited_power_generator, 'Spaces')
    project.link(limited_power_generator, 'Spaces', building_data, 'Spaces')

    space_simplified = ThermalSpaceSimplified("IM_3")
    project.add(space_simplified)

    project.link(building_data, 'Spaces', space_simplified, 'Spaces')
    project.link(space_simplified, 'Qneeds', limited_power_generator, 'Qneeds')

    project.link(building_data, 'Qwall', space_simplified, 'Qwall')

    project.link(limited_power_generator, 'Qprovided', space_simplified, 'Qprovided')

    # TODO: générer les lines automatiquement

    project.add_plot("Weather", weather, "Text")
    project.add_plot("Tint", space_simplified, "Tint")
    project.add_plot("Qwall", wall_losses, "Qwall")
    project.add_plot("Qprovided", limited_power_generator, "Qprovided")
    project.to_plot = True
    project.run()
    project.plot()
    pass

    #input_template = wall_losses.input_template()
    #parameter_template = wall_losses.parameter_template()
    #output_template = wall_losses.output_template()
    #template = wall_losses.template()


