"""
Tests for the `exceptions_utils.py` module.
"""

import pytest

from colibri.utils.enums_utils import ErrorMessages
from colibri.utils.exceptions_utils import (
    AttachmentError,
)


def test_exception_classes() -> None:
    """Test the exceptions."""

    def foo():
        raise AttachmentError("foo...")

    def bar():
        raise AttachmentError()

    with pytest.raises(AttachmentError) as exception_information:
        foo()
    assert exception_information.typename == AttachmentError.__name__
    assert "foo..." in str(exception_information.value)

    with pytest.raises(AttachmentError) as exception_information:
        bar()
    assert exception_information.typename == AttachmentError.__name__
    assert (
        str(exception_information.value) == ErrorMessages.ATTACHMENT_ERROR.value
    )
