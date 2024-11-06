"""
Tests for the `meta_fields_mixin.py` module.
"""

from typing import Any, Dict, Type

import pytest

from colibri.mixins import MetaFieldMixin
from colibri.modules import (
    AcvExploitationOnly,
    LayerWallLosses,
    LimitedGenerator,
    SimplifiedWallLosses,
)
from colibri.project_objects import (
    Boundary,
    Space,
)
from colibri.utils.enums_utils import (
    Roles,
    Units,
)
from colibri.utils.exceptions_utils import AttachmentError


def test_meta_fields_mixin() -> None:
    """Test the MetaFieldMixin class."""

    class NewClass(MetaFieldMixin):
        TYPE: str = "z-field"
        DESCRIPTION: str = "No description"

        def __init__(self):
            super().__init__()
            self.z = self.define_parameter(
                name="z",
                default_value=42,
                description="Z value.",
                format=str,
                min=None,
                max=None,
                unit=Units.UNITLESS,
                attached_to=None,
            )

    new_object: NewClass = NewClass()
    assert new_object.parameters == new_object.get_fields(role=Roles.PARAMETERS)
    assert new_object.to_scheme() == {
        "NewClass": {
            "z": {
                "choices": None,
                "default": 42,
                "description": "Z value.",
                "format": "str",
                "min": None,
                "max": None,
                "unit": "-",
            },
            "description": "No description",
            "type": "z-field",
        },
    }

    class OtherClass(MetaFieldMixin):
        def __init__(self):
            super().__init__()
            self.z = self.define_parameter(
                name="z",
                default_value=42,
                description="Z value.",
                format=str,
                min=None,
                max=None,
                unit=Units.UNITLESS,
                attached_to=None,
                required="some-parameter",
            )

    with pytest.raises(AttachmentError) as exception_information:
        OtherClass()
    assert exception_information.typename == AttachmentError.__name__
    assert (
        str(exception_information.value)
        == "Required parameters are always relative to an attached object."
    )


