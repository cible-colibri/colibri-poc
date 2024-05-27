"""
This file tests the file.py module in dataclasses.
"""

from pathlib import Path

import pytest

from colibri.core.helpers.file import File


@pytest.mark.short_test
def test_file():
    """Test the behavior of File."""
    file = File("file", Path(__file__))
    assert isinstance(file, File)
    assert hasattr(file, "name")
    assert hasattr(file, "path")
    assert hasattr(file, "description")
    assert file.__repr__() == file.__str__()


if __name__ == "__main__":
    test_file()
