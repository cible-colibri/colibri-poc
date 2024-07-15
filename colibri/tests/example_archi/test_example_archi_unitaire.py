import json
import os

from pkg_resources import resource_filename

from colibri.core.processing.building.building_data import BuildingData
from colibri.models.example_archi.LayerWallLosses import LayerWallLosses
from colibri.models.example_archi.SimplifiedWallLosses import SimplifiedWallLosses

def test_generate_json():
    wall_losses = LayerWallLosses("Pertes avec couches")
    # create a json (input and parameters)
    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    in_values = wall_losses.input_parameter_template()
    json_file = os.path.join(building_path, 'wall_losses_in.json')
    with open(json_file, "w") as f:
        f.write(json.dumps(in_values, indent=4))

    # create a json (expected outputs with default values)
    output_template = wall_losses.output_template()
    json_file = os.path.join(building_path, 'wall_losses_out.json')
    with open(json_file, "w") as f:
        f.write(json.dumps(output_template, indent=4))

    # run from json
    json_file = os.path.join(building_path, 'wall_losses_in.json')
    with open(json_file, "r") as f:
        in_values = json.loads(f.read())

    wall_losses2 = LayerWallLosses("M1b from json")
    wall_losses2.load_from_json(in_values)
    wall_losses2.run()
    result = wall_losses2.Qwall
    print(result)

def test_run_model_objects():

    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    file_name = 'house_1.json'
    building_file = os.path.join(building_path, file_name)
    building_data = BuildingData(building_file)

    wall_losses = SimplifiedWallLosses("M1b")
    wall_losses.Boundaries = building_data.boundary_list
    wall_losses.run()
    print(wall_losses.Qwall)

