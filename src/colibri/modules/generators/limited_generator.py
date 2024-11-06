"""
LimitedGenerator class from Generator interface.
"""

from __future__ import annotations

from typing import Dict, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces.modules.generators import Generator
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class LimitedGenerator(Generator):
    """LimitedGenerator class from Generator interface"""

    def __init__(
        self,
        name: str,
        q_needs: Optional[Dict[str, float]] = None,
        q_provided: Optional[Dict[str, float]] = None,
        q_consumed: Optional[Dict[str, float]] = None,
        project_data: Optional[ProjectData] = None,
    ):
        if q_needs is None:
            q_needs: Dict[str, float] = dict()
        if q_provided is None:
            q_provided: Dict[str, float] = dict()
        if q_consumed is None:
            q_consumed: Dict[str, float] = dict()
        super().__init__(
            name=name,
            q_needs=q_needs,
            q_provided=q_provided,
            q_consumed=q_consumed,
        )
        self.project_data = self.define_parameter(
            name="project_data",
            default_value=project_data,
            description="Project data.",
            format=ProjectData,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=[
                Parameter(
                    name="pn",
                    default_value=500.0,
                    description="Nominal power.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY_OBJECT,
                        class_name="Emitter",
                        from_archetype=False,
                    ),
                ),
                Parameter(
                    name="efficiency",
                    default_value=0.8,
                    description="Efficiency of the emitter.",
                    format=float,
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY_OBJECT,
                        class_name="Emitter",
                        from_archetype=True,
                    ),
                ),
            ],
        )

    def initialize(self) -> bool: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for space in self.project_data.spaces:
            emitters: list = [
                boundary_object
                for boundary in space.boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.type.lower() == "emitter"
            ]
            max_q: float = sum([emitter.pn for emitter in emitters])
            q_needs: float = self.q_needs.get(
                space.id,
                space.q_needs,
            )
            q_total_provided: float = min(max_q, q_needs)
            for emitter in emitters:
                self.q_consumed[space.id] = q_total_provided / (
                    (emitter.pn / max_q) * emitter.efficiency
                )
                self.q_provided[space.id] = q_total_provided / (
                    emitter.pn / max_q
                )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True


if __name__ == "__main__":
    from typing import Any

    limited_generator: LimitedGenerator = LimitedGenerator(
        name="limited-generator-1"
    )
    template: Dict[str, Any] = LimitedGenerator.to_template()
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
    limited_generator_2: LimitedGenerator = LimitedGenerator.from_template(
        template=template
    )
    limited_generator_2.initialize()
    limited_generator_2.run(time_step=1, number_of_iterations=1)
    limited_generator_2.end_time_step(time_step=1)
    limited_generator_2.end_iteration(time_step=1)
    limited_generator_2.end_simulation()
    print(limited_generator_2.q_provided)
    print(limited_generator_2.q_consumed)
