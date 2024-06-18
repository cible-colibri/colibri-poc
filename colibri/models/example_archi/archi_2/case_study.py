
import numpy as np
from collections import namedtuple

from colibri.core.project import Project
from acv import Acv
from generator_sim import GeneratorSim
from occupants import Occupants
from simplified_wall_losses import SimplifiedWallLosses
from thermal_space import ThermalSpace
from utils import Aggregation, Summation
from weather import WeatherModel


# Spaces

Space1 = namedtuple("Space1", ["spaceSurface", "spaceHeight", "TconsPresence", "TconsAbsence", "ScenarioPresence"])
Space1.spaceSurface = 50
Space1.spaceHeight = 2.5
Space1.TconsPresence = 20
Space1.TconsAbsence = 17
Space1.ScenarioPresence = [1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]
Space2 = namedtuple("Space2", ["spaceSurface", "spaceHeight", "TconsPresence", "TconsAbsence", "ScenarioPresence"])
Space2.spaceSurface = 30
Space2.spaceHeight = 2.5
Space2.TconsPresence = 20
Space2.TconsAbsence = 17
Space2.ScenarioPresence = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]




wall_1 = namedtuple("Wall",  ["U", "S"])
wall_1.U = 1
wall_1.S = 25
wall_2 = namedtuple("Wall",  ["U", "S"])
wall_2.U = 0.3
wall_2.S = 13
wall_3 = namedtuple("Wall",  ["U", "S"])
wall_3.U = 0.35
wall_3.S = 15


elemitter_1 = namedtuple("ElEmitter",  ["efficiency"])
elemitter_1.efficiency = 0.85
elemitter_2 = namedtuple("ElEmitter",  ["efficiency"])
elemitter_2.efficiency = 0.60
elemitter_3 = namedtuple("ElEmitter",  ["efficiency"])
elemitter_3.efficiency = 0.90


project = Project("project_1")
#project.link(weather, "temperature", building, "ext_temperature")

simplified_wall_losses = SimplifiedWallLosses("wall_losses_1")
#project.link(consumption_summation_1, "sum", acv_1, "Qconsumed")
#project.run()
#print(f"{acv_1.Co2Impact = }")


print("\n")

building_1 = namedtuple("Building", ["altitude"])
building_1.altitude = 250
print("building_1.altitude: ", building_1.altitude)

print("\n")

aggregation_1 = Aggregation("aggregation_1")
aggregation_1.element = building_1.altitude
print("aggregation_1.elements: ", aggregation_1.elements)
aggregation_1.initialize()
aggregation_1.run()
aggregation_1.timestep_done()
aggregation_1.simulation_done()
print("aggregation_1.elements: ", aggregation_1.elements)

print("\n")

weather_1 = WeatherModel("weather_1")
weather_1.altitude = aggregation_1.elements
print("weather_1.Text: ", weather_1.Text)
weather_1.initialize()
weather_1.run()
weather_1.timestep_done()
weather_1.simulation_done()
print("weather_1.Text: ", weather_1.Text)

print("\n")



print("\n")

consumption_summation_1 = Summation("consumption_summation_1")
consumption_summation_1.elements = [3, 4, 2, 1]
print("consumption_summation_1.elements: ", consumption_summation_1.elements)
print("consumption_summation_1.sum: ", consumption_summation_1.sum)
consumption_summation_1.initialize()
consumption_summation_1.run()
consumption_summation_1.timestep_done()
consumption_summation_1.simulation_done()
print("consumption_summation_1.elements: ", consumption_summation_1.elements)
print("consumption_summation_1.sum: ", consumption_summation_1.sum)

print("\n")

acv_1 = Acv("acv_1")
acv_1.Qconsumed = consumption_summation_1.sum.value
print("acv_1.Qconsumed: ", acv_1.Qconsumed)
print("acv_1.Co2Impact: ", acv_1.Co2Impact)
acv_1.initialize()
acv_1.run()
acv_1.timestep_done()
acv_1.simulation_done()
print("acv_1.Qconsumed: ", acv_1.Qconsumed)
print("acv_1.Co2Impact: ", acv_1.Co2Impact)

print("\n")

occupant_1 = Occupants("occupant_1")
occupant_1.spaceSurface = np.array([Space1.spaceSurface, Space2.spaceSurface])
occupant_1.TconsAbsence = np.array([Space1.TconsAbsence, Space2.TconsAbsence])
occupant_1.TconsPresence = np.array([Space1.TconsPresence, Space2.TconsPresence])
occupant_1.scenarioPresence = np.array([Space1.ScenarioPresence, Space2.ScenarioPresence])
print("occupant_1.spaceSurface: ", occupant_1.spaceSurface)
print("occupant_1.TconsAbsence: ", occupant_1.TconsAbsence)
print("occupant_1.TconsPresence): ", occupant_1.TconsPresence)
print("occupant_1.scenarioPresence: ", occupant_1.scenarioPresence)
print("occupant_1.Tcons: ", occupant_1.Tcons)
print("occupant_1.QoccGains: ", occupant_1.QoccGains)
occupant_1.initialize()
occupant_1.run()
occupant_1.timestep_done()
occupant_1.simulation_done()
print("occupant_1.Tcons: ", occupant_1.Tcons)
print("occupant_1.QoccGains: ", occupant_1.QoccGains)
