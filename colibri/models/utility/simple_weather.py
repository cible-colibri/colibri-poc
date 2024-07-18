# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pandas
import numpy

# ========================================
# Internal imports
# ========================================

from colibri.core.model        import Model
from colibri.core.variables.variable import Variable
from colibri.utils.enums_utils import Units

# ========================================
# Constants
# ========================================

from colibri.config.constants import SOLAR_CONSTANT_OF_THE_EARTH

# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

# Class representing the Weather object
class SimpleWeather(Model):

    # Solar constant of the Earth # [W/m²]
    SOLAR_CONSTANT_OF_THE_EARTH = Variable(SOLAR_CONSTANT_OF_THE_EARTH, 1367.0, Units.WATT_PER_SQUARE_METER, "Solar constant of the Earth")

    def _define_inputs(self) -> list:
        inputs = [
                Variable(
                            name        = "number_of_surfaces",
                            value       = 1,
                            unit        = Units.UNITLESS,
                            description = "Number of surfaces [-]",
                            linked_to   = [
                                                ("outputs", Variable("direct_beam_solar_radiation", 0)),
                                                ("outputs", Variable("sky_diffuse_solar_radiation", 0)),
                                                ("outputs", Variable("reflected_diffuse_solar_radiation")),
                                                ("outputs", Variable("total_incident_solar_radiation")),
                                                ("parameters", Variable("surface_azimuth_angle", 0, unit=Units.DEGREE)),
                                                ("parameters", Variable("surface_tilt_angle", 0, unit= Units.DEGREE)),
                                           ],
                            model       = self,
                         )

        ]
        return inputs

    def _define_outputs(self) -> list:
        outputs = []
        return outputs

    def _define_conditions(self) -> list:
        conditions = []
        return conditions

    def _define_parameters(self) -> list:
        parameters = [
                        Variable("altitude", 100.0, Units.METER, "Altitude (alt) of the place in meters [m]"),
                        Variable("day_numbers", 0, Units.UNITLESS, "Number of days (n) since the beginning of the year [-]"),
                        Variable("ending_day", 365, Units.UNITLESS, "Ending number of days (n_end) since the beginning of the year [-]"),
                        Variable("ground_reflectance", 0.6, Units.UNITLESS, "Ground reflectance (rho) near the place [-]"),
                        Variable("latitude", 45.0, Units.DEGREE, "Latitude (LAT) of the place in degress [°]"),
                        Variable("legal_standard_time", 42.0, Units.HOUR, "Legal standard time (LST) in hours [h], time we see in our watches"),
                        Variable("local_standard_meridian", 75, Units.DEGREE, "Local standard meridian (LSM) in degrees [°], which is the reference meridian used for a particular time zone"),
                        Variable("longitude", 73.0, Units.DEGREE, "Longitude (LON) of the place in degress [°]"),
                        Variable("number_of_time_steps_per_day", 24, Units.UNITLESS, " Number of time steps in a day [-]"),
                        Variable("starting_day", 1, Units.UNITLESS, "Starting number of days (n_start) since the beginning of the year [-]"),
                      ]
        return parameters

    # Initialize the weather (compute all weather variables over the given period)
    def initialize(self) -> None:
        """Initialize the weather (compute all weather variables over the given period)

        Parameters
        ----------

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
        # Compute the number of days (n) since the beginning of the year [-]
        self.day_numbers = [day_number for day_number in range(self.starting_day, self.ending_day + 1, 1) for _ in range(0, self.number_of_time_steps_per_day, 1)]
        # Create a dataframe to store all the weather data
        weather_data = {
                            "day_number":           self.day_numbers,
                            "legal_standard_time":  self.legal_standard_time,
                        }
        weather_data = pandas.DataFrame.from_dict(weather_data)
        self._create_weather_data(weather_data)


    def run(self, time_step: int = 0, n_iteration: int = 0):
        if time_step > 155:
            print("toto")
        for surface_index in range(1, self.number_of_surfaces + 1):
            surface_direct_beam_solar_radiation             = self.get_variable(f"direct_beam_solar_radiation_{surface_index}")
            surface_sky_diffuse_solar_radiation             = self.get_variable(f"sky_diffuse_solar_radiation_{surface_index}")
            surface_reflected_diffuse_solar_radiation       = self.get_variable(f"reflected_diffuse_solar_radiation_{surface_index}")
            surface_total_incident_solar_radiation          = self.get_variable(f"total_incident_solar_radiation_{surface_index}")
            surface_direct_beam_solar_radiation       = self.weather_data.loc[time_step, f"direct_beam_solar_radiation_{surface_index}"]
            surface_sky_diffuse_solar_radiation       = self.weather_data.loc[time_step, f"sky_diffuse_solar_radiation_{surface_index}"]
            surface_reflected_diffuse_solar_radiation = self.weather_data.loc[time_step, f"reflected_diffuse_solar_radiation_{surface_index}"]
            surface_total_incident_solar_radiation    = self.weather_data.loc[time_step, f"total_incident_solar_radiation_{surface_index}"]

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

    # Create a dataframe (named weather_data) with all the main weather data
    def _create_weather_data(self, weather_data: pandas.DataFrame):
        """Create a dataframe (named weather_data) with all the main weather data

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        ValueError
            Raise an error if the number of days (n) is not between 1 and 365 (days)

        Examples
        --------
        >>> None
        """
        weather_data["equation_of_time"]                             = weather_data["day_number"].apply(lambda day_number: self.get_solar_equation_of_time(day_number))
        weather_data["apparent_solar_time"]                          = weather_data.apply(lambda columns: self.get_apparent_solar_time(columns["legal_standard_time"], self.local_standard_meridian, self.longitude, columns["equation_of_time"]), axis = 1)
        weather_data["hour_angle"]                                   = weather_data["apparent_solar_time"].apply(lambda apparent_solar_time: self.get_hour_angle(apparent_solar_time))
        weather_data["declination_angle"]                            = weather_data["day_number"].apply(lambda day_number: self.get_declination_angle(day_number))
        weather_data["solar_altitude_angle"]                         = weather_data.apply(lambda columns: self.get_solar_altitude_angle(self.latitude, columns["declination_angle"], columns["hour_angle"]), axis = 1)
        weather_data["solar_azimuth_angle"]                          = weather_data.apply(lambda columns: self.get_solar_azimuth_angle(self.latitude, columns["declination_angle"], columns["solar_altitude_angle"], columns["hour_angle"]), axis = 1)
        weather_data["solar_zenith_angle"]                           = weather_data["solar_altitude_angle"].apply(lambda solar_altitude_angle: self.get_solar_zenith_angle(solar_altitude_angle))
        weather_data["atmospheric_transmittance_for_beam_radiation"] = weather_data["solar_zenith_angle"].apply(lambda solar_zenith_angle: self.get_atmospheric_transmittance_for_beam_radiation(self.altitude, solar_zenith_angle))
        weather_data["diffuse_atmospheric_transmittance"]            = weather_data["atmospheric_transmittance_for_beam_radiation"].apply(lambda atmospheric_transmittance_for_beam_radiation: self.get_diffuse_atmospheric_transmittance(atmospheric_transmittance_for_beam_radiation))
        weather_data["sun_rise_time"]                                = weather_data["declination_angle"].apply(lambda declination_angle: self.get_sun_rise_time(self.latitude, declination_angle))
        weather_data["sun_set_time"]                                 = weather_data["declination_angle"].apply(lambda declination_angle: self.get_sun_set_time(self.latitude, declination_angle))
        weather_data["extraterrestrial_solar_radiation"]             = weather_data["day_number"].apply(lambda day_number : self.get_extraterrestrial_solar_radiation(day_number))
        weather_data["direct_normal_beam_solar_radiation"]           = weather_data.apply(lambda columns: self.get_direct_normal_beam_solar_radiation(columns["extraterrestrial_solar_radiation"], columns["atmospheric_transmittance_for_beam_radiation"]), axis = 1)
        weather_data["direct_horizontal_beam_solar_radiation"]       = weather_data.apply(lambda columns: self.get_direct_horizontal_beam_solar_radiation(columns["direct_normal_beam_solar_radiation"], columns["solar_altitude_angle"]), axis = 1)
        weather_data["normal_sky_diffuse_solar_radiation"]           = weather_data.apply(lambda columns: self.get_normal_sky_diffuse_solar_radiation(columns["diffuse_atmospheric_transmittance"], columns["solar_altitude_angle"]), axis = 1)
        for surface_index in range(1, self.number_of_surfaces + 1):
            surface_azimuth_angle                                                              = self.get_variable(f"surface_azimuth_angle_{surface_index}")
            surface_tilt_angle                                                                 = self.get_variable(f"surface_tilt_angle_{surface_index}")
            weather_data[f"solar_surface_azimuth_angle_{surface_index}"]                       = weather_data["solar_azimuth_angle"].apply(lambda solar_azimuth_angle: self.get_solar_surface_azimuth_angle(solar_azimuth_angle, surface_azimuth_angle))
            weather_data[f"incidence_angle_{surface_index}"]                                   = weather_data.apply(lambda columns: self.get_incidence_angle(columns["solar_zenith_angle"], surface_tilt_angle, columns[f"solar_surface_azimuth_angle_{surface_index}"]), axis = 1)
            weather_data[f"direct_beam_solar_radiation_{surface_index}"]                       = weather_data.apply(lambda columns: self.get_direct_beam_solar_radiation(columns["direct_normal_beam_solar_radiation"], columns[f"incidence_angle_{surface_index}"], columns["solar_altitude_angle"], surface_tilt_angle), axis = 1)
            weather_data[f"sky_diffuse_solar_radiation_{surface_index}"]                       = weather_data.apply(lambda columns: self.get_sky_diffuse_solar_radiation(columns["normal_sky_diffuse_solar_radiation"], surface_tilt_angle), axis = 1)
            weather_data[f"reflected_diffuse_solar_radiation_{surface_index}"]                 = weather_data.apply(lambda columns: self.get_reflected_diffuse_solar_radiation(columns["direct_horizontal_beam_solar_radiation"], columns["normal_sky_diffuse_solar_radiation"], self.ground_reflectance, surface_tilt_angle), axis = 1)
            condition_no_sun                                                                   = (weather_data.loc[:, "legal_standard_time"] < weather_data.loc[:, "sun_rise_time"]) | (weather_data.loc[:, "legal_standard_time"] > weather_data.loc[:, "sun_set_time"])
            weather_data.loc[condition_no_sun, f"direct_beam_solar_radiation_{surface_index}"] = 0
            weather_data[f"total_incident_solar_radiation_{surface_index}"]                    = weather_data[f"direct_beam_solar_radiation_{surface_index}"] + weather_data[f"sky_diffuse_solar_radiation_{surface_index}"] + weather_data[f"reflected_diffuse_solar_radiation_{surface_index}"]
        self.weather_data = weather_data

    # Get the extraterrestrial solar radiation (Ion) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
    def get_extraterrestrial_solar_radiation(self, day_number: int) -> float:
        """Get the extraterrestrial solar radiation (Ion) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]

        Parameters
        ----------
        day_number : int
            Number of days (n) since the beginning of the year [-]

        Returns
        -------
        extraterrestrial_solar_radiation : float
            Eextraterrestrial solar radiation (Ion) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]

        Raises
        ------
        ValueError
            Raise an error if the number of days (n) is not between 1 and 365 (days)

        Examples
        --------
        >>> None
        """
        if (day_number > 365) or (day_number < 1):
             raise ValueError(f"Sorry, but the day_number (n) should be between 1 and 365 (days)! Given : {day_number}.")
        extraterrestrial_solar_radiation = self.SOLAR_CONSTANT_OF_THE_EARTH * (1 + 0.033 * numpy.cos(2 * numpy.pi * day_number / 365))
        return extraterrestrial_solar_radiation

    # Get the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
    @staticmethod
    def get_direct_normal_beam_solar_radiation(extraterrestrial_solar_radiation: float, atmospheric_transmittance_for_beam_radiation: float) -> float:
        """Get the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]

        Parameters
        ----------
        extraterrestrial_solar_radiation : float
            Eextraterrestrial solar radiation (Ion) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        atmospheric_transmittance_for_beam_radiation : float
            Atmospheric transmittance for beam radiation (tau_b) [-]

        Returns
        -------
        direct_normal_beam_solar_radiation : float
            Direct normal beam solar radiation (Ibn) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]

        Raises
        ------
        ValueError
            Raise an error if the number of days (n) is not between 1 and 365 (days)

        Examples
        --------
        >>> None
        """
        direct_normal_beam_solar_radiation = extraterrestrial_solar_radiation * atmospheric_transmittance_for_beam_radiation
        return direct_normal_beam_solar_radiation

    # Get the direct horizontal bean solar radiation (Ibh) in watts per square meter [W/m²] from the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]
    @staticmethod
    def get_direct_horizontal_beam_solar_radiation(direct_normal_beam_solar_radiation: float, solar_altitude_angle: float) -> float:
        """Get the direct horizontal bean solar radiation (Ibh) in watts per square meter [W/m²] from the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]

        Parameters
        ----------
        direct_normal_beam_solar_radiation : float
            Direct normal beam solar radiation (Ibn) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)

        Returns
        -------
        direct_horizontal_beam_solar_radiation : float
            Direct horizontal beam solar radiation (Ib) in watts per square meter [W/m²] from the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        solar_altitude_angle                   = numpy.deg2rad(solar_altitude_angle)
        direct_horizontal_beam_solar_radiation = direct_normal_beam_solar_radiation * numpy.sin(solar_altitude_angle)
        return direct_horizontal_beam_solar_radiation

    # Get the normal/horizontal sky diffuse solar radiation (Idh) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
    def get_normal_sky_diffuse_solar_radiation(self, diffuse_atmospheric_transmittance: float, solar_altitude_angle: float) -> float:
        """Get the normal/horizontal sky diffuse solar radiation (Idh) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]

        Parameters
        ----------
        diffuse_atmospheric_transmittance : float
            Diffuse atmospheric transmittance (tau_d) [-]
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)

        Returns
        -------
        normal_sky_diffuse_solar_radiation : float
            Normal/horizontal sky diffuse solar radiation (Idh) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        solar_altitude_angle               = numpy.deg2rad(solar_altitude_angle)
        normal_sky_diffuse_solar_radiation = self.SOLAR_CONSTANT_OF_THE_EARTH * diffuse_atmospheric_transmittance * numpy.sin(solar_altitude_angle)
        return normal_sky_diffuse_solar_radiation

    # Get the declination angle (delta) in degrees [°]
    @staticmethod
    def get_declination_angle(day_number: int) -> float:
        """Get the declination angle (delta) in degrees [°]

        Parameters
        ----------
        day_number : int
            Number of days (n) since the beginning of the year [-]

        Returns
        -------
        declination_angle : float
            Declination angle (delta) in degrees [°]

        Raises
        ------
        ValueError
            Raise an error if the number of days (n) is not between 1 and 365 (days)

        Examples
        --------
        >>> None
        """
        # The sun's path changes over the year sine the Earth's orbit is inclined (23.5°)
        # It causes the seasons. It is zero at the equinoxes, maximum at the summer solstice (23.45), and minimum at the winter solstice (-23.45).
        if (day_number > 365) or (day_number < 1):
             raise ValueError(f"Sorry, but the day_number (n) should be between 1 and 365 (days)! Given : {day_number}")
        declination_angle = 23.45 * numpy.sin(numpy.deg2rad(360 * ((day_number + 284) / 365)))
        return declination_angle

    # Get the solar equation of time (EOT) in minutes [min] to account for irregularities in the Earth's orbit
    @staticmethod
    def get_solar_equation_of_time(day_number: int) -> float:
        """Get the solar equation of time (EOT) in minutes [min] to account for irregularities in the Earth's orbit (eccentricity, obliquity of the axis)

        Parameters
        ----------
        day_number : int
            Number of days (n) since the beginning of the year [-]

        Returns
        -------
        equation_of_time : float
            Solar equation of time (EOT) in minutes [min] to account for irregularities in the Earth's orbit (eccentricity, obliquity of the axis)

        Raises
        ------
        ValueError
            Raise an error if the number of days (n) is not between 1 and 365 (days)

        Examples
        --------
        >>> None
        """
        if (day_number > 365) or (day_number < 1):
             raise ValueError(f"Sorry, but the day_number (n) should be between 1 and 365 (days)! Given : {day_number}")
        equation_of_time = 9.87 * numpy.sin(4 * numpy.pi * ((day_number - 81) / 364)) - 7.53 * numpy.cos(2 * numpy.pi * ((day_number - 81) / 364)) - 1.5 * numpy.sin(2 * numpy.pi * ((day_number - 81) / 364))
        return equation_of_time

    # Get the apparent solar time (AST) in hours [h] to take into account: (i) the 4 min per degree between LSM and the actual longitude of the place and (ii) a correction called "equation of time" (in minutes)
    @staticmethod
    def get_apparent_solar_time(legal_standard_time: float, local_standard_meridian: float, longitude: float, equation_of_time: float) -> float:
        """Get the apparent solar time (AST) in hours [h] to take into account: (i) the 4 min per degree between LSM and the actual longitude of the place and (ii) a correction called "equation of time" (in minutes)

        Parameters
        ----------
        legal_standard_time : float
            Local standard time (LST) in hours [h], time we see in our watches
        local_standard_meridian : float
            Local standard meridian (LSM) in degrees [°], which is the reference meridian used for a particular time zone
        longitude : float
            Longitude (LON) of the place in degress [°]
        equation_of_time : float
            Solar equation of time (EOT) in minutes [min] to account for irregularities in the Earth's orbit (eccentricity, obliquity of the axis)

        Returns
        -------
        apparent_solar_time : float
            Apparent solar time (AST) in hours [h]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # 4 (min/deg)
        apparent_solar_time = legal_standard_time + (4 * (local_standard_meridian - longitude) + equation_of_time) / 60
        return apparent_solar_time

    # Get the hour angle (HA) in degrees [°C], that is, 15 degrees per hour past solar noon
    @staticmethod
    def get_hour_angle(apparent_solar_time: float) -> float:
        """Get the hour angle (HA) in degrees [°C], that is, 15 degrees per hour past solar noon

        Parameters
        ----------
        apparent_solar_time : float
            Apparent solar time (AST)

        Returns
        -------
        hour_angle : float
           Hour angle (HA) in degrees [°C], that is, 15 degrees per hour past solar noon

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        # HA is negative from 00:00 to noon
        hour_angle = 15 * (apparent_solar_time - 12)
        return hour_angle

    # Get the solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)
    @staticmethod
    def get_solar_altitude_angle(latitude: float, declination_angle: float, hour_angle: float) -> float:
        """Get the solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)

        Parameters
        ----------
        latitude : float
            Latitude angle (LAT) in degrees [°]
        declination_angle : float
            Declination angle (delta) in degrees [°]
        hour_angle : float
           Hour angle (HA) in degrees [°C], that is, 15 degrees per hour past solar noon

        Returns
        -------
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        latitude             = numpy.deg2rad(latitude)
        declination_angle    = numpy.deg2rad(declination_angle)
        hour_angle           = numpy.deg2rad(hour_angle)
        solar_altitude_angle = max(0, numpy.arcsin(numpy.cos(latitude) * numpy.cos(declination_angle) * numpy.cos(hour_angle) + numpy.sin(latitude) * numpy.sin(declination_angle)))
        solar_altitude_angle = numpy.rad2deg(solar_altitude_angle)
        return solar_altitude_angle

    # Get the solar azimuth angle (phi) in degrees [°], which is the angle between the sun's rays and a reference direction (e.g., South = 0°, West = - 90°, North = 180°, East = 90°)
    @staticmethod
    def get_solar_azimuth_angle(latitude: float, declination_angle: float, solar_altitude_angle: float, hour_angle: float) -> float:
        """Get the solar azimuth angle (phi) in degrees [°], which is the angle between the sun's rays and a reference direction (e.g., South = 0°, West = - 90°, North = 180°, East = 90°)

        Parameters
        ----------
        latitude : float
            Latitude angle (LAT) in degrees [°]
        declination_angle : float
            Declination angle (delta) in degrees [°]
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)
        hour_angle : float
           Hour angle (HA) in degrees [°C], that is, 15 degrees per hour past solar noon

        Returns
        -------
        solar_azimuth_angle : float
           Solar azimuth angle (phi) in degrees [°], which is the angle between the sun's rays and a reference direction (e.g., South = 0°, West = - 90°, North = 180°, East = 90°)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        latitude             = numpy.deg2rad(latitude)
        declination_angle    = numpy.deg2rad(declination_angle)
        solar_altitude_angle = numpy.deg2rad(solar_altitude_angle)
        hour_angle           = numpy.deg2rad(hour_angle)
        if hour_angle == 0.0:
            solar_azimuth_angle = 0.0
        else:
            # Negative in the morning and positive in the afternoon
            solar_azimuth_angle = numpy.arccos((numpy.sin(solar_altitude_angle) * numpy.sin(latitude) - numpy.sin(declination_angle)) / (numpy.cos(solar_altitude_angle) * numpy.cos(latitude))) * (hour_angle / abs(hour_angle))
            solar_azimuth_angle = numpy.rad2deg(solar_azimuth_angle)
        return solar_azimuth_angle

    # Get the solar surface azimuth angle (gamma) in degrees [°], which is the angle difference between solar azimuth angle and the surface azimuth angle)
    @staticmethod
    def get_solar_surface_azimuth_angle(solar_azimuth_angle: float, surface_azimuth_angle: float) -> float:
        """Get the solar surface azimuth angle (gamma) in degrees [°], which is the angle difference between solar azimuth angle and the surface azimuth angle)

        Parameters
        ----------
        solar_azimuth_angle : float
           Solar azimuth angle (phi) in degrees [°], which is the angle between the sun's rays and a reference direction (e.g., South = 0°, West = - 90°, North = 180°, East = 90°)
        surface_azimuth_angle : float
            Surface azimuth angle (phi) in degrees [°], which is the angle between the sun's rays and the surface direction (e.g., South = 0°, West = - 90°, North = 180°, East = 90°)

        Returns
        -------
        solar_surface_azimuth_angle : float
           Solar surface azimuth angle (gamma) in degrees [°], which is the angle difference between solar azimuth angle and the surface azimuth angle)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        solar_surface_azimuth_angle = solar_azimuth_angle - surface_azimuth_angle
        return solar_surface_azimuth_angle

    # Get the incidence angle (theta) on the tilted surface (beta) in degrees [°], which is the angle between the solar rays and the normal to the surface
    @staticmethod
    def get_incidence_angle(solar_zenith_angle: float, surface_tilt_angle: float, solar_surface_azimuth_angle: float) -> float:
        """Get the incidence angle (theta) on the tilted surface (beta) in degrees [°], which is the angle between the solar rays and the normal to the surface

        Parameters
        ----------
        solar_zenith_angle : float
            Solar zenith angle (theta_z) in degrees [°], which is the angle between the sun's rays and the vertical (between 0 and 90°)
        surface_tilt_angle : float
            Surface tilt angle (beta) in degrees [°], which is the angle between the surface and the horizon (0 - 180°)
        solar_surface_azimuth_angle : float
           Solar surface azimuth angle (gamma) in degrees [°], which is the angle difference between solar azimuth angle and the surface azimuth angle)

        Returns
        -------
        incidence_angle : float
           The incidence angle (theta) on the tilted surface (beta) in degrees [°], which is the angle between the solar rays and the normal to the surface

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        solar_zenith_angle          = numpy.deg2rad(solar_zenith_angle)
        surface_tilt_angle          = numpy.deg2rad(surface_tilt_angle)
        solar_surface_azimuth_angle = numpy.deg2rad(solar_surface_azimuth_angle)
        incidence_angle             = numpy.arccos(numpy.sin(solar_zenith_angle) * numpy.cos(abs(solar_surface_azimuth_angle)) * numpy.sin(surface_tilt_angle) + numpy.cos(solar_zenith_angle) * numpy.cos(surface_tilt_angle))
        incidence_angle             = min(numpy.pi / 2, incidence_angle)
        incidence_angle             = numpy.rad2deg(incidence_angle)
        return incidence_angle

    # Get the solar zenith angle (theta_z) in degrees [°], which is the angle between the sun's rays and the vertical (between 0 and 90°)
    @staticmethod
    def get_solar_zenith_angle(solar_altitude_angle: float) -> float:
        """Get the solar zenith angle (theta_z) in degrees [°], which is the angle between the sun's rays and the vertical (between 0 and 90°)

        Parameters
        ----------
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)

        Returns
        -------
        solar_zenith_angle : float
            Solar zenith angle (theta_z) in degrees [°], which is the angle between the sun's rays and the vertical (between 0 and 90°)

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        solar_altitude_angle = numpy.deg2rad(solar_altitude_angle)
        solar_zenith_angle   = numpy.pi / 2 - solar_altitude_angle
        solar_zenith_angle   = numpy.rad2deg(solar_zenith_angle)
        return solar_zenith_angle

    # Get the atmospheric transmittance for beam radiation (tau_b) [-]
    @staticmethod
    def get_atmospheric_transmittance_for_beam_radiation(altitude: float, solar_zenith_angle: float):
        """Get the atmospheric transmittance for beam radiation (tau_b) [-]

        Parameters
        ----------
        altitude : float
            Altitude (alt) in meters [m]
        solar_zenith_angle : float
            Solar zenith angle (theta_z) in degrees [°C], which is the angle between the sun's rays and the vertical (between 0 and 90°)

        Returns
        -------
        atmospheric_transmittance_for_beam_radiation : float
            Atmospheric transmittance for beam radiation (tau_b) [-]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        solar_zenith_angle = numpy.deg2rad(solar_zenith_angle)
        altitude_km        = altitude / 1000
        a_0                = 1.03 * (0.4237 - 0.00821 * (6 - altitude_km) ** 2)
        a_1                = 1.01 * (0.5055 + (0.00595 * (6.5 - altitude_km) ** 2))
        k                  = 1 * (0.2711 + (0.01858 * (2.5 - altitude_km) ** 2))
        if numpy.cos(solar_zenith_angle) == 0.0:
            atmospheric_transmittance_for_beam_radiation = 0.0
        else:
            atmospheric_transmittance_for_beam_radiation = a_0 + a_1 * numpy.exp(-k / numpy.cos(solar_zenith_angle))
        return atmospheric_transmittance_for_beam_radiation

    # Get the diffuse atmospheric transmittance (tau_d) [-]
    @staticmethod
    def get_diffuse_atmospheric_transmittance(atmospheric_transmittance_for_beam_radiation: float) -> float:
        """Get the diffuse atmospheric transmittance (tau_d) [-]

        Parameters
        ----------
        atmospheric_transmittance_for_beam_radiation : float
            Atmospheric transmittance for beam radiation (tau_b) [-]

        Returns
        -------
        diffuse_atmospheric_transmittance : float
            Diffuse atmospheric transmittance (tau_d) [-]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        diffuse_atmospheric_transmittance = 0.2710 - 0.2939 * atmospheric_transmittance_for_beam_radiation
        return diffuse_atmospheric_transmittance

    # Get the direct beam solar radiation (Ib) in watts per square meter [W/m²] from the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]
    @staticmethod
    def get_direct_beam_solar_radiation(direct_normal_beam_solar_radiation: float, incidence_angle: float, solar_altitude_angle: float, surface_tilt_angle: float) -> float:
        """Get the direct beam solar radiation (Ib) in watts per square meter [W/m²] from the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]

        Parameters
        ----------
        direct_normal_beam_solar_radiation : float
            Direct normal beam solar radiation (Ibn) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        incidence_angle : float
           The incidence angle (theta) on the tilted surface (beta) in degrees [°], which is the angle between the solar rays and the normal to the surface
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)
        surface_tilt_angle : float
            Surface tilt angle (beta) in degrees [°], which is the angle between the surface and the horizon (0 - 180°)

        Returns
        -------
        direct_beam_solar_radiation : float
            Direct beam solar radiation (Ib) in watts per square meter [W/m²] direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        incidence_angle      = numpy.deg2rad(incidence_angle)
        solar_altitude_angle = numpy.deg2rad(solar_altitude_angle)
        # For horizontal surfaces
        if surface_tilt_angle == 0.0:
            direct_beam_solar_radiation = direct_normal_beam_solar_radiation * numpy.sin(solar_altitude_angle)
        else:
            direct_beam_solar_radiation = direct_normal_beam_solar_radiation * numpy.cos(incidence_angle)
        return direct_beam_solar_radiation

    # Get the sky-diffuse solar radiation (Id) in watts per square meter [W/m²] from the normal/horizontal sky-diffuse solar radiation (Idh) in watts per square meter [W/m²]
    @staticmethod
    def get_sky_diffuse_solar_radiation(normal_sky_diffuse_solar_radiation: float, surface_tilt_angle: float) -> float:
        """Get the sky-diffuse solar radiation (Id) in watts per square meter [W/m²] from the normal/horizontal sky-diffuse solar radiation (Idh) in watts per square meter [W/m²]

        Parameters
        ----------
        normal_sky_diffuse_solar_radiation : float
            Normal/horizontal sky diffuse solar radiation (Idh) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        surface_tilt_angle : float
            Surface tilt angle (beta) in degrees [°], which is the angle between the surface and the horizon (0 - 180°)

        Returns
        -------
        sky_diffuse_solar_radiation : float
            Sky-diffuse solar radiation (Id) in watts per square meter [W/m²] from the normal/horizontal sky-diffuse solar radiation (Idh) in watts per square meter [W/m²]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        surface_tilt_angle          = numpy.deg2rad(surface_tilt_angle)
        sky_diffuse_solar_radiation = normal_sky_diffuse_solar_radiation * ((1 + numpy.cos(surface_tilt_angle)) / 2)
        return sky_diffuse_solar_radiation

    # Get the reflected solar radiation from the ground (Ig) in watts per square meter [W/m²] from the normal/horizontal sky-diffuse and horizontal beam solar radiations (Idh and Ibg) in watts per square meter [W/m²]
    @staticmethod
    def get_reflected_diffuse_solar_radiation(direct_horizontal_beam_solar_radiation: float, normal_sky_diffuse_solar_radiation: float, ground_reflectance: float, surface_tilt_angle: float) -> float:
        """Get the reflected solar radiation from the ground (Ig) in watts per square meter [W/m²] from the normal/horizontal sky-diffuse and horizontal beam solar radiations (Idh and Ibg) in watts per square meter [W/m²]

        Parameters
        ----------
        direct_horizontal_beam_solar_radiation : float
            Direct horizontal beam solar radiation (Ib) in watts per square meter [W/m²] from the direct normal beam solar radiation (Ibn) in watts per square meter [W/m²]
        normal_sky_diffuse_solar_radiation : float
            Normal/horizontal sky diffuse solar radiation (Idh) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        ground_reflectance : float
            Ground reflectance (rho) near the place [-]
        surface_tilt_angle : float
            Surface tilt angle (beta) in degrees [°], which is the angle between the surface and the horizon (0 - 180°)

        Returns
        -------
        reflected_diffuse_solar_radiation : float
            Reflected solar radiation from the ground (Ig) in watts per square meter [W/m²] from the normal/horizontal sky-diffuse and horizontal beam solar radiations (Idh and Ibg) in watts per square meter [W/m²]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        surface_tilt_angle                = numpy.deg2rad(surface_tilt_angle)
        reflected_diffuse_solar_radiation = (direct_horizontal_beam_solar_radiation + normal_sky_diffuse_solar_radiation) * ground_reflectance * ((1 - abs(numpy.cos(surface_tilt_angle))) / 2)
        return reflected_diffuse_solar_radiation

    # Get the total solar radiation on the tilt surface (It) in watts per square meter [W/m²]
    def get_total_incident_solar_radiation(self, direct_normal_beam_solar_radiation: float, normal_sky_diffuse_solar_radiation: float, incidence_angle: float, solar_altitude_angle: float, surface_tilt_angle: float, ground_reflectance: float) -> float:
        """Get the total solar radiation on the tilt surface (It) in watts per square meter [W/m²]

        Parameters
        ----------
        direct_normal_beam_solar_radiation : float
            Direct normal beam solar radiation (Ibn) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        normal_sky_diffuse_solar_radiation : float
            Normal/horizontal sky diffuse solar radiation (Idh) in watts per square meter [W/m²] using the solar constant of the Earth - 1367 [W/m²]
        incidence_angle : float
           The incidence angle (theta) on the tilted surface (beta) in degrees [°], which is the angle between the solar rays and the normal to the surface
        solar_altitude_angle : float
           Solar altitude angle (alpha) in degrees [°], which is the angle between the sun's rays and the horizon (between 0 and 90°)
        surface_tilt_angle : float
            Surface tilt angle (beta) in degrees [°], which is the angle between the surface and the horizon (0 - 180°)
        ground_reflectance : float
            Ground reflectance (rho) near the place [-]

        Returns
        -------
        total_incident_solar_radiation : float
            Total solar radiation on the tilt surface (It) in watts per square meter [W/m²]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        total_incident_solar_radiation = self.get_direct_beam_solar_radiation(direct_normal_beam_solar_radiation, incidence_angle, solar_altitude_angle, surface_tilt_angle) + \
                                         self.get_sky_diffuse_solar_radiation(normal_sky_diffuse_solar_radiation, surface_tilt_angle) + \
                                         self.get_reflected_diffuse_solar_radiation(direct_normal_beam_solar_radiation, normal_sky_diffuse_solar_radiation, ground_reflectance, surface_tilt_angle)
        return total_incident_solar_radiation

    # Get the sunrise time (time at which the sunrise happens) in hours [h]
    def get_sun_rise_time(self, latitude: float, declination_angle: float) -> float:
        """Get the sunrise time (time at which the sunrise happens) in hours [h]

        Parameters
        ----------
        latitude : float
            Latitude angle (LAT) in degrees [°]
        declination_angle : float
            Declination angle (delta) in degrees [°]

        Returns
        -------
        sun_rise_time : float
            Sunrise time (time at which the sunrise happens) in hours [h]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        sun_set_hour_angle = self._get_sun_hour_angle(latitude, declination_angle)
        sun_rise_time      =  12 - sun_set_hour_angle / 15
        return sun_rise_time

    # Get the sunset time (time at which the sunset happens) in hours [h]
    def get_sun_set_time(self, latitude: float, declination_angle: float) -> float:
        """Get the sunset time (time at which the sunset happens) in hours [h]

        Parameters
        ----------
        latitude : float
            Latitude angle (LAT) in degrees [°]
        declination_angle : float
            Declination angle (delta) in degrees [°]

        Returns
        -------
        sun_set_time : float
            Sunset time (time at which the sunset happens) in hours [h]

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        sun_set_hour_angle = self._get_sun_hour_angle(latitude, declination_angle)
        sun_set_time       = 12 + sun_set_hour_angle / 15
        return sun_set_time

    # Get the sun hour angle in degrees [°], which can be subtracted or added to noon to get the sunrise and sunset times
    @staticmethod
    def _get_sun_hour_angle(latitude: float, declination_angle: float) -> float:
        """Get the sun hour angle in degrees [°], which can be subtracted or added to noon to get the sunrise and sunset times

        Parameters
        ----------
        latitude : float
            Latitude angle (LAT) in degrees [°]
        declination_angle : float
            Declination angle (delta) in degrees [°]

        Returns
        -------
        sun_set_hour_angle : float
            sun hour angle in degrees [°], which can be subtracted or added to noon to get the sunrise and sunset times

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        latitude           = numpy.deg2rad(latitude)
        declination_angle  = numpy.deg2rad(declination_angle)
        sun_set_hour_angle = numpy.arccos(-numpy.tan(latitude) * numpy.tan(declination_angle))
        sun_set_hour_angle = numpy.rad2deg(sun_set_hour_angle)
        return sun_set_hour_angle

    # Return the string representation of the object
    def __str__(self) -> str:
        """Return the string representation of the object

        Parameters
        ----------

        Returns
        -------
        string_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        string_representation = f"{self.__class__.__name__}({self.name})"
        return string_representation

    # Return the object representation as a string
    def __repr__(self) -> str:
        """Return the object representation as a string

        Parameters
        ----------

        Returns
        -------
        object_representation : str
            String representing the object

        Raises
        ------
        None

        Examples
        --------
        >>> None
        """
        object_representation = self.__str__()
        return object_representation

# ========================================
# Functions
# ========================================


# ========================================
# References
# ========================================

