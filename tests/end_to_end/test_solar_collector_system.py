# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================

from connectors.generics.generic                          import GenericConnector
from connectors.hydronics.fluid_flow                      import FluidFlowConnector
from core.project                                         import Project
from models.hydronics.duct                                import Duct
from models.hydronics.simple_pump                         import SimplePump
from models.solar_thermal_collectors.flat_plate_collector import FlatPlateCollector
from models.utility.simple_weather                        import SimpleWeather

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

def test_collector():

    """
    # Create a project
    project              = Project()
    # Create a weather
    weather              = SimpleWeather("weather_1")
    # Create a flat-plate collector
    flat_plate_collector = FlatPlateCollector("flat_plate_collector_1")
    # Create pipes
    pipe_1               = Pipe("pipe_1")
    pipe_2               = Pipe("pipe_2")
    pipe_3               = Pipe("pipe_3")
    # Create a pump
    pump                 = SimplePump("pump_1")
    # Create connectors
    liquid_flow          = FluidFlowConnector()
    generic_connector    = GenericConnector()
    # Link models
    project.link(weather, flat_plate_collector, generic_connector)
    project.link(pipe_1, pump, FluidFlowConnector)
    project.link(pump, "outlet_flow_rate", pipe_2, "inlet_flow_rate_1")
    project.link(pipe_2, "outlet_flow_rate", flat_plate_collector, "inlet_flow_rate_1")
    project.link(flat_plate_collector, "outlet_flow_rate", pipe_3, "inlet_flow_rate_1")
    # Add models to project
    project.add(weather) \
           .add(pipe_1) \
           .add(pump) \
           .add(pipe_2) \
           .add(flat_plate_collector) \
           .add(pipe_3)
    # project.save_as_json(f"{project.name}.json")
    # Run project
    project.time_steps = 24
    project.n_max_iterations = 200
    project.add_plot("Temperatures_ducts", duct_1, "outlet_temperature")
    project.add_plot("Temperatures_ducts", duct_2, "outlet_temperature")
    project.add_plot("Temperatures_pump", pump_1, "outlet_temperature")
    project.add_plot("Temperatures_storage", storage_tank_1, "outlet_temperature_1")
    project.run()
    """

    """
    class Yeah(object):
        def __init__(self, name):
            self.name = name
        # Gets called when an attribute is accessed
        def __getattribute__(self, item):
            print('__getattribute__ ', item)
            # Calling the super class to avoid recursion
            return super(Yeah, self).__getattribute__(item)
        # Gets called when the item is not found via __getattribute__
        def __getattr__(self, item):
            print('__getattr__ ', item)
            return super(Yeah, self).__setattr__(item, 'orphan')

    y1 = Yeah('yes')
    print(y1.__dict__)
    print(y1.name)
    print(y1.__dict__)
    print(y1.foo)
    print(y1.__dict__)
    print(y1.foo)
    print(y1.__dict__)
    print(y1.goo)
    print(y1.__dict__)
    """


if __name__ == "__main__":
    test_collector()
