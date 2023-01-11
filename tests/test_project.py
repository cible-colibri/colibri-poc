import json
from connectors.thermal.flow import LiquidFlowConnector
from core.project import Project
from models.thermal.duct import Duct
from models.thermal.storage_tank import StorageTank
from utils.noncyclyc_encoder import NonCyclycEncoder


def test_project():
    p = Project()

    d1 = Duct("duct-1")
    d1.get_input("Inlet flow").value = 100
    d1.get_input("Inlet temperature").value = 20
    # or:
    #d1.inlet_temperature = 20
    p.add(d1)

    d2 = Duct("duct-2")
    p.add(d2)

    #p.link("duct-1", "flow", "duct-2", "flow")
    #p.link("duct-1", "temperature", "duct-2", "temperature")
    # or:
    liquid_flow = LiquidFlowConnector()
    p.link("duct-1", "duct-2", liquid_flow)

    st = StorageTank("storage tank-1")
    st.set("Number of thermostats", 2) # expands variable list to 2:
    st.set("Height fraction of thermostat-1", 0.0)
    st.get_input("Height fraction of thermostat-2").value = 0.5
    p.add(st)

    p.link("duct-2", "flow", "storage tank-1", "Inlet temperature for port-1")
    s = json.dumps(p, cls=NonCyclycEncoder, check_circular=False, indent=2)
    p.run()

