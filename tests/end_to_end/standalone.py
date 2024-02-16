from core.project import Project
from models.airflow.AirflowBuilding.airflow_building import AirflowBuilding
from models.thermal.MultizoneBuilding.multizone_building import MultizoneBuilding
from models.thermal.vnat.thermal_model.generic import print_results

file_name='house_1_1.json'
weather_file='725650TYCST.epw'

#################################################################################
#       simulation loop
#################################################################################
# Create a project
project = Project()

project.iterate = True
project.n_max_iterations = 10
project.time_steps = 8760
project.verbose = False


multizone_building = MultizoneBuilding("thermal model")
multizone_building.blind_position = 1 # 1 = open
multizone_building.case = 0

project.add(multizone_building)

airflow_building = AirflowBuilding("air flow model")
airflow_building.case = 0
project.add(airflow_building)

# *** if we want to connect an external controller for the blinds (pilots one variable)
project.link(multizone_building, "air_temperature_dictionary", airflow_building, "air_temperature_dictionary")
project.link(airflow_building, "flow_rates", multizone_building , "flow_rates")

project.run()

print_results(multizone_building.my_T)
# kitchen_temperatures = [x['kitchen_1'] for x in multizone_building.air_temperature_dictionary_series]
# import matplotlib.pyplot as plt
# plt.plot(kitchen_temperatures)
# plt.show()


