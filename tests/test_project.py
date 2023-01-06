from connectors.thermal.flow import LiquidFlowConnector
from core.project import Project
from models.thermal.duct import Duct


def test_project():
    p = Project()

    d1 = Duct("duct-1")
    d1.get_input("Inlet flow").value = 100
    d1.get_input("Inlet temperature").value = 20
    p.add(d1)

    d2 = Duct("duct-2")
    p.add(d2)

    #p.link("duct-1", "flow", "duct-2", "flow")
    #p.link("duct-1", "temperature", "duct-2", "temperature")
    # or:

    liquid_flow = LiquidFlowConnector()
    p.link("duct-1", "duct-2", liquid_flow)

    p.run()

