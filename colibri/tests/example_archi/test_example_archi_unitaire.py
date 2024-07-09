import json
import os

from pkg_resources import resource_filename

from colibri.core.dataclasses.Building.building_data import BuildingData
from colibri.core.project import Project
from colibri.models.example_archi.LayerWallLosses import LayerWallLosses
from colibri.models.example_archi.SimplifiedWallLosses import SimplifiedWallLosses
from colibri.models.example_archi.SimplifiedWallLossesJson import SimplifiedWallLossesJson
from colibri.models.utility.weather import Weather

def test_run_model_objects():

    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    file_name = 'house_1.json'
    building_file = os.path.join(building_path, file_name)
    building_data = BuildingData(building_file)

    wall_losses = SimplifiedWallLosses("M1b")
    wall_losses.Boundaries = building_data.boundary_list
    wall_losses.run()
    print(wall_losses.Qwall)

def test_run_model_json():
    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    file_name = 'house_1.json'
    building_file = os.path.join(building_path, file_name)
    with open(building_file, 'r') as f:
        j = json.load(f)


    wall_losses = SimplifiedWallLossesJson("M1bJ")
    wall_losses.inputs = j

    # set inputs
    for space_id, space in wall_losses.inputs['nodes_collection']['space_collection'].items():
        space['Tint'] = 20
    wall_losses.inputs['Text'] = 10

    # set parameters
    for boundary_id, boundary in wall_losses.inputs['boundary_collection'].items():
        boundary['area'] = 10
        boundary['u_value'] = 2

    wall_losses.run()
    print(wall_losses.Qwall)




    # m1 = SimplifiedWallLosses()
    # m1.inputs = j1['inputs']
    # m1.outputs = j1['outputs']
    # m1.run()
    # print(m1.outputs)
    #
    # m1.Text = j1['Text']
    # m1.Boundaries = j1['Boundaries']
    # m1.run()
    # print(m1.QWall)
    #
    # m1.template()