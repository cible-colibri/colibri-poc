import json
import os

from pkg_resources import resource_filename
from colibri.core.project import Project
from colibri.models.example_archi.SimplifiedWallLosses import SimplifiedWallLosses
from colibri.models.example_archi.SimplifiedWallLosses_no_for import SimplifiedWallLossesNoLoop
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

    building_data = project.add_building_data(building_file)

    # TODO : explain why we want this in real-life applications
    #project.create_envelop()
    #project.create_systems()


    wall_losses = SimplifiedWallLossesNoLoop("M1a")
    wall_losses.U = [b.u_value for b in building_data.boundary_list]
    wall_losses.S = [b.area for b in building_data.boundary_list]
    project.add(wall_losses)

    # add links
    # dans le vrai Colibri, weather aurait un output qui s'apelle 'Text', ici on utilise un lecteur météo existant (non-colibri)
    project.link(weather, 'temperature', wall_losses, 'Text')


    project.link(building_data, 'TintWall', wall_losses, 'Tint')
    project.link(wall_losses, 'QWall_out', building_data , 'QWall_in')

    # TODO: générer les lines automatiquement

    project.run()


