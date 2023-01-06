from core.project import Project
from models.thermal.duct import Duct


def test_project():
    p = Project()

    d1 = Duct("duct-1")
    d1.get_input("flow").value = 100
    d1.get_input("temperature").value = 20
    p.add(d1)

    d2 = Duct("duct-2")
    d2.get_input("flow").value = 200
    d2.get_input("temperature").value = 30
    p.add(d2)

    p.link("duct-1", "flow", "duct-2", "flow")
    p.link("duct-1", "temperature", "duct-2", "temperature")

    p.run()

