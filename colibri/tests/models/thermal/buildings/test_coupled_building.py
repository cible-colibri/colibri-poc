import json
import os

from pkg_resources import resource_filename

from colibri.core.processing.building.building_data import BuildingData
from colibri.core.project import Project
from colibri.models.airflow.AirflowBuilding.Airflow_Building import Airflow_Building
from colibri.models.thermal.DetailedBuilding.generic import print_results
from colibri.models.thermal.DetailedBuilding.Thermal_Building import Thermal_Building
from colibri.models.utility.weather import Weather
from colibri.tests.data.bestest_cases import bestest_configs

def test_coupled_building():
    run_test_case(0) # with pressure model
    # run_test_case(50) # with hydraulic network
    # run_test_case(600) # bestest 600
    # run_test_case(900) # bestest 900

def run_test_case(case: int=0):

    building_path = resource_filename('colibri', os.path.join('tests', 'data'))
    # bestest case
    if case == 0:  # custom test
        file_name = 'house_1.json'
        weather_file = 'Paris.epw'  # old weather file
        time_zone = 'Europe/Paris'
    elif case > 100:
        weather_file = 'DRYCOLDTMY.epw'  # old weather file
        # epw_file = '725650TYCST.epw'  # new weather file after update of standard in 2020
        time_zone = 'America/Denver'
        if case >= 900:
            file_name = 'house_bestest_900.json'
        elif case < 900:
            file_name = 'house_bestest_600.json'
    else:
        weather_file = 'DRYCOLDTMY.epw'  # old weather file
        time_zone = 'America/Denver'
        file_name = 'house_hydraulic.json'

    building_file = os.path.join(building_path, file_name)

    # adapt to bestest cases if necessary
    if case > 100:  # Bestest
        with open(building_file, 'r') as f:
            building_file = json.load(f)
        building_file = bestest_configs(building_file, case)

    # Create a project
    project = Project()

    project.iterate = True
    project.n_max_iterations = 100
    project.time_steps = 8760
    project.verbose = False
    project.auto_links = False

    # weather
    weather = Weather("weather")
    weather.constant_ground_temperature = 10.
    weather.weather_file = weather_file
    weather.time_zone = time_zone
    project.add(weather)

    building_data = BuildingData(building_file)
    project.add(building_data)

    # thermal model
    multizone_building = Thermal_Building("thermal model")
    multizone_building.blind_position = 1 # 1 = open
    multizone_building.case = case
    project.add(multizone_building)

    # air flow model
    airflow_building = Airflow_Building("air flow model")
    airflow_building.case = case
    project.add(airflow_building)

    if case == 0:  # Colibri house
        airflow_building.pressure_model = True
    else:  # bestest, no pressure calculation
        airflow_building.pressure_model = False

    project.link(airflow_building, "flow_rates_output", multizone_building , "flow_rates_input")
    project.link(multizone_building, "space_temperatures", airflow_building, "space_temperatures")

    project.link(building_data, "Spaces", multizone_building, "Spaces")
    project.link(building_data, "Emitters", multizone_building, "Emitters")
    project.link(building_data, "Boundaries", multizone_building, "Boundaries")
    project.link(building_data, "Windows", multizone_building, "Windows")

    project.link(building_data, "Spaces", airflow_building, "Spaces")

    project.run()

    print_results(multizone_building)
    print(project.n_iterations)

    # plot_results(multizone_building, to_plot=True)
    #
    # for emitter in  project.get_models_from_class(Emitter):
    #     import matplotlib.pyplot as plt
    #     fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all')
    #     ax1.plot(emitter.phi_radiative_series, label='phi radiative')
    #     ax1.set_ylabel('Phi radiative [w]')
    #
    #     if isinstance(emitter, HydroEmitter):
    #         ax2.plot(emitter.temperature_out_series, label='temperature out')
    #         ax2.set_ylabel('Temperature out of the emitter [degC]')
    #         ax2.set_xlabel('h')
    #     plt.show()



    # kitchen_temperatures = [x['kitchen_1'] for x in multizone_building.air_temperature_dictionary_series]

    # plt.plot(kitchen_temperatures)
    # plt.show()


