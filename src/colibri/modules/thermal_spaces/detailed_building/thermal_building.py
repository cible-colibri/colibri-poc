"""
ThermalBuilding class from Building interface.
"""

from typing import Any, Dict, List, Optional, Tuple

import ephem
import numpy as np
import pandas as pd
import pvlib
from numpy import ndarray
from pandas import DatetimeIndex, Series

from colibri.core import ProjectData
from colibri.core.fields import Parameter
from colibri.interfaces import Building, ElementObject
from colibri.modules.modules_constants import CP_AIR, DENSITY_AIR
from colibri.modules.thermal_spaces.detailed_building.controls import (
    compute_ventilation_losses,
    get_operation_mode,
    space_temperature_control_simple,
)
from colibri.modules.thermal_spaces.detailed_building.rycj import (
    generate_euler_exponential_system_and_control_matrices,
    generate_system_and_control_matrices,
    get_states_from_index,
    run_state_space,
    set_boundary_discretization_properties,
    set_input_signals_from_index,
    set_radiative_shares,
    set_u_values,
)
from colibri.utils.colibri_utils import Attachment
from colibri.utils.enums_utils import (
    ColibriProjectObjects,
    Units,
)


class ThermalBuilding(Building):
    def __init__(
        self,
        name: str,
        blind_position: float = 1.0,
        sky_temperatures: Series = None,
        exterior_air_temperatures: Series = None,
        direct_radiations: Series = None,
        diffuse_radiations: Series = None,
        project_data: Optional[ProjectData] = None,
    ) -> None:
        super().__init__(
            name=name,
            blind_position=blind_position,
            sky_temperatures=sky_temperatures,
            exterior_air_temperatures=exterior_air_temperatures,
            direct_radiations=direct_radiations,
            diffuse_radiations=diffuse_radiations,
        )
        self.name = name
        # TODO: Associate to the project (time_step) instead of module?
        self.time_step = self.define_parameter(
            name="time_step",
            default_value=3_600,
            description="Time step for the simulation.",
            format=float,
            min=0,
            max=float("inf"),
            unit=Units.SECOND,
            attached_to=None,
            required=None,
        )
        self.radiative_share_sensor = self.define_parameter(
            name="radiative_share_sensor",
            default_value=0,
            description="Radiative share between Tair and Tmr "
            "for operative temperature control: 0 = Tair, 1 = Tmr.",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.f_sky = self.define_parameter(
            name="f_sky",
            default_value=0.5,
            description="Coefficient to connect the mean radiant temperature "
            "(Tmr) around the building.\n"
            "If f_sky = 0, then Tmr = Tair, "
            "if f_sky = 1, then Tmr = Fsky.",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.radiative_share_internal_gains = self.define_parameter(
            name="radiative_share_internal_gains",
            default_value=0.6,
            description="Radiative share for internal gains.",
            format=float,
            min=0,
            max=1,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.maximum_number_of_iterations = self.define_parameter(
            name="maximum_number_of_iterations",
            default_value=3,
            description="Maximum number of iteration.",
            format=int,
            min=0,
            max=10_000,
            unit=Units.UNITLESS,
            attached_to=None,
            required=None,
        )
        self.project_data = self.define_parameter(
            name="project_data",
            default_value=project_data,
            description="Project data.",
            format=ProjectData,
            min=None,
            max=None,
            unit=Units.UNITLESS,
            attached_to=None,
            required=[
                # Space
                Parameter(
                    name="setpoint_heating",
                    default_value=19.0,
                    description="Heating set-point temperature of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="setpoint_cooling",
                    default_value=26.0,
                    description="Cooling set-point temperature of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="occupant_gains",
                    default_value=200.0,
                    description="Gain generated by a single occupant.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="air_change_rate",
                    default_value=0.41,
                    description="Air change rate (ACH) of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="heating_set_point",
                    default_value=20.0,
                    description="Heating set point temperature of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                Parameter(
                    name="cooling_set_point",
                    default_value=27.0,
                    description="Cooling set point temperature of the space.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.DEGREE_CELSIUS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                # TODO: Make format an enum?
                Parameter(
                    name="operating_modes",
                    default_value=["heating", "cooling"],
                    description="Operating modes of the space.",
                    format=List[str],
                    min=None,
                    max=None,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.SPACE,
                    ),
                ),
                # Boundary
                Parameter(
                    name="u_value",
                    default_value=0.0,
                    description="Thermal conductance of the boundary.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.BOUNDARY,
                        from_archetype=True,
                    ),
                ),
                # Windows
                Parameter(
                    name="area",
                    default_value=0.0,
                    description="Surface area of the window.",
                    format=float,
                    min=0,
                    max=float("inf"),
                    unit=Units.SQUARE_METER,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
                Parameter(
                    name="transmittance",
                    default_value=0.7475 * (1 - 0.035),
                    description="Transmittance of the window.",
                    format=float,
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
                Parameter(
                    name="emissivities",
                    default_value=[0.85, 0.85],
                    description="Emissivity of each layer of the window.",
                    format=List[float],
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
                Parameter(
                    name="absorption",
                    default_value=0.08,
                    description="Absorption of the window.",
                    format=float,
                    min=0.0,
                    max=1.0,
                    unit=Units.UNITLESS,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
                Parameter(
                    name="u_value",
                    default_value=3.0,
                    description="Thermal conductance of the window.",
                    format=float,
                    min=0.0,
                    max=float("inf"),
                    unit=Units.WATT_PER_SQUARE_METER_PER_KELVIN,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Window",
                    ),
                ),
                # Emitters
                Parameter(
                    name="nominal_heating_power",
                    default_value=10_000.0,
                    description="Nominal heating power of the emitter.",
                    format=float,
                    min=0.0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Emitter",
                    ),
                ),
                Parameter(
                    name="nominal_cooling_power",
                    default_value=10_000.0,
                    description="Nominal cooling power of the emitter.",
                    format=float,
                    min=0.0,
                    max=float("inf"),
                    unit=Units.WATT,
                    attached_to=Attachment(
                        category=ColibriProjectObjects.ELEMENT_OBJECT,
                        class_name="Emitter",
                    ),
                ),
            ],
        )
        # TODO: A definir ou pas ?
        self.number_of_simulation_steps = None
        self.heating_setpoints = None
        self.cooling_setpoints = None
        self.operating_modes = None
        self.air_temperatures = None
        self.operating_mode = None
        self.setpoints = None
        self.index_states = None
        self.index_inputs = None
        self.system_matrix_exponential = None
        self.control_matrix_exponential = None
        self.states = None
        self.previous_states = None
        self._has_module_converged = False
        self.ventilation_gains = None
        # TODO: See how to get those? Module parameters?
        self.latitude = 47.73
        self.longitude = 2.4
        self.time_zone = "Europe/Paris"

    def initialize(self) -> bool:
        # Sky temperatures and exterior air temperatures come
        # from another module, so as long as they are None,
        # this module is not initialized (return False)
        if (
            (self.sky_temperatures is None)
            or (self.exterior_air_temperatures is None)
            or (self.direct_radiations is None)
            or (self.diffuse_radiations is None)
        ):
            return False
        # Simulation parameters
        # TODO: Should the number_of_steps be retrieved differently
        #       (from projet level)?
        self.number_of_simulation_steps: int = len(self.sky_temperatures)
        # Create thermal building model
        self._initialize_thermal_model()
        self.initialize_system_parameters()
        # Control parameters
        number_of_spaces: int = len(self.project_data.spaces)
        self.heating_setpoints = np.zeros(number_of_spaces)
        self.cooling_setpoints = np.zeros(number_of_spaces)
        self.operating_modes: List[str] = []
        for space_index, space in enumerate(self.project_data.spaces):
            self.heating_setpoints[space_index] = space.heating_set_point
            self.cooling_setpoints[space_index] = space.cooling_set_point
            self.operating_modes += space.operating_modes
        self.operating_modes = np.unique(self.operating_modes)
        # Initialize outputs
        self.emitters_radiative_gains = np.zeros(number_of_spaces)
        self.emitters_convective_gains = np.zeros(number_of_spaces)
        self.emitters_latent_gains = np.zeros(number_of_spaces)
        self.heat_fluxes = np.zeros(number_of_spaces)
        return True

    def run(self, time_step: int, number_of_iterations: int) -> None:
        # Control modes
        if number_of_iterations == 1:
            # Compute operation mode based on the results of the last time step
            self.air_temperatures = get_states_from_index(
                states=self.states,
                index_states=self.index_states,
                label="spaces_air",
            )
            self.operating_mode, self.setpoints = get_operation_mode(
                indoor_temperatures=self.air_temperatures,
                outdoor_temperature=self.my_weather.rolling_external_temperature[
                    time_step
                ],
                heating_setpoints=self.setpoint_heating_vec,
                cooling_setpoints=self.setpoint_cooling_vec,
                operating_modes=self.operating_modes,
            )
            # Reset parameters for next time step
            # Set to True at each time step, before iterating
            self._has_module_converged = False
            self.found = []
            # Impose supply temperature from generator based on operating mode
            for index, space in enumerate(self.project_data.spaces):
                emitters: List[ElementObject] = [
                    boundary_object
                    for boundary in space.boundaries
                    for boundary_object in boundary.object_collection
                    if boundary_object.__class__.__name__ == "Emitter"
                ]
                for emitter in emitters:
                    # TODO: Créer un paramètre hydraulique.
                    #       Est-ce que c'est à faire ici ce truc ?
                    is_hydro_emitter: bool = emitter.type == "HydroEmitter"
                    is_cooling_mode: bool = (
                        self.operating_mode[index] == "cooling"
                    )
                    is_heating_mode: bool = (
                        self.operating_mode[index] == "heating"
                    )
                    # TODO: last, pas last ? Pas initialisé en tout cas
                    inlet_temperature: float = emitter.temperature_out
                    if is_hydro_emitter and is_cooling_mode:
                        inlet_temperature = (
                            emitter.nominal_cooling_supply_temperature
                        )
                    if is_hydro_emitter and is_heating_mode:
                        inlet_temperature = (
                            emitter.nominal_heating_supply_temperature
                        )
                    emitter.temperature_in = inlet_temperature
        # Thermal model one at each time step, not in iteration
        self.compute_thermal_building_module_iteration(time_step=time_step)
        self.compute_convergence_flag(threshold=1e-1)
        # for convergence plotting
        self.found.append(np.sum(self.hvac_flux_vec))
        self.store_space_temperatures_in_building()

    def end_iteration(self, time_step: int) -> None: ...

    def end_time_step(self, time_step: int) -> None: ...

    def end_simulation(self) -> None: ...

    def has_converged(self, time_step: int, number_of_iterations: int) -> bool:
        return True

    def _initialize_thermal_model(self) -> None:
        # Number of boundaries and spaces
        number_of_spaces: int = len(self.project_data.spaces)
        # TODO: Can we add that to project_data? Make it a function here?
        for boundary_index, boundary in enumerate(self.project_data.boundaries):
            windows: List[BoundaryObject] = [
                boundary_object
                for boundary_object in boundary.object_collection
                if boundary_object.__class__.__name__.lower() == "window"
            ]
            for window in windows:
                window.side_1 = boundary.side_1
                window.side_2 = boundary.side_2
                window.tilt = boundary.tilt
                window.azimuth = boundary.azimuth
                window.boundary_number = boundary_index
                window.boundary_id = boundary.id
                window.area = window.x_length * window.y_length
        # Set the boundaries' discretization properties
        for boundary in self.project_data.boundaries:
            set_boundary_discretization_properties(boundary=boundary)
        # Function to define radiative shares of wall surfaces inside a thermal zone
        set_radiative_shares(spaces=self.project_data.spaces)
        # Compute the global u-values for final balances of outputs (not for calculation)
        set_u_values(spaces=self.project_data.spaces)
        # Create A (system) and B (control) matrices
        system_matrix, control_matrix, self.index_states, self.index_inputs = (
            generate_system_and_control_matrices(
                spaces=self.project_data.spaces,
                boundaries=self.project_data.boundaries,
            )
        )
        """
        print("\n\n\n")
        print("B")
        for i in range(len(control_matrix)):
            j_mes = ""
            for j in range(len(control_matrix[0])):
                j_value = round(control_matrix[i][j], 2)
                print(f"{j_mes}{j_value}", end='')
                j_mes = ", "
            print()
        print("\n\n\n")
        """
        # Convert matrices to euler exponential
        self.system_matrix_exponential, self.control_matrix_exponential = (
            generate_euler_exponential_system_and_control_matrices(
                system_matrix=system_matrix,
                control_matrix=control_matrix,
                time_step=self.time_step,
                label="None",
            )
        )
        # Initialise several things
        number_of_inputs: int = np.shape(control_matrix)[1]
        number_of_states: int = np.shape(control_matrix)[0]
        input_signals: int = np.zeros(number_of_inputs)
        # States in order: boundary nodes, window nodes, air nodes, mean radiant nodes
        self.states = np.zeros(number_of_states) + 20.0
        # States in order: boundary nodes, window nodes, air nodes, mean radiant nodes
        self.previous_states = np.zeros(number_of_states) + 20.0
        # Generate global dict where results can be saved
        # TODO: Mettre dans la définition de la classe ?
        #       Mais pb connaissance de la taille des vecteurs
        self._initialize_results()
        # Create solar radiation matrix for all boundaries
        (
            self.solar_boundary_arriving_fluxes,
            self.solar_transmitted_fluxes,
        ) = self.solar_processor()
        # Radiative parameters
        self.boundary_absorptions = np.zeros(len(self.project_data.boundaries))
        for boundary_index, boundary in enumerate(self.project_data.boundaries):
            if boundary.side_1 == "exterior":
                self.boundary_absorptions[boundary_index] = (
                    1 - boundary.albedos[0]
                )
            else:
                self.boundary_absorptions[boundary_index] = (
                    1 - boundary.albedos[1]
                )
        # Internal gains
        self.internal_gains = np.zeros(number_of_spaces)
        for space_index, space in enumerate(self.project_data.spaces):
            self.internal_gains[space_index] = space.occupant_gains

    def solar_processor(
        self,
    ):
        number_of_boundaries: int = len(self.project_data.boundaries)
        number_of_spaces: int = len(self.project_data.spaces)
        sun_height, sun_azimuth, weather_index = (
            self.sun_height_azimuth_and_weather_index(
                latitude=self.latitude,
                longitude=self.longitude,
                time_zone=self.time_zone,
            )
        )
        extra_terrestrial: ndarray = pvlib.irradiance.get_extra_radiation(
            datetime_or_doy=weather_index
        ).values
        direct_radiation: ndarray = self.direct_radiations
        diffuse_radiation: ndarray = self.diffuse_radiations
        solar_bound_arriving_flux_matrix: ndarray = np.zeros(
            (number_of_boundaries, self.number_of_simulation_steps)
        )
        solar_transmitted_flux_matrix = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        for boundary_index, boundary in enumerate(self.project_data.boundaries):
            inclination: int = boundary.tilt
            angle: int = boundary.azimuth
            (
                diffuse_radiation_on_plane,
                direct_radiation_on_plane,
                angle_of_incidence,
            ) = radiation_process(
                angle=angle,
                inclination=inclination,
                direct_radiation=direct_radiation,
                diffuse_radiation=diffuse_radiation,
                sun_height=sun_height,
                sun_azimuth=sun_azimuth.flatten(),
                extra_terrestrial=extra_terrestrial,
                albedo=0.2,
            )
            boundary.direct_radiation = direct_radiation_on_plane
            boundary.diffuse_radiation = diffuse_radiation_on_plane
            boundary.angle_of_incidence = angle_of_incidence
            solar_bound_arriving_flux_matrix[boundary_index, :] = (
                direct_radiation_on_plane + diffuse_radiation_on_plane
            )
        for space_index, space in enumerate(self.project_data.spaces):
            pass
            """
            windows: List[ElementObject] = [
                boundary_object
                for boundary in boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.__class__.__name__ == "Window"
            ]
            for window in windows:
                # Search for boundary for tilt and orientation

            for env in space.envelope_list:
                if space.envelope_list[env]["type"] == "window":

                    for bound in Boundary_list:
                        if (
                            bound.label
                            == space.envelope_list[env]["boundary_name"]
                        ):
                            inclination = bound.tilt
                            angle = bound.azimuth
                            (
                                diffuse_radiation_on_plane,
                                direct_radiation_on_plane,
                                angle_of_incidence,
                            ) = radiation_process(
                                angle=angle,
                                inclination=inclination,
                                direct_radiation=direct_radiation,
                                diffuse_radiation=diffuse_radiation,
                                sun_height=sun_height,
                                sun_azimuth=sun_azimuth.flatten(),
                                extra_terrestrial=extra_terrestrial,
                                albedo=0.2,
                            )
                            space.envelope_list[env]["direct_radiation"] = (
                                direct_radiation_on_plane
                            )
                            space.envelope_list[env]["diffuse_radiation"] = (
                                diffuse_radiation_on_plane
                            )
                            space.envelope_list[env]["angle_of_incidence"] = (
                                angle_of_incidence
                            )
                            window_transmission_factor = space.envelope_list[
                                env
                            ]["transmittance"]

                            # transmission through windows from dimosim
                            transmission_coeff = np.clip(
                                (
                                    (1.0 - (angle_of_incidence / 90.0) ** 5)
                                    * window_transmission_factor
                                ),
                                0.0,
                                1.0,
                            )
                            direct_transmission = (
                                transmission_coeff * direct_radiation_on_plane
                            )
                            diffuse_transmission = (
                                0.894
                                * window_transmission_factor
                                * diffuse_radiation_on_plane
                            )  # [Brau88]
                            solar_transmitted_flux_matrix[i, :] += (
                                direct_transmission + diffuse_transmission
                            ) * space.envelope_list[env]["area"]
            i += 1
            """
        return solar_bound_arriving_flux_matrix, solar_transmitted_flux_matrix

    @staticmethod
    def sun_height_azimuth_and_weather_index(
        latitude: float, longitude: float, time_zone: str = "America/Denver"
    ) -> Tuple[ndarray, ndarray, DatetimeIndex]:
        """Compute the sun height, sun azimuth and the weather index

        Parameters
        ----------
        latitude : float
            Latitude
        longitude : float
            Longitude
        time_zone : str = "America/Denver"
            Time zone

        Returns
        -------
        Tuple[ndarray, ndarray, DatetimeIndex]
            sun_height : ndarray
            sun_azimuth : ndarray
            weather_index : DatetimeIndex

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        start: str = "2018-01-01 00:00"
        end: str = "2018-12-31 23:00"
        weather_index: DatetimeIndex = pd.date_range(
            start=start, end=end, freq="1h", tz=time_zone
        )
        # Position from which the sun is observed
        sun_observer: ephem.Observer = ephem.Observer()
        sun_observer.lon, sun_observer.lat = str(longitude), str(latitude)
        # UTC time in datetime format
        utc_index = weather_index.tz_convert(tz="UTC")
        # Compute the height and azimuth of the sun
        sun: ephem.Sun = ephem.Sun()
        sun_height: ndarray = np.zeros(
            (len(weather_index), 1), dtype=np.float32
        )
        sun_azimuth: ndarray = np.zeros(
            (len(weather_index), 1), dtype=np.float32
        )
        for index, date in enumerate(utc_index):
            sun_observer.date = date
            sun_observer.date += ephem.minute * 30
            sun.compute(sun_observer)
            sun_height[index, 0] = sun.alt * 180.0 / np.pi
            sun_azimuth[index, 0] = sun.az * 180.0 / np.pi
        return sun_height, sun_azimuth, weather_index

    def initialize_system_parameters(self):
        number_of_spaces: int = len(self.project_data.spaces)
        # Heating and cooling system parameters
        self.hvac_flux_vec_last = np.zeros(number_of_spaces)
        self.window_losses = np.zeros(number_of_spaces)
        self.wall_losses = np.zeros(number_of_spaces)
        self.convective_gains_vec = np.zeros(number_of_spaces)
        self.radiative_gains_vec = np.zeros(number_of_spaces)
        self.radiative_share_hvac_vec = np.zeros(number_of_spaces)
        self.convective_internal_gains_vec = np.zeros(number_of_spaces)
        self.radiative_internal_gains_vec = np.zeros(number_of_spaces)
        self.max_heating_power_vec = np.zeros(
            number_of_spaces
        )  # #TODO: update each time step for hydronic
        self.max_cooling_power_vec = np.zeros(
            number_of_spaces
        )  # #TODO: update each time step for hydronic
        # Ventilation parameters
        self.air_change_rate = 0.0
        # Exhaust ventilation, no heat recovery
        self.efficiency_heat_recovery = 0.0
        self.ventilation_gain_multiplier = np.zeros(number_of_spaces)
        for space_index, space in enumerate(self.project_data.spaces):
            emitters: List[ElementObject] = [
                boundary_object
                for boundary in space.boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.__class__.__name__ == "Emitter"
            ]
            if emitters:
                # TODO: Quid si plusieurs émetteurs mais pas du même mode ?
                #       ou pas du même radiative share ?
                #       (ex: poële + plancher chauffant)
                self.radiative_share_hvac_vec[space_index] = emitters[
                    0
                ].radiative_share
                self.max_heating_power_vec[space_index] = emitters[
                    0
                ].nominal_heating_power
                self.max_cooling_power_vec[space_index] = emitters[
                    0
                ].nominal_cooling_power
            self.ventilation_gain_multiplier[space_index] = (
                space.volume * DENSITY_AIR * CP_AIR
            )
            self.air_change_rate += space.air_change_rate

    def compute_convergence_flag(self, threshold: float = 1e-3) -> None:
        """Compute the convergence flag - whether or not the module
        has converged

        Parameters
        ----------
        threshold : float=1e-3
            Convergence threshold

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        self._has_module_converged = (
            np.max(np.abs(self.heat_fluxes - self.previous_heat_fluxes))
            <= threshold
        )

    def compute_thermal_building_module_iteration(self, time_step: int) -> None:
        # Weather data
        exterior_air_temperature: float = self.exterior_air_temperatures[
            time_step
        ]
        sky_temperature: float = self.sky_temperatures[time_step]
        exterior_radiant_temperature: float = (
            exterior_air_temperature * (1 - self.f_sky)
            + sky_temperature * self.f_sky
        )
        ground_temperature: float = self.ground_temperatures[time_step]
        # Set heat fluxes from internal gains and solar transmission
        self.convective_internal_gains = self.internal_gains * (
            1.0 - self.radiative_share_internal_gains
        )
        self.radiative_internal_gains = (
            self.solar_transmitted_fluxes[:, time_step] * self.blind_position
            + self.internal_gains * self.radiative_share_internal_gains
        )
        # TODO: Comment faire pour initialiser plus tôt toutes ces matrices ?
        self.input_signals = np.zeros(self.n_inputs)
        set_input_signals_from_index(
            input_signals=self.input_signals,
            input_signals_indices=self.input_signals_indices,
            label="ground_temperature",
            value_to_set=ground_temperature,
        )
        set_input_signals_from_index(
            input_signals=self.input_signals,
            input_signals_indices=self.input_signals_indices,
            label="exterior_air_temperature",
            value_to_set=exterior_air_temperature,
        )
        set_input_signals_from_index(
            input_signals=self.input_signals,
            input_signals_indices=self.input_signals_indices,
            label="exterior_radiant_temperature",
            value_to_set=exterior_air_temperature,
        )
        set_input_signals_from_index(
            input_signals=self.input_signals,
            input_signals_indices=self.input_signals_indices,
            label="radiative_gain_boundary_external",
            value_to_set=self.solar_bound_arriving_flux_matrix[:, time_step]
            * self.boundary_absorption_array,
        )
        # Ventilation preprocessing
        ventilation_gain_coefficient = (
            self.ventilation_gain_multiplier
            * self.air_change_rate
            * (1.0 - self.efficiency_heat_recovery)
            / 3600.0
        )
        air_temperatures = get_states_from_index(
            states=self.states,
            index_states=self.index_states,
            label="spaces_air",
        )
        # emitter preprocessing
        for space_index, space in enumerate(self.project_data.spaces):
            emitters: List[ElementObject] = [
                boundary_object
                for boundary in space.boundaries
                for boundary_object in boundary.object_collection
                if boundary_object.__class__.__name__ == "Emitter"
            ]
            for emitter in emitters:
                # TODO: Créer un paramètre hydraulique.
                #       Est-ce que c'est à faire ici ce truc ?
                is_hydro_emitter: bool = emitter.type == "HydroEmitter"
                # TODO: suppose ideal
                if is_hydro_emitter is True:
                    thermal_output_max = emitter.nominal_UA * (
                        emitter.temperature_in - air_temperatures[space_index]
                    )
                    self.max_heating_power_vec[space_index] = max(
                        0.0, thermal_output_max
                    )
                    self.max_cooling_power_vec[space_index] = abs(
                        min(0.0, thermal_output_max)
                    )
                else:
                    self.max_heating_power_vec[space_index] = (
                        emitter.nominal_heating_power
                    )
                    self.max_cooling_power_vec[space_index] = (
                        emitter.nominal_cooling_power
                    )
        # space heating control
        self.hvac_flux_vec = space_temperature_control_simple(
            self.op_mode,
            self.setpoint,
            self.Ad,
            self.Bd,
            self.states,
            self.U,
            self.hvac_flux_vec_last,
            self.index_states,
            self.index_inputs,
            self.radiative_share_hvac_vec,
            self.radiative_share_sensor,
            self.max_heating_power_vec,
            self.max_cooling_power_vec,
            self.ventilation_gain_multiplier,
            ventilation_gain_coefficient,
            self.efficiency_heat_recovery,
            self.convective_internal_gains_vec,
            self.radiative_internal_gains_vec,
            self.space_temperatures,
            self.flow_array,
        )

        # now apply the hvac_flux_vec and simulate the building a last time to obtain all results

        # recalculate ventilation losses
        if (
            self.flow_array == 0 or len(self.flow_array) == 0
        ):  # without pressure calculation, only use air change rates for all rooms
            # update coefficient for flow x cp x dT
            air_temperatures = get_states_from_index(
                self.states, self.index_states, "spaces_air"
            )
            self.ventilation_gains = (
                exterior_air_temperature - air_temperatures
            ) * ventilation_gain_coefficient
        else:
            # with flow matrix and airflow calculation
            self.ventilation_gains = compute_ventilation_losses(
                flows=self.flow_array,
                air_temperatures=self.space_temperatures,
                outdoor_temperature=exterior_air_temperature,
                efficiency_heat_recovery=self.efficiency_heat_recovery,
            )

        # set heat flux from controller for "official building simulation"
        self.convective_gains_vec = (
            self.hvac_flux_vec * (1 - self.radiative_share_hvac_vec)
            + self.ventilation_gains
            + self.convective_internal_gains_vec
        )
        set_input_signals_from_index(
            input_signals=self.input_signals,
            input_signals_indices=self.input_signals_indices,
            label="space_convective_gain",
            value_to_set=self.convective_gains_vec,
        )
        self.radiative_gains_vec = (
            self.hvac_flux_vec * self.radiative_share_hvac_vec
            + self.radiative_internal_gains_vec
        )
        set_input_signals_from_index(
            input_signals=self.input_signals,
            input_signals_indices=self.input_signals_indices,
            label="space_radiative_gain",
            value_to_set=self.radiative_gains_vec,
        )
        # apply corrected flux to the model
        self.states = run_state_space(
            system_matrix=self.system_matrix_exponential,
            control_matrix=self.control_matrix_exponential,
            states=self.states,
            input_signals=self.input_signals,
        )
        # for outputs
        self.window_gains = self.solar_transmitted_flux_matrix[:, time_step]
        # TODO: idem voir si dans une classe Space on veut y associer des résultats ou pas, si oui à chaque pas de temps ? en assessment en reprenant l'ensemble des matrices calculees ?

        # for i, space in enumerate(self.Spaces):
        #     self.window_losses[i] = space.u_window * space.window_area * (ext_temperature_operative - air_temperatures[i])
        #     self.wall_losses[i] = space.u_wall * space.wall_area * (ext_temperature_operative - air_temperatures[i])

    def _initialize_results(self, definition: str = "all") -> None:
        # Number of boundaries and spaces
        number_of_boundaries: int = len(self.project_data.boundaries)
        number_of_spaces: int = len(self.project_data.spaces)
        # Generate global dictionary where results can be saved
        self.results: Dict[str, Any] = dict()
        for res in self.index_states.keys():
            self.results[res] = np.zeros(
                (
                    self.index_states[res]["n_elements"],
                    self.number_of_simulation_steps,
                )
            )
        self.results["outdoor_temperatures"] = np.zeros(
            (number_of_boundaries, self.number_of_simulation_steps)
        )
        self.results["ground_temperature"] = np.zeros(
            (1, self.number_of_simulation_steps)
        )
        self.results["solar_direct"] = np.zeros(
            (1, self.number_of_simulation_steps)
        )
        self.results["solar_diffuse"] = np.zeros(
            (1, self.number_of_simulation_steps)
        )
        self.results["hvac_flux_vec"] = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        self.results["setpoint"] = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        self.results["window_losses"] = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        self.results["wall_losses"] = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        self.results["window_gains"] = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        self.results["ventilation_gains"] = np.zeros(
            (number_of_spaces, self.number_of_simulation_steps)
        )
        # Define here which variables you want to save and plot (if empty list, all variables will be saved)
        if definition == "all":
            self.results["results"] = [
                "outdoor_temperatures",
                "ground_temperature",
                "solar_direct",
                "solar_diffuse",
                "hvac_flux_vec",
                "spaces_air",
                "spaces_mean_radiant",
                "windows",
                "boundaries",
                "window_losses",
                "window_gains",
                "wall_losses",
                "ventilation_gains",
            ]
        # Select this one if you only want some of them
        elif definition == "custom":
            self.results["results"] = ["spaces_air"]
        # Turn on this one to check simulation speed without data storage
        else:
            self.results["results"] = []


def radiation_process(
    angle: int,
    inclination: int,
    direct_radiation: ndarray,
    diffuse_radiation: ndarray,
    sun_height: ndarray,
    sun_azimuth: ndarray,
    extra_terrestrial: ndarray,
    albedo: float,
    diffuse_radiation_model: str = "perez",
) -> Tuple[ndarray, ndarray, ndarray]:
    """Compute the diffuse, direct radiation on plane
    and the angle of incidence using the simulators from pvlib for
    radiation processing

    We take into account the influence of shading masks on direct radiation
    mask_on_direct(shading_mask.astype(np.float64)
    sun_height.astype(np.float64)
    sun_azimuth.astype(np.float64))
    direct_radiation = direct_radiation * mask

    We consider the influence of masks on diffuse radiation by applying
    to it a correction factor equal to the percentage of the sky that
    is not shaded, with a formula from Bernard & Bocher (2018)

    In this case the reflection on the other buildings are not considerate
    Be careful, I think there is already a 0.5 factor for the walls,
    that's why there isn't a factor 2
    sky_view = min(1 - 1. / 180. * (sum(np.sin(np.radians(shading_mask)) ** 2) - 180.), 1.)
    diffuse_radiation = diffuse_radiation * sky_view

    Parameters
    ----------
    angle : int
        Angle
    inclination : int
        Inclination
    direct_radiation : ndarray
        Direct radiation
    diffuse_radiation : ndarray
        Diffuse radiation
    sun_height : ndarray
        Sun's height
    sun_azimuth : ndarray
        Sun's azimuth
    extra_terrestrial : ndarray
        Extra terrestrial
    albedo : float
        Albedo
    diffuse_radiation_model : str = "perez"
        Diffuse radiation model

    Returns
    -------
    Tuple[ndarray, ndarray, ndarray]
        diffuse_radiation_on_plane : ndarray
        direct_radiation_on_plane : ndarray
        angle_of_incidence : ndarray

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    # Zenith from the sun height
    zenith: ndarray = 90.0 - sun_height.flatten()
    # Computation of ground direct
    direct_radiation_horizontal: ndarray = direct_radiation * np.sin(
        sun_height.flatten() * np.pi / 180.0
    )
    direct_radiation_horizontal[direct_radiation_horizontal < 0] = 0
    # Computation of ground diffuse
    ground_global: ndarray = diffuse_radiation + direct_radiation_horizontal
    ground_diffuse: ndarray = pvlib.irradiance.get_ground_diffuse(
        surface_tilt=inclination,
        ghi=ground_global,
        albedo=albedo,
    )
    # Computation of sky diffuse on plane
    if diffuse_radiation_model == "perez":
        relative_airmass: ndarray = pvlib.atmosphere.get_relative_airmass(
            zenith=zenith,
            model="kastenyoung1989",
        )
        sky_diffuse_perez: ndarray = pvlib.irradiance.perez(
            surface_tilt=inclination,
            surface_azimuth=angle,
            dhi=diffuse_radiation,
            dni=direct_radiation,
            dni_extra=extra_terrestrial,
            solar_zenith=zenith,
            solar_azimuth=sun_azimuth,
            airmass=relative_airmass,
        )
        sky_diffuse: ndarray = np.where(
            np.isnan(sky_diffuse_perez), 0, sky_diffuse_perez
        )
    # Just in case, there was problem with some Georgios' files
    elif diffuse_radiation_model == "isotropic":
        sky_diffuse_isotropic: ndarray = pvlib.irradiance.isotropic(
            surface_tilt=inclination,
            dhi=diffuse_radiation,
        )
        sky_diffuse: ndarray = sky_diffuse_isotropic
    # Too simple sky model, with no calculation gains
    else:
        raise ValueError(
            f"Invalid value for diffuse_radiation_model: {diffuse_radiation_model}."
        )
    # Angle of incidence calculation
    angle_of_incidence: ndarray = pvlib.irradiance.aoi(
        inclination, angle, zenith, sun_azimuth
    )
    # Computation of total radiation on the surface
    radiation_on_plane: ndarray = pvlib.irradiance.poa_components(
        aoi=angle_of_incidence,
        dni=direct_radiation,
        poa_sky_diffuse=sky_diffuse,
        poa_ground_diffuse=ground_diffuse,
    )
    diffuse_radiation_on_plane: ndarray = radiation_on_plane["poa_diffuse"]
    direct_radiation_on_plane: ndarray = radiation_on_plane["poa_direct"]
    return (
        diffuse_radiation_on_plane,
        direct_radiation_on_plane,
        angle_of_incidence,
    )


if __name__ == "__main__":
    from pandas import DataFrame

    from colibri.core import ProjectData
    from colibri.interfaces import BoundaryObject
    from colibri.project_objects import Boundary, Space

    data: DataFrame = pd.read_csv(
        r"D:\developments\versioned\colibri\colibri\src\colibri\sky_temperatures.csv",
        sep=";",
        names=[
            "sky_temperatures",
            "exterior_air_temperatures",
            "direct_radiations",
            "diffuse_radiations",
        ],
        header=1,
    )
    space_1: Space = Space(
        id="living_room_1",
        label="living-room",
        volume=52.25,
        reference_area=20.9,
        occupant_gains=200,
        air_change_rate=0.41,
        heating_set_point=20.0,
        cooling_set_point=27.0,
        operating_modes=["heating", "cooling"],
    )
    space_2: Space = Space(
        id="kitchen_1",
        label="kitchen",
        volume=23.8,
        reference_area=9.52,
        occupant_gains=200,
        air_change_rate=0.41,
        heating_set_point=20.0,
        cooling_set_point=27.0,
        operating_modes=["heating", "cooling"],
    )
    layer_1: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "beton_1",
            "label": "béton 20cm",
            "thermal_conductivity": 1.75,
            "specific_heat": 0.9,
            "density": 2_500,
            "thickness": 0.2,
            "constitutive_materials": [
                {"share": 1, "constitutive_material_type": "cement"}
            ],
            "lca_impact_properties": None,
            "end_of_life_properties": None,
            "material_type": "concrete",
            "light_reflectance": 0.8,
            "albedo": 0.25,
            "emissivity": 0.92,
            "installation_year": 0.92,
            "service_life": 50,
        },
    )
    layer_2: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "isolant_1",
            "label": "isolant 15cm pour mur verticaux",
            "thermal_conductivity": 0.035,
            "specific_heat": 1.03,
            "density": 25,
            "thickness": 0.15,
            "constitutive_materials": [
                {"share": 1, "constitutive_material_type": "cement"}
            ],
            "lca_impact_properties": None,
            "end_of_life_properties": None,
            "material_type": "insulation",
            "light_reflectance": 0.8,
            "albedo": 0.25,
            "emissivity": 0.92,
            "installation_year": 0.92,
            "service_life": 50,
        },
    )
    layer_3: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "isolant_toiture",
            "label": "isolant 10cm pour toiture",
            "thermal_conductivity": 0.035,
            "specific_heat": 1.03,
            "density": 25,
            "thickness": 0.1,
            "constitutive_materials": [
                {"share": 1, "constitutive_material_type": "cement"}
            ],
            "lca_impact_properties": None,
            "end_of_life_properties": None,
            "material_type": "insulation",
            "light_reflectance": 0.8,
            "albedo": 0.25,
            "emissivity": 0.92,
            "installation_year": 0.92,
            "service_life": 50,
        },
    )
    layer_4: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "isolant_plancher",
            "label": "isolant 5cm pour plancher",
            "thermal_conductivity": 0.035,
            "specific_heat": 1.03,
            "density": 25,
            "thickness": 0.05,
            "constitutive_materials": [
                {"share": 1, "constitutive_material_type": "cement"}
            ],
            "lca_impact_properties": None,
            "end_of_life_properties": None,
            "material_type": "insulation",
            "light_reflectance": 0.8,
            "albedo": 0.25,
            "emissivity": 0.92,
            "installation_year": 0.92,
            "service_life": 50,
        },
    )
    layer_5: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "vide_10",
            "label": "vide 10cm",
            "thermal_conductivity": 0.025,
            "specific_heat": 1,
            "density": 1.293,
            "thickness": 0.1,
            "constitutive_materials": [
                {"share": 1, "constitutive_material_type": "cement"}
            ],
            "lca_impact_properties": None,
            "end_of_life_properties": None,
            "material_type": "insulation",
            "light_reflectance": 0.8,
            "albedo": 0.25,
            "emissivity": 0.92,
            "installation_year": 0.92,
            "service_life": 50,
        },
    )
    layer_6: ElementObject = ElementObject.create_instance(
        class_name="Layer",
        fields={
            "id": "ba_13",
            "label": "BA13",
            "thermal_conductivity": 0.25,
            "specific_heat": 1,
            "density": 850,
            "thickness": 0.013,
            "constitutive_materials": [
                {"share": 1, "constitutive_material_type": "cement"}
            ],
            "lca_impact_properties": None,
            "end_of_life_properties": None,
            "material_type": "plaster",
            "light_reflectance": 0.8,
            "albedo": 0.25,
            "emissivity": 0.92,
            "installation_year": 0.92,
            "service_life": 50,
        },
    )
    layers_1: List[ElementObject] = [layer_2, layer_1]
    layers_2: List[ElementObject] = [layer_1, layer_3]
    layers_3: List[ElementObject] = [layer_4, layer_1]
    layers_4: List[ElementObject] = [layer_5, layer_6, layer_5]
    window_1: BoundaryObject = BoundaryObject(
        id="window_1",
        label="Fenetre 1 vantail",
        type="window",
        type_id="typical_window",
        x_length=0.6,
        y_length=0.8,
        x_relative_position=1.0,
        y_relative_position=1.0,
        z_relative_position=0.0,
        on_side="side_1_to_side_2",
        emissivities=[0.85, 0.85],
        absorption=0.08,
        u_value=3.0,
        transmittance=0.7475 * (1 - 0.035),
    )
    window_2: BoundaryObject = BoundaryObject(
        id="window_2",
        label="Fenetre 1 vantail",
        type="window",
        type_id="typical_window",
        x_length=0.6,
        y_length=0.8,
        x_relative_position=3.0,
        y_relative_position=1.0,
        z_relative_position=0.0,
        on_side="side_1_to_side_2",
        emissivities=[0.85, 0.85],
        absorption=0.08,
        u_value=3.0,
        transmittance=0.7475 * (1 - 0.035),
    )
    window_3: BoundaryObject = BoundaryObject(
        id="window_3",
        label="Fenetre 1 vantail",
        type="window",
        type_id="typical_window",
        x_length=0.6,
        y_length=0.8,
        x_relative_position=4.0,
        y_relative_position=1.0,
        z_relative_position=0.0,
        on_side="side_1_to_side_2",
        emissivities=[0.85, 0.85],
        absorption=0.08,
        u_value=3.0,
        transmittance=0.7475 * (1 - 0.035),
    )
    window_4: BoundaryObject = BoundaryObject(
        id="window_4",
        label="Fenetre 1 vantail",
        type="window",
        type_id="typical_window",
        x_length=0.6,
        y_length=0.8,
        x_relative_position=0.7,
        y_relative_position=1,
        z_relative_position=0.0,
        on_side="side_1_to_side_2",
        emissivities=[0.85, 0.85],
        absorption=0.08,
        u_value=3.0,
        transmittance=0.7475 * (1 - 0.035),
    )
    boundary_1: Boundary = Boundary(
        id="mur_salon_sud_1",
        label="Mur salon sud",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=180,
        tilt=90,
        area=15.0,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
    )
    boundary_2: Boundary = Boundary(
        id="mur_salon_ouest_1",
        label="Mur salon ouest",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=270,
        tilt=90,
        area=9.04,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
        object_collection=[window_1, window_2],
    )
    boundary_3: Boundary = Boundary(
        id="mur_salon_nord_1",
        label="Mur salon nord",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=0,
        tilt=90,
        area=15.0,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
    )
    boundary_4: Boundary = Boundary(
        id="mur_salon_est_1",
        label="Mur salon est",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=90,
        tilt=90,
        area=5.0,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
    )
    boundary_5: Boundary = Boundary(
        id="plancher_salon",
        label="Plancher salon",
        side_1="living_room_1",
        side_2="ground",
        azimuth=0,
        tilt=180,
        area=24.0,
        origin=None,
        segments=None,
        u_value=0.648,
        layers=layers_3,
    )
    boundary_6: Boundary = Boundary(
        id="plafond_salon",
        label="Plafond salon",
        side_1="exterior",
        side_2="living_room_1",
        azimuth=0,
        tilt=0,
        area=24.0,
        origin=None,
        segments=None,
        u_value=0.336,
        layers=layers_2,
    )
    boundary_7: Boundary = Boundary(
        id="mur_salon_cuisine",
        label="Mur salon cuisine",
        side_1="kitchen_1",
        side_2="living_room_1",
        azimuth=90,
        tilt=90,
        area=5.0,
        origin=None,
        segments=None,
        u_value=0.243,
        layers=layers_4,
    )
    boundary_8: Boundary = Boundary(
        id="mur_cuisine_nord_1",
        label="Mur cuisine nord",
        side_1="exterior",
        side_2="kitchen_1",
        azimuth=0,
        tilt=90,
        area=14.52,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
        object_collection=[window_3],
    )
    boundary_9: Boundary = Boundary(
        id="mur_cuisine_est_1",
        label="Mur cuisine est",
        side_1="exterior",
        side_2="kitchen_1",
        azimuth=90,
        tilt=90,
        area=4.52,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
        object_collection=[window_4],
    )
    boundary_10: Boundary = Boundary(
        id="mur_cuisine_sud_1",
        label="Mur cuisine sud",
        side_1="exterior",
        side_2="kitchen_1",
        azimuth=180,
        tilt=90,
        area=15,
        origin=None,
        segments=None,
        u_value=0.227,
        layers=layers_1,
    )
    boundary_11: Boundary = Boundary(
        id="plancher_cuisine",
        label="Plancher cuisine",
        side_1="kitchen_1",
        side_2="ground",
        azimuth=0,
        tilt=180,
        area=12.0,
        origin=None,
        segments=None,
        u_value=0.648,
        layers=layers_3,
    )
    boundary_12: Boundary = Boundary(
        id="plafond_cuisine",
        label="Plafond cuisine",
        side_1="exterior",
        side_2="kitchen_1",
        azimuth=0,
        tilt=0,
        area=12.0,
        origin=None,
        segments=None,
        u_value=0.336,
        layers=layers_2,
    )
    boundaries: List[Boundary] = [
        boundary_1,
        boundary_2,
        boundary_3,
        boundary_4,
        boundary_7,
        boundary_8,
        boundary_9,
        boundary_10,
        boundary_6,
        boundary_5,
        boundary_12,
        boundary_11,
    ]
    space_1.boundaries = [
        boundary_1,
        boundary_2,
        boundary_3,
        boundary_4,
        boundary_5,
        boundary_6,
        boundary_7,
    ]
    space_2.boundaries = [
        boundary_7,
        boundary_8,
        boundary_9,
        boundary_10,
        boundary_11,
        boundary_12,
    ]
    spaces: List[Space] = [space_1, space_2]
    project_data: ProjectData = ProjectData(name="project-data-1", data=None)
    project_data.spaces = spaces
    project_data.boundaries = boundaries
    # TODO: Add that to project_data
    for boundary_index, boundary in enumerate(boundaries):
        windows: List[BoundaryObject] = [
            boundary_object
            for boundary_object in boundary.object_collection
            if boundary_object.type.lower() == "window"
        ]
        for window in windows:
            window.side_1 = boundary.side_1
            window.side_2 = boundary.side_2
            window.tilt = boundary.tilt
            window.azimuth = boundary.azimuth
            window.boundary_number = boundary_index
            window.boundary_id = boundary.id
            window.area = window.x_length * window.y_length
    thermal_building: ThermalBuilding = ThermalBuilding(
        name="thermal-building-1",
        project_data=project_data,
    )
    thermal_building.sky_temperatures = data["sky_temperatures"].to_numpy()
    thermal_building.exterior_air_temperatures = data[
        "exterior_air_temperatures"
    ].to_numpy()
    thermal_building.direct_radiations = data["direct_radiations"].to_numpy()
    thermal_building.diffuse_radiations = data["diffuse_radiations"].to_numpy()
    is_initialized: bool = thermal_building.initialize()
    print(is_initialized)
