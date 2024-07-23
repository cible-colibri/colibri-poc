import os

from pkg_resources import resource_filename

from colibri.core.project import Project


def test_project_from_config():
    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    file_name = 'house_1.json'
    weather_file = 'Paris.epw'
    time_zone = 'Europe/Paris'
    building_file = os.path.join(building_path, file_name)

    config = {
        "models": [("colibri.models.utility.weather.Weather", {"weather_file": weather_file, "time_zone": time_zone}),
                   ("colibri.core.processing.building.building_data.BuildingData", {"building_file": building_file}),
                   ("colibri.models.example_archi.SimplifiedWallLosses.SimplifiedWallLosses", {}),
                   ("colibri.models.example_archi.LimitedGenerator.LimitedGenerator", {"efficiency": 0.9}),
                   ("colibri.models.example_archi.ThermalSpace.ThermalSpaceSimplified", {}),
                   ("colibri.models.example_archi.ACVExploitationOnlyModel.ACVExploitationOnlyModel", {}), ],

        "project": {
            "iterate": False,
            "n_max_iterations": 1,
            "time_steps": 168,
            "verbose": False

        },

        "version": "RT2042"

    }

    project = Project("pfc")
    project.project_from_config(config)

    # son & lumière
    project.add_plot("Weather", project.get("Weather"), "Text")
    project.add_plot("Tint", project.get("ThermalSpaceSimplified"), "Tint")
    project.add_plot("Qwall", project.get("SimplifiedWallLosses"), "Qwall")
    project.add_plot("Qprovided", project.get("LimitedGenerator"), "Qprovided")
    project.to_plot = True

    project.run()
    project.plot()