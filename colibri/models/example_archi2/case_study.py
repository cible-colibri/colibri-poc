
import numpy as np
from collections import namedtuple

from colibri.core.processing.link import Link
from colibri.core.project import Project
from acv import Acv
from generator_sim import GeneratorSim
from occupants import Occupants
from simplified_wall_losses import SimplifiedWallLosses
from thermal_space import ThermalSpace
from utils import Aggregation, Multiplication, Stack, Summation
from weather import WeatherModel
from infinite_power_generator import InfinitePowerGenerator


# Project

project_1 = Project("project_1")

# Spaces

space_1 = namedtuple("Space1", ["spaceSurface", "spaceHeight", "TconsPresence", "TconsAbsence", "ScenarioPresence"])
space_1.spaceSurface = 50
space_1.spaceHeight = 2.5
space_1.TconsPresence = 20
space_1.TconsAbsence = 17
space_1.ScenarioPresence = [1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]
space_2 = namedtuple("Space2", ["spaceSurface", "spaceHeight", "TconsPresence", "TconsAbsence", "ScenarioPresence"])
space_2.spaceSurface = 30
space_2.spaceHeight = 2.5
space_2.TconsPresence = 20
space_2.TconsAbsence = 17
space_2.ScenarioPresence = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]

# building

Building = namedtuple("building", ["altitude"])
Building.altitude = 250

# Walls

wall_1 = namedtuple("Wall1",  ["U", "S"])
wall_1.U = 1
wall_1.S = 25
wall_2 = namedtuple("Wall2",  ["U", "S"])
wall_2.U = 0.3
wall_2.S = 13
wall_3 = namedtuple("Wall3",  ["U", "S"])
wall_3.U = 0.35
wall_3.S = 15

# Aggregation

multiplication_1 = Multiplication("aggregation_1")
project_1.link(Building, "altitude", multiplication_1, "element")
project_1.add(multiplication_1)

# Weather

weather_model_1 = WeatherModel("WeatherModel")
project_1.link(multiplication_1, "elements", weather_model_1, "altitude")
project_1.add(weather_model_1)

# Stack

stack_1 = Stack("stack_1").add(wall_1, "U").add(wall_2, "U").add(wall_3, "U")
stack_2 = Stack("stack_2").add(wall_1, "S").add(wall_2, "S").add(wall_3, "S")
stack_3 = Stack("stack_3").add(space_1, "Tint").add(space_1, "Tint").add(space_2, "Tint")
stack_4 = Stack("stack_4").add(space_1, "spaceSurface").add(space_2, "spaceSurface")
stack_5 = Stack("stack_5").add(space_1, "spaceHeight").add(space_2, "spaceHeight")

project_1.add(stack_1)
project_1.add(stack_2)
project_1.add(stack_3)
project_1.add(stack_4)
project_1.add(stack_5)

# ThermalSimplified

thermal_simplified_1 = ThermalSpace("ThermalSimplified")
project_1.link(stack_4, "elements", thermal_simplified_1, "spaceSurface")
project_1.link(stack_5, "elements", thermal_simplified_1, "spaceHeight")
project_1.add(thermal_simplified_1)

# SimplifiedWallLosses

simplified_wall_losses_1 = SimplifiedWallLosses("SimplifiedWallLosses")
project_1.link(weather_model_1, "Text", simplified_wall_losses_1, "Text")
project_1.link(stack_1, "elements", simplified_wall_losses_1, "U")
project_1.link(stack_2, "elements", simplified_wall_losses_1, "S")
project_1.link(stack_3, "elements", simplified_wall_losses_1, "Tint")
project_1.add(simplified_wall_losses_1)

# Emitters

elemitter_1 = namedtuple("ElEmitter",  ["efficiency"])
elemitter_1.efficiency = 0.85
elemitter_2 = namedtuple("ElEmitter",  ["efficiency"])
elemitter_2.efficiency = 0.60
elemitter_3 = namedtuple("ElEmitter",  ["efficiency"])
elemitter_3.efficiency = 0.90

# InfinitePowerGenerator

infinite_power_generator_1 = InfinitePowerGenerator("InfinitePowerGenerator")
project_1.add(infinite_power_generator_1)

# Occupants

aggregation_1 = Aggregation("aggregation_1")
occupant_1 = Occupants("OccupantModel")
project_1.add(aggregation_1)
project_1.add(occupant_1)

occupant_1.spaceSurface = np.array([space_1.spaceSurface, space_2.spaceSurface])
occupant_1.TconsAbsence = np.array([space_1.TconsAbsence, space_2.TconsAbsence])
occupant_1.TconsPresence = np.array([space_1.TconsPresence, space_2.TconsPresence])
occupant_1.scenarioPresence = np.array([space_1.ScenarioPresence, space_2.ScenarioPresence])

# Summation

summation_1 = Summation("QconsumedSummation")

# ACV

acv_1 = Acv("ACVExploitationOnlyModel")
link_10 = Link(summation_1, "sum", acv_1, "Qconsumed")

# Run project

project_1.run()
