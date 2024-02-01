# -*- coding: utf-8 -*-
import time
import numpy as np
import matplotlib.pyplot as plt

from core.project import Project
from models.thermal.DetailedBuilding.detailed_building import DetailedBuilding
from models.thermal.vnat.thermal_model.generic import convergence_plot, print_results, plot_results, store_results

def test_detailed_building(file_name='house_1_1.json', weather_file='725650TYCST.epw'):

    #################################################################################
    #       simulation loop
    #################################################################################
    # Save starting time
    starting_time = time.perf_counter()
    # Create a project
    project = Project()

    project.iterate = False
    project.n_max_iterations = 1
    project.time_steps = 8760

    detailed_building = DetailedBuilding("Chez Peter")
    detailed_building.blind_position = 1 # 1 = open
    detailed_building.case = 0

    project.add(detailed_building)

    # *** if we want to connect an external controller for the blinds (pilots one variable)
    # blind_controller = BlindController("always open")
    # project.link(blind_controller, "blind_position", detailed_building, "blind_position")

    # *** if we want to connect a heat pump (automatically connects all variables defibned by the backbone for Generators
    # heat_pump = HeatPump("amazing new heat pump")
    # project.link(heat_pump, detailed_building, GeneratorConnector)

    project.run()

    print_results(detailed_building.my_T)
    print(detailed_building.air_temperatures) # all air node temperatures for the current (last) timestep with units and description
    print(detailed_building.air_temperatures_series[-1]) # all air node temperatures of the last timestep (just the values)


