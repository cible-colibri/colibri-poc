import time
import numpy as np
import matplotlib.pyplot as plt

from core.project import Project
from models.airflow.AirflowBuilding.airflow_building import AirflowBuilding

from models.thermal.MultizoneBuilding.multizone_building import MultizoneBuilding
from models.thermal.vnat.thermal_model.generic import convergence_plot, print_results, plot_results, store_results

def test_coupled_building(file_name='house_1_1.json', weather_file='725650TYCST.epw'):

    #################################################################################
    #       simulation loop
    #################################################################################
    # Create a project
    project = Project()

    project.iterate = True
    project.n_max_iterations = 10
    project.time_steps = 8760

    multizone_building = MultizoneBuilding("thermal model")
    multizone_building.blind_position = 1 # 1 = open
    multizone_building.case = 0

    project.add(multizone_building)

    airflow_building = AirflowBuilding("air flow model")
    airflow_building.case = 0

    # *** if we want to connect an external controller for the blinds (pilots one variable)
    project.link(multizone_building, "air_temperature_dictionary", airflow_building, "air_temperature_dictionary")
    project.link(airflow_building, "flow_rates", multizone_building , "flow_rates")

    project.run()

    print_results(multizone_building.my_T)
    print(multizone_building.air_temperatures) # all air node temperatures for the current (last) timestep with units and description
    print(multizone_building.air_temperatures_series[-1]) # all air node temperatures of the last timestep (just the values)


