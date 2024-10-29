from random import randint
from typing import List

from colibri import AcvExploitationOnly, LimitedGenerator, ProjectOrchestrator, ProjectData, InfinitePowerGenerator


def test_field_mixin() -> None:

    acv: AcvExploitationOnly = AcvExploitationOnly(name="acv-1")
    lg = LimitedGenerator("lg-1")

    scheme1 = AcvExploitationOnly.to_template()
    scheme2 = LimitedGenerator.to_template()

    lg2 : LimitedGenerator = LimitedGenerator.from_template(scheme2)
    lg2.initialize()
    lg2.run(1,1)

    print(lg2.q_consumed)

def test_generate_simple_house():
    from colibri.interfaces import Module
    from colibri import OccupantModel
    from colibri import SimplifiedWallLosses
    from colibri import ThermalSpaceSimplified
    from colibri import WeatherModel


    acv_exploitation_only: AcvExploitationOnly = AcvExploitationOnly(name="acv")
    infinite_power_generator: InfinitePowerGenerator = InfinitePowerGenerator(
        name="infinite_power_generator"
    )
    thermal_space_simplified: ThermalSpaceSimplified = ThermalSpaceSimplified(
        name="thermal_space_simplified"
    )
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(
        name="simplified_wall_losses"
    )
    occupants: OccupantModel = OccupantModel(name="occupants")
    weather: WeatherModel = WeatherModel(
        name="weather",
        scenario_exterior_air_temperatures=[
            randint(5, 20) for _ in range(0, 168)
        ],
    )

    #module_collection: List[Module] = [acv_exploitation_only, occupants, infinite_power_generator, simplified_wall_losses, thermal_space_simplified, weather]
    module_collection: List[Module] = [simplified_wall_losses]

    template = {}
    for module in module_collection:
        module_template = module.to_template()
        template = merge_dicts_recursive(template, module_template)

    # run project from template
    project_orchestrator: ProjectOrchestrator = ProjectOrchestrator(name="project1", verbose=False)
    project_data: ProjectData = ProjectData(
        name="project_data", data=template)

    # Add models
    project_orchestrator.add_module(module=project_data)
    project_orchestrator.add_module(module=acv_exploitation_only)
    project_orchestrator.add_module(module=infinite_power_generator)
    project_orchestrator.add_module(module=simplified_wall_losses)
    project_orchestrator.add_module(module=thermal_space_simplified)
    project_orchestrator.add_module(module=occupants)
    project_orchestrator.add_module(module=weather)

    project_orchestrator.create_links_automatically()

    project_orchestrator.run()

    pass



def merge_dicts_recursive(dict1, dict2):
    result = dict1.copy()  # Start with a copy of dict1
    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = merge_dicts_recursive(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                # Append lists
                result[key].extend(value)
            else:
                # Replace non-list, non-dict values with value from dict2
                result[key] = value
        else:
            # If the key is not in dict1, add it
            result[key] = value
    return result