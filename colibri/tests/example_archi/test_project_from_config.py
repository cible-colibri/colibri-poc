import os

from pkg_resources import resource_filename

from colibri.core.project import Project


def test_project_from_config():
    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    file_name = 'house_1.json'
    weather_file = 'Paris.epw'
    time_zone = 'Europe/Paris'
    building_file = os.path.join(building_path, file_name)

    # auto_links based on names are created first
    # custom_links unlink if necessary
    # instances used the class name (without path) as name perdefault ; to change it, used 'name' parameter
    config = {
        "models": [("colibri.core.model.Model", "colibri.models.utility.weather.Weather", {"name": "Weather", "weather_file": weather_file, "time_zone": time_zone}),
                   ("colibri.core.model.Model", "colibri.core.processing.building.building_data.BuildingData", {"building_file": building_file}),
                   ("colibri.models.example_archi.wall.wall.Wall", "colibri.models.example_archi.wall.simplified_wall_losses.SimplifiedWallLosses", {}),
                   ("colibri.core.model.Model", "colibri.models.example_archi.limited_generator.LimitedGenerator", {"efficiency": 0.9}),
                   ("colibri.core.model.Model", "colibri.models.example_archi.thermal_space.ThermalSpaceSimplified", {}),
                   ("colibri.core.model.Model", "colibri.models.example_archi.acv_exploitation_only_model.ACVExploitationOnlyModel", {}), ],

        # "custom_links" : [
        #     ("Weather", "Text", "SimplifiedWallLosses", "Toutside")
        #            ],

        "project": {
            "iterate": True,
            "n_max_iterations": 4,
            "time_steps": 168,
            "verbose": False,
            "convergence_tolerance": 0.1,
            "auto_links": True
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
