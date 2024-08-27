

config = {
    "models": [("colibri.core.model.Model", "colibri.models.utility.weather.Weather", {}),
               ("colibri.core.model.Model", "colibri.core.processing.building.building_data.BuildingData", {}),
#                   ("colibri.models.example_archi.wall.wall.Wall", "colibri.models.example_archi.wall.layer_wall_losses.LayerWallLosses",{}),
               ("colibri.models.example_archi.wall.wall.Wall", "colibri.models.example_archi.wall.simplified_wall_losses.SimplifiedWallLosses",{}),
               ("colibri.core.model.Model", "colibri.models.example_archi.limited_generator.LimitedGenerator", {}),
               ("colibri.core.model.Model", "colibri.models.example_archi.thermal_space.ThermalSpaceSimplified", {}),
               ("colibri.core.model.Model", "colibri.models.example_archi.acv_exploitation_only_model.ACVExploitationOnlyModel", {}), ],

    # "custom_links" : [
    #     ("Weather", "Text", "SimplifiedWallLosses", "Toutside")
    #            ],

    "project": {
        "iterate": True,
        "n_max_iterations": 10, # max_iterations for ALL models; model instances can set lower values using the check_convergence attribute
        "time_steps": 168,
        "verbose": False,
        "convergence_tolerance": 0.1,
        "auto_links": True
    },

    "version": "RT2042"
}
