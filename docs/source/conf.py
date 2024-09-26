# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------

# Patch sys.path in your Sphinx conf.py to include the folder of your sources.
sys.path.insert(0, os.path.abspath("../../src"))
print("")
print(sys.path)
print("")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "colibri"
copyright = "2024, colibri-community"
author = "colibri-community"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "numpydoc",  # For numpy docstrings
    "sphinx.ext.autodoc",  # Core Sphinx library for auto html doc generation from docstrings
    "sphinx.ext.autosummary",  # Create neat summary tables for modules/classes/methods etc
]

# Generate autosummary even if no references
# Enable autosummary generation
autosummary_generate = True
# Generate function/method/attribute summary lists,
autosummary_imported_members = True
# Show all members of a class in the Methods and Attributes
numpydoc_show_class_members = False
# show all inherited members of a class
numpydoc_show_inherited_class_members = True
# create a Sphinx table of contents for the lists of class methods and attributes
numpydoc_class_members_toctree = True


templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # requires pip install sphinx-rtd-theme
# html_static_path = ["_static"]
