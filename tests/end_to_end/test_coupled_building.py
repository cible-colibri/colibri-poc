import os
import pathlib

from core.project import Project
from models.thermal.vnat.aero_peter.matrix_aero import P_Model
from models.thermal.vnat.thermal_model.generic import print_results, plot_results
from models.thermal.vnat.thermal_model.thermal_matrix_model import Th_Model
from models.utility.weather import Weather


def test_coupled_building(file_name='house_1.json', weather_file='725650TYCST.epw'):

    main_dir = pathlib.Path(__file__).parents[2]
    building_path = os.path.join(main_dir, 'models', 'thermal', 'vnat', 'test_cases')
    case = 0
    # bestest case
    if case == 0:  # custom test
        file_name = 'house_1.json'
        weather_file = 'Paris.epw'  # old weather file
        time_zone = 'Europe/Paris'
    else:
        weather_file = 'DRYCOLDTMY.epw'  # old weather file
        # epw_file = '725650TYCST.epw'  # new weather file after update of standard in 2020
        time_zone = 'America/Denver'
        if case >= 900:
            file_name = 'house_bestest_900.json'
        elif case < 900:
            file_name = 'house_bestest_600.json'
    building_file = os.path.join(building_path, file_name)

    # Create a project
    project = Project()

    project.iterate = False
    project.n_max_iterations = 1
    project.time_steps = 8760
    project.verbose = False

    # weather
    weather = Weather("weather")
    weather.weather_file = weather_file
    weather.time_zone = time_zone
    project.add(weather)

    project.add_building_data(building_file)

    # thermal model
    multizone_building = Th_Model("thermal model")
    multizone_building.blind_position = 1 # 1 = open
    multizone_building.case = case
    project.add(multizone_building)
    multizone_building.create_emitters()

    # air flow model
    airflow_building = P_Model("air flow model")
    airflow_building.case = case
    project.add(airflow_building)

    if case == 0:  # Colibri house
        airflow_building.pressure_model = True
    else:  # bestest, no pressure calculation
        airflow_building.pressure_model = False

    # *** if we want to connect an external controller for the blinds (pilots one variable)
    project.link(multizone_building, "air_temperature_dictionary_output", airflow_building, "air_temperature_dictionary_input")
    project.link(airflow_building, "flow_rates_output", multizone_building , "flow_rates_input")


    project.run()

    print_results(multizone_building)
    plot_results(multizone_building, to_plot=True)
    # kitchen_temperatures = [x['kitchen_1'] for x in multizone_building.air_temperature_dictionary_series]
    # import matplotlib.pyplot as plt
    # plt.plot(kitchen_temperatures)
    # plt.show()


