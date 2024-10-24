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
                    default_value=0.9,
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

    def initialize(self) -> None: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for space in self.project_data.spaces:
            emitters: list = [
                boundary_object
                for boundary in space.boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.type == "emitter"
            ]
            max_q: float = sum([emitter.pn for emitter in emitters])
            q_needs: float = self.q_needs.get(
                space.label,
                space.q_needs,
            )
            q_total_provided: float = min(max_q, q_needs)
            for emitter in emitters:
                self.q_consumed[space.label] = q_total_provided / (
                    (emitter.pn / max_q) * emitter.efficiency
                )
                self.q_provided[space.label] = q_total_provided / (
                    emitter.pn / max_q
                )

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True


if __name__ == "__main__":
    import json

    limited_generator: LimitedGenerator = LimitedGenerator(
        name="limited-generator-1"
    )
    print(f"{limited_generator = }")
    print(f"{limited_generator.inputs = }")
    print(f"{limited_generator.outputs = }")
    print(f"{limited_generator.parameters = }")
    print(f"{LimitedGenerator.to_scheme() = }")
    print(json.dumps(LimitedGenerator.to_scheme(), indent=2))
