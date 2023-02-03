# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib

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

def test_file():
    # Create file
    file = File("file", pathlib.Path(__file__))
    # Test file
    assert isinstance(file, File)
    assert hasattr(file, "name")
    assert hasattr(file, "path")
    assert hasattr(file, "description")
    assert file.__repr__() == file.__str__()


if __name__ == "__main__":
    test_file()
