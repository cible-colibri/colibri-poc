from typing import List

from colibri import AcvExploitationOnly, LimitedGenerator


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


    acv: AcvExploitationOnly = AcvExploitationOnly(
        name="acv-1",
        q_consumed={"kitchen": 350},
        co2_impact=25.0,
    )
    lg : LimitedGenerator = LimitedGenerator("lg-1")
    occupant_model : OccupantModel = OccupantModel(name="occupants")
    simplified_wall_losses: SimplifiedWallLosses = SimplifiedWallLosses(name="simplified_wall_losses")
    thermal_space_simplified : ThermalSpaceSimplified = ThermalSpaceSimplified("thermal_space_simplified")
    weather : WeatherModel = WeatherModel(name="weather")


    module_collection: List[Module] = [acv, occupant_model, lg, simplified_wall_losses, thermal_space_simplified, weather]

    template = {}
    for module in module_collection:
        module_template = module.to_template()
        template = merge_dicts_recursive(template, module_template)
        pass

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