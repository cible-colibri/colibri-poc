"""
Tests for the `class_utils.py` module.
"""

import pytest

from colibri.modules import AcvExploitationOnly
from colibri.project_objects import Space
from colibri.utils.class_utils import (
    create_class_instance,
    get_class,
)
from colibri.utils.enums_utils import ColibriObjectTypes
from colibri.utils.exceptions_utils import (
    ColibriModuleNotFoundError,
    UnauthorizedColibriModule,
)


def test_create_class_instance() -> None:
    """Test the create_class_instance function."""
    acv: AcvExploitationOnly = create_class_instance(
        class_name="AcvExploitationOnly",
        class_parameters={"name": "model-1"},
        output_type=ColibriObjectTypes.MODEL,
    )
    assert isinstance(acv, AcvExploitationOnly) is True
    assert acv.co2_impact == 0.0
    acv: AcvExploitationOnly = create_class_instance(
        class_name="AcvExploitationOnly",
        class_parameters={"name": "model-1", "co2_impact": 24},
        output_type=ColibriObjectTypes.MODEL,
    )
    assert isinstance(acv, AcvExploitationOnly) is True
    assert acv.co2_impact == 24
    with pytest.raises(Exception) as exception_information:
        _ = create_class_instance(
            class_name="WrongName",
            class_parameters={"name": "model-1"},
            output_type=ColibriObjectTypes.MODEL,
        )
    assert exception_information.typename == ColibriModuleNotFoundError.__name__
    assert str(exception_information.value) == "WrongName is not a valid model."
    with pytest.raises(Exception) as exception_information:
        _ = create_class_instance(
            class_name="CustomModel",
            class_parameters={"name": "model-1"},
            output_type=ColibriObjectTypes.MODEL,
        )
    assert exception_information.typename == UnauthorizedColibriModule.__name__
    assert "not a subclass of the available scheme configuration" in str(
        exception_information.value
    )
    space: Space = create_class_instance(
        class_name="Space",
        class_parameters={"id": "space-1", "label": "kitchen"},
        output_type=ColibriObjectTypes.PROJECT_OBJECT,
    )
    assert isinstance(space, Space) is True


def test_get_class() -> None:
    """Test the get_class function."""
    assert (
        get_class(
            class_name="AcvExploitationOnly",
            output_type=ColibriObjectTypes.MODEL,
        ).__name__
        == "AcvExploitationOnly"
    )
    assert (
        get_class(
            class_name="Layer", output_type=ColibriObjectTypes.PROJECT_OBJECT
        ).__name__
        == "ElementObject"
    )
