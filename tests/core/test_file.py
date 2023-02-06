# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib
import pytest

# ========================================
# Internal imports
# ========================================

from core.file import File

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================


# ========================================
# Functions
# ========================================

@pytest.mark.short_test
def test_file():
    file = File("file", pathlib.Path(__file__))
    assert isinstance(file, File)
    assert hasattr(file, "name")
    assert hasattr(file, "path")
    assert hasattr(file, "description")
    assert file.__repr__() == file.__str__()


if __name__ == "__main__":
    test_file()
