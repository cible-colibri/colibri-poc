"""
Tests for the `colibri_utils.py` module.
"""

import pytest

from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import ColibriProjectObjects
from colibri.utils.exceptions_utils import AttachmentError


def test_attachment() -> None:
    """Test the Attachment class."""
    attachment_1: Attachment = Attachment(category=ColibriProjectObjects.SPACE)
    assert isinstance(attachment_1, Attachment) is True
    assert attachment_1.category.value == ColibriProjectObjects.SPACE.value
    assert attachment_1.class_name is None
    attachment_2: Attachment = Attachment(
        category=ColibriProjectObjects.BOUNDARY_OBJECT, class_name="Emitter"
    )
    assert isinstance(attachment_2, Attachment) is True
    assert (
        attachment_2.category.value
        == ColibriProjectObjects.BOUNDARY_OBJECT.value
    )
    assert attachment_2.class_name == "Emitter"
    attachment_3: Attachment = Attachment(
        category=ColibriProjectObjects.BOUNDARY_OBJECT, class_name="emitter"
    )
    assert isinstance(attachment_3, Attachment) is True
    assert (
        attachment_3.category.value
        == ColibriProjectObjects.BOUNDARY_OBJECT.value
    )
    assert attachment_3.class_name == "Emitter"
    with pytest.raises(Exception) as exception_information:
        _ = Attachment(category=ColibriProjectObjects.BOUNDARY_OBJECT)
    assert exception_information.typename == AttachmentError.__name__
    assert "Boundary object must have a class name." in str(
        exception_information.value
    )
