from core.project import Project
from models.thermal.vnat.aero_peter.matrix_aero import P_Model
from models.thermal.vnat.thermal_model.generic import convergence_plot, print_results, plot_results, store_results
from models.thermal.vnat.thermal_model.thermal_matrix_model import Th_Model


def test_coupled_building(file_name='house_1_1.json', weather_file='725650TYCST.epw'):

    #################################################################################
    #       simulation loop
    #################################################################################
    # Create a project
    project = Project()

    project.iterate = True
    project.n_max_iterations = 100
    project.time_steps = 8760
    project.verbose = False


    multizone_building = Th_Model("thermal model")
    multizone_building.blind_position = 1 # 1 = open
    multizone_building.case = 0

    project.add(multizone_building)

    airflow_building = P_Model("air flow model")
    airflow_building.case = 0
    project.add(airflow_building)

    # *** if we want to connect an external controller for the blinds (pilots one variable)
    project.link(multizone_building, "air_temperature_dictionary_output", airflow_building, "air_temperature_dictionary_input")
    project.link(airflow_building, "flow_rates_output", multizone_building , "flow_rates_input")

    project.run()

    print_results(multizone_building)
    # kitchen_temperatures = [x['kitchen_1'] for x in multizone_building.air_temperature_dictionary_series]
    # import matplotlib.pyplot as plt
    # plt.plot(kitchen_temperatures)
    # plt.show()


