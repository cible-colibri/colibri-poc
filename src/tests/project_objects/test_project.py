"""
Tests for the `project.py` module.
"""

from colibri.interfaces import StructureObject
from colibri.project_objects import Project


def test_project() -> None:
    """Test the Project class"""
    project_1 = Project(
        id="project-1",
        label="Project A",
    )
    assert isinstance(project_1, Project) is True
    assert isinstance(project_1, StructureObject) is True
    assert project_1.label == "Project A"

    project_2 = Project(
        id="project-2",
        label="Project B",
        altitude=450,
    )
    assert isinstance(project_2, Project) is True
    assert isinstance(project_2, StructureObject) is True
    assert project_2.label == "Project B"
    assert project_2.altitude == 450


if __name__ == "__main__":
    test_project()
