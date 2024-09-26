"""
InfinitePowerGenerator class from Generator interface.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces.modules.generators import Generator
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class InfinitePowerGenerator(Generator):
    """InfinitePowerGenerator class from Generator interface"""

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

    def post_initialize(self) -> None: ...

    def run(self, time_step: int, number_of_iterations: int) -> None:
        for space in self.project_data.spaces:
            emitters = [
                boundary_object
                for boundary in space.boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.type == "emitter"
            ]
            number_of_emitters: int = len(emitters)
            q_needs: float = self.q_needs.get(
                space.label,
                space.q_needs,
            )
            for emitter in emitters:
                self.q_consumed[space.label] = q_needs / (
                    number_of_emitters * emitter.efficiency
                )
                self.q_provided[space.label] = q_needs / number_of_emitters

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...