def test_to_scheme():
    """Test the MetaFieldMixin class's to_scheme function."""
    assert Boundary.to_scheme() == {
        "Boundary": {
            "origin_3d": {
                "choices": None,
                "default": None,
                "description": "Origin (x,y,z) in the absolute reference of the first point of "
                "the first segment of the boundary.It can be used to build the 3D "
                "model without using segment information for rebuilding anything.",
                "format": "Tuple[float, float, float]",
                "max": "inf",
                "min": 0,
                "unit": "m",
            },
            "area": {
                "choices": None,
                "default": None,
                "description": "Area of the boundary.",
                "format": "float",
                "max": "inf",
                "min": 0,
                "unit": "m²",
            },
            "azimuth": {
                "choices": None,
                "default": None,
                "description": "Normal orientation of the side 1 of the boundary.",
                "format": "int",
                "max": 359,
                "min": 0,
                "unit": "°",
            },
            "description": "A boundary is a two-sided plane surface delimiting spaces and/or the "
            "exterior.\n"
            "A boundary can be fictive or concrete (wall, floor, roof...).",
            "id": {
                "choices": None,
                "default": None,
                "description": "Unique identifier (ID) of the boundary.",
                "format": "str",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "label": {
                "choices": None,
                "default": None,
                "description": "Name/label of the boundary (wall), not used as id.",
                "format": "str",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "object_collection": {
                "choices": None,
                "default": [],
                "description": "Collection of objects associated to the boundary (windows, doors, "
                "emitters, inlets, ...).",
                "format": "List[BoundaryObject]",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "segments": {
                "choices": None,
                "default": [],
                "description": "Collection of segments forming the edges of the boundary or in "
                "case of a non 3D description linears of interest for modeling. "
                "Important: coordinates need to be set in CLOCKWISE order "
                "regarding side_1 of the boundary. The coordinates of segments are "
                "set in a 2D plane (boundaries are always planar) with a relative "
                "reference point, where the first point of the boundary is "
                "designated as x:0, y:0. If 3D is not used, the key 'points' is "
                "set to None and only 'length' is used. Examples :[ {'id' : "
                "'arrete_1', 'points' : [[x1,y1],[x2,y2]], 'length' : 10, "
                "'junction' : {'nodes_type' : 'linear_junction','nodes_id' : "
                "'junction_64'} ] Search for 'points', 'length', 'junction' to "
                "know more...",
                "format": "List[Segment]",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "side_1": {
                "choices": None,
                "default": None,
                "description": "Unique identifier (ID) of the space (or 'exterior' or 'ground' if "
                "not connected to a space or a bundary_condition node) onto which "
                "face 1 of the boundary is in contact.",
                "format": "str",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "side_2": {
                "choices": None,
                "default": None,
                "description": "Unique identifier (ID) of the space (or 'exterior' if not "
                "connected to a space) onto which face 2 of the boundary is in "
                "contact",
                "format": "str",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "spaces": {
                "choices": None,
                "default": [],
                "description": "Spaces related to the boundary.",
                "format": "List[Space]",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "tilt": {
                "choices": None,
                "default": None,
                "description": "Inclination of the boundary (wall) relative to the horizontal; 0° "
                ": horizontal facing upwards, 90° : vertical, 180° : horizontal "
                "facing downwards.",
                "format": "int",
                "max": 180,
                "min": 0,
                "unit": "°",
            },
            "type": "boundary",
        },
    }
    assert Space.to_scheme() == {
        "Space": {
            "boundaries": {
                "choices": None,
                "default": [],
                "description": "Boundaries related to the space.",
                "format": "List[Boundary]",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "description": "A space is a continuous volume delimited by boundaries.",
            "id": {
                "choices": None,
                "default": None,
                "description": "Unique identifier (ID) of the space.",
                "format": "str",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "label": {
                "choices": None,
                "default": None,
                "description": "Name/label of the space (room), not used as id.",
                "format": "str",
                "max": None,
                "min": None,
                "unit": "-",
            },
            "type": "space",
        },
    }
    assert LimitedGenerator.to_scheme() == {
        "Archetypes": {
            "Emitter": {
                "category": "BoundaryObject",
                "efficiency": {
                    "choices": None,
                    "default": 0.8,
                    "description": "Efficiency of the emitter.",
                    "format": "float",
                    "max": 1.0,
                    "min": 0.0,
                    "required": None,
                    "unit": "-",
                },
            },
        },
        "Emitter": {
            "category": "BoundaryObject",
            "pn": {
                "choices": None,
                "default": 500.0,
                "description": "Nominal power.",
                "format": "float",
                "max": "inf",
                "min": 0,
                "required": None,
                "unit": "W",
            },
        },
        "Space": {
            "q_needs": {
                "choices": None,
                "default": 0.0,
                "description": "Needs of the space.",
                "format": "float",
                "max": "inf",
                "min": 0,
                "unit": "W",
            },
        },
    }
    assert LayerWallLosses.to_scheme() == {
        "Archetypes": {
            "Layer": {
                "category": "ElementObject",
                "density": {
                    "choices": None,
                    "default": 2500,
                    "description": "Volumetric density of the layer.",
                    "format": "float",
                    "max": 50000,
                    "min": 0.1,
                    "required": None,
                    "unit": "kg/m³",
                },
                "material_type": {
                    "choices": [
                        "concrete",
                        "insulation",
                        "plaster",
                        "wood",
                    ],
                    "default": "concrete",
                    "description": "Material characterization of the layer.",
                    "format": "enum",
                    "max": None,
                    "min": None,
                    "required": None,
                    "unit": "-",
                },
                "specific_heat": {
                    "choices": None,
                    "default": 900,
                    "description": "Specific heat capacity (known as C) of the layer.",
                    "format": "float",
                    "max": 8000,
                    "min": 100,
                    "required": None,
                    "unit": "J/kg",
                },
                "thermal_conductivity": {
                    "choices": None,
                    "default": 1.75,
                    "description": "Thermal conductivity of the layer.",
                    "format": "float",
                    "max": 5,
                    "min": 0.01,
                    "required": None,
                    "unit": "W/(m.K)",
                },
                "thickness": {
                    "choices": None,
                    "default": 0.3,
                    "description": "Thickness of the layer.",
                    "format": "float",
                    "max": 2,
                    "min": 0.001,
                    "required": None,
                    "unit": "m",
                },
            },
        },
        "ElementObject": {
            "Layer": {
                "attached_to": "Boundary",
                "category": "Archetype",
                "layers": {
                    "choices": None,
                    "default": [],
                    "description": "Layers of a boundary.",
                    "format": "List[Layer]",
                    "max": None,
                    "min": None,
                    "required": None,
                    "unit": "-",
                },
            },
        },
        "Project": {
            "exterior_air_temperature": {
                "choices": None,
                "default": None,
                "description": "Outside air temperature.",
                "format": "float",
                "max": 100,
                "min": -100,
                "unit": "°C",
            },
        },
        "Space": {
            "inside_air_temperatures": {
                "choices": None,
                "default": {},
                "description": "Inside air temperature of the spaces.",
                "format": "Dict[str, float]",
                "max": 100,
                "min": -100,
                "unit": "°C",
            },
        },
    }

    assert SimplifiedWallLosses.to_scheme() == {
        "Space": {
            "inside_air_temperatures": {
                "description": "Inside air temperature of the spaces.",
                "format": "Dict[str, float]",
                "min": -100,
                "max": 100,
                "unit": "°C",
                "choices": None,
                "default": {},
            },
            "inside_air_temperature": {
                "description": "Temperature inside space",
                "format": "float",
                "min": 0,
                "max": "inf",
                "unit": "°C",
                "choices": None,
                "default": 19.0,
                "required": None,
            },
        },
        "Project": {
            "exterior_air_temperature": {
                "description": "Outside air temperature.",
                "format": "float",
                "min": -100,
                "max": 100,
                "unit": "°C",
                "choices": None,
                "default": None,
            }
        },
        "Boundary": {
            "u_value": {
                "description": "Thermal conductance.",
                "format": "float",
                "min": 0,
                "max": "inf",
                "unit": "W/(m².K)",
                "choices": None,
                "default": 1.5,
                "required": None,
            }
        },
        "Archetypes": {
            "Boundary": {
                "category": "Boundary",
                "u_value": {
                    "description": "Thermal conductance.",
                    "format": "float",
                    "min": 0,
                    "max": "inf",
                    "unit": "W/(m².K)",
                    "choices": None,
                    "default": 1.5,
                    "required": None,
                },
            }
        },
    }


def test_from_template() -> None:
    """Test the MetaFieldMixin class's from_template function."""
    template: Dict[str, Any] = {
        "project": {
            "id": "project-123",
            "simulation_parameters": {
                "time_steps": 168,
                "verbose": False,
                "iterate_for_convergence": True,
                "maximum_number_of_iterations": 10,
            },
            "module_collection": {},
            "building_land": {},
            "node_collection": {
                "space_collection": {
                    "space-1": {
                        "id": "space-1",
                        "label": "space-1",
                        "q_needs": 75.0,
                    }
                }
            },
            "boundary_collection": {
                "boundary-1": {
                    "id": "boundary-1",
                    "label": "boundary-1",
                    "side_1": "space-1",
                    "side_2": "exterior",
                    "area": None,
                    "azimuth": None,
                    "tilt": None,
                    "origin": None,
                    "segments": [],
                    "object_collection": [
                        {
                            "id": "emitter-1",
                            "type": "Emitter",
                            "type_id": "emitter_archetype_1",
                            "pn": 200,
                        }
                    ],
                }
            },
            "archetype_collection": {
                "Emitter_types": {
                    "emitter_archetype_1": {
                        "efficiency": 0.9,
                    },
                }
            },
        }
    }
    limited_generator: LimitedGenerator = LimitedGenerator.from_template(
        template=template
    )
    limited_generator.initialize()
    limited_generator.run(time_step=1, number_of_iterations=1)
    limited_generator.end_time_step(time_step=1)
    limited_generator.end_iteration(time_step=1)
    limited_generator.end_simulation()
    assert limited_generator.q_provided == {"space-1": 75.0}
    assert limited_generator.q_consumed["space-1"] == pytest.approx(
        83.3, abs=0.5
    )


if __name__ == "__main__":
    test_meta_fields_mixin()
    test_to_scheme()
    test_from_template()
