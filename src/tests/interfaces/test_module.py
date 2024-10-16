"""
Tests for the `module.py` module.
"""

from colibri.core.fields import Field
from colibri.core.link import Link
from colibri.core.project_orchestrator import ProjectOrchestrator
from colibri.interfaces.module import Module
from colibri.utils.enums_utils import Roles, Units


def test_model() -> None:
    """Test the Module class."""

    class RealModule(Module):
        def __init__(self, name: str):
            super().__init__(name=name)
            self.my_field = self.define_input(
                name="my_field",
                default_value=42,
                description="None so far.",
                format=int,
                min=0,
                max=42,
                unit=Units.UNITLESS,
                attached_to=None,
            )

        def initialize(self) -> bool: ...

        def run(self, time_step: int, number_of_iterations: int) -> None: ...

        def end_iteration(self, time_step: int) -> None: ...

        def end_time_step(self, time_step: int) -> None: ...

        def end_simulation(self) -> None: ...

    model_name_example: str = "model_example"
    model_example: RealModule = RealModule(name=model_name_example)
    assert model_example.project is None
    assert isinstance(model_example._fields_metadata["my_field"], Field) is True
    assert isinstance(model_example.get_fields(), list) is True
    assert isinstance(model_example.get_fields()[0], Field) is True
    assert model_example.get_fields()[0].role is Roles.INPUTS
    assert model_example.get_fields(role=Roles.INPUTS)[0].role is Roles.INPUTS
    assert model_example.get_fields(role=Roles.OUTPUTS) == []
    assert isinstance(model_example.get_field("my_field"), Field) is True
    assert model_example.get_field("wrong-name") is None

    class RealModuleVariant(Module):
        def __init__(self, name: str):
            super().__init__(name=name)
            self.my_input_field = self.define_input(
                name="my_input_field",
                default_value=42,
                description="None so far.",
                format=int,
                min=0,
                max=42,
                unit=Units.UNITLESS,
                attached_to=None,
            )
            self.my_parameter_field = self.define_parameter(
                name="my_parameter_field",
                default_value=42,
                description="None so far.",
                format=int,
                min=0,
                max=42,
                unit=Units.UNITLESS,
                attached_to=None,
            )
            self.my_output_field = self.define_output(
                name="my_output_field",
                default_value=42,
                description="None so far.",
                format=int,
                min=0,
                max=42,
                unit=Units.UNITLESS,
                attached_to=None,
            )

        def initialize(self) -> bool: ...

        def run(self, time_step: int, number_of_iterations: int) -> None: ...

        def end_iteration(self, time_step: int) -> None: ...

        def end_time_step(self, time_step: int) -> None: ...

        def end_simulation(self) -> None: ...

    model_example_variant: RealModuleVariant = RealModuleVariant(
        name="other-name"
    )
    assert model_example_variant.inputs[0].name == "my_input_field"
    assert model_example_variant.parameters[0].name == "my_parameter_field"
    assert model_example_variant.outputs[0].name == "my_output_field"

    assert model_example.is_field_linked(field_name="my_field") is False
    assert model_example.get_link(field_name="my_field") is None
    project_example: ProjectOrchestrator = ProjectOrchestrator("project-1")
    model_example.project = project_example
    assert model_example.is_field_linked(field_name="my_field") is False
    assert model_example.get_link(field_name="my_field") is None
    project_example.add_link(
        model_example_variant,
        "my_output_field",
        model_example,
        "my_field",
    )
    assert model_example.is_field_linked(field_name="my_field") is True
    assert (
        isinstance(model_example.get_link(field_name="my_field"), Link) is True
    )
    project_example.add_module(module=model_example_variant)
    project_example._initialize_module_output_series()
    model_example_variant.my_output_field = 35
    model_example_variant.save_time_step(1)
    assert model_example_variant.my_output_field_series[1] == 35

    model_name_example: str = "model_example"
    model_example: Module = Module(name=model_name_example)
    assert model_example.name == model_name_example
    assert model_example.project is None
    assert model_example._fields_metadata == dict()


if __name__ == "__main__":
    test_model()
