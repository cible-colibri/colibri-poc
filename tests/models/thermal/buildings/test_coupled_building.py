import json
import os

from pkg_resources import resource_filename
from core.project import Project
from core.models.airflow.AirflowBuilding.P_Model import P_Model
from core.models.emitters.emitter import Emitter
from core.models.emitters.hydro_emitter import HydroEmitter
from core.models.thermal.DetailedBuilding.generic import print_results, plot_results
from core.models.thermal.DetailedBuilding.Th_Model import Th_Model
from core.models.utility.weather import Weather
from tests.data.bestest_cases import bestest_configs


def test_coupled_building():

    building_path = resource_filename('tests', 'data')
    case = 600
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
    project.n_max_iterations = 3
    project.time_steps = 8760
    project.verbose = False

    # weather
    weather = Weather("weather")
    weather.constant_ground_temperature = 10.
    weather.weather_file = weather_file
    weather.time_zone = time_zone
    project.add(weather)

    #TODO: ça créé la structure de données automatiquement mais pas le type de modélisation (pas Model ou DataClass en fonction du type de modèle thermique utilisé par ex)
    project.add_building_data(building_file)

    # thermal model
    multizone_building = Th_Model("thermal model")
    multizone_building.blind_position = 1 # 1 = open
    multizone_building.case = case
    project.add(multizone_building)

    # air flow model
    airflow_building = P_Model("air flow model")
    airflow_building.case = case
    project.add(airflow_building)

    #TODO: soit on met dans le json la classe des objets, si rien n'est spécifié on utilisé la classe RT par défaut
    project.create_envelop()
    project.create_systems()

    if case == 0:  # Colibri house
        airflow_building.pressure_model = True
    else:  # bestest, no pressure calculation
        airflow_building.pressure_model = False

    # TODO: fichier link avec tout en dur pour faire tout automatiquement
    #  Faire des classes "génériques" pour avoir les entrées fixées par types de classes (Enveloppe thermique, Emetteur hydraulique,
    #  Emetteur direct, Emetteur plancher chauffant, Générateur...): soit scalaire, soit vecteur mais par classe. Entre 2 classes on ne peut pas avoir 2 types de sorties (vecteur/scalaires)
    #  Sous quelle forme faire les liens ? On laisse choisir les modèles ? Pas de dict car peut contenir des variables avec des unités différentes (ou sinon homogène avec un type de variable),
    #  faire plutôt type vecteur
    # *** if we want to connect an external controller for the blinds (pilots one variable)
    project.link(multizone_building, "air_temperature_dictionary_output", airflow_building, "air_temperature_dictionary_input")
    project.link(airflow_building, "flow_rates_output", multizone_building , "flow_rates_input")

    project.run()

    print_results(multizone_building)
    plot_results(multizone_building, to_plot=True)

    #TODO: attention, on peut récupérer des objets à différents endroits, mais ce ne sont pas les "vrais objets" par ex Emitter_list n'est pas mis à jour
    # où trouver les inputs ? Il faudrait aller chercher l'objet d'avant ? la galère... en post pro faut pouvoir y accéder facilement
    emitter = project.get_models_from_class(Emitter)[0]
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all')
    ax1.plot(emitter.phi_radiative_series, label='phi radiative')
    ax1.set_ylabel('Phi radiative [w]')

    if isinstance(emitter, HydroEmitter):
        ax2.plot(emitter.temperature_out_series, label='temperature out')
        ax2.set_ylabel('Temperature out of the emitter [degC]')
        ax2.set_xlabel('h')
    plt.show()

    #TODO: todo avec des questions un peu générales
    # - Comment gérer les liens entre les objets ? Ou plus précisément comment récupérer les objets liés (amont et aval) d'un objet en particulier ?
    # - Comment relier les inputs/outputs ? Avec une fonction dédiée appelée à chaque fois avant les run ? Pour l'instant c'est dans ThModel qu'on impose les temperatures in/out de hydroemitter et la heat_demand -> pas très modulaire
    # - Faire des classes génériques de type "Emitter" pour faciliter les connexions et la récupération des objets. Mais comment détecter les différences de type émetteur hydraulique ou non ?


    # kitchen_temperatures = [x['kitchen_1'] for x in multizone_building.air_temperature_dictionary_series]

    # plt.plot(kitchen_temperatures)
    # plt.show()


