import pvlib
import ephem
import numpy as np
import os
import pandas as pd
from pkg_resources import resource_filename
from pathlib import Path
from colibri.core.model import Model
from colibri.utils.enums_utils import Roles, Units


class Weather(Model):
    def __init__(self, name: str):
        self.name = name

        self.Text = self.field(name='Text', default_value = 0.0, role=Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)

        self.constant_ground_temperature = self.field("constant_ground_temperature", 16, Roles.PARAMETERS, unit=Units.DEGREE_CELSIUS, description='Impose a constant ground temperature if the parameter is not None')

        self.year = self.field("year", 0, Roles.OUTPUTS)
        self.month = self.field("month", 0, Roles.OUTPUTS)
        self.day = self.field("day", 0, Roles.OUTPUTS)
        self.hour = self.field("hour", 0, Roles.OUTPUTS)
        self.minute = self.field("minute", 0, Roles.OUTPUTS)
        self.datasource = self.field("datasource", 0, Roles.OUTPUTS)
        self.temperature = self.field("temperature", 0, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.DewPoint = self.field("DewPoint", 0, Roles.OUTPUTS)
        self.RelHum = self.field("RelHum", 0, Roles.OUTPUTS)
        self.pressure = self.field("pressure", 0, Roles.OUTPUTS)
        self.ExtHorzRad = self.field("ExtHorzRad", 0, Roles.OUTPUTS)
        self.ExtDirRad = self.field("ExtDirRad", 0, Roles.OUTPUTS)
        self.HorzIRSky = self.field("HorzIRSky", 0, Roles.OUTPUTS)
        self.GloHorzRad = self.field("GloHorzRad", 0, Roles.OUTPUTS)
        self.direct_radiation = self.field("direct_radiation", 0, Roles.OUTPUTS)
        self.diffuse_radiation = self.field("diffuse_radiation", 0, Roles.OUTPUTS)
        self.GloHorzIllum = self.field("GloHorzIllum", 0, Roles.OUTPUTS)
        self.DirNormIllum = self.field("DirNormIllum", 0, Roles.OUTPUTS)
        self.DifHorzIllum = self.field("DifHorzIllum", 0, Roles.OUTPUTS)
        self.ZenLum = self.field("ZenLum", 0, Roles.OUTPUTS)
        self.wind_direction = self.field("wind_direction", 0, Roles.OUTPUTS)
        self.wind_speed = self.field("wind_speed", 0, Roles.OUTPUTS)
        self.TotSkyCvr = self.field("TotSkyCvr", 0, Roles.OUTPUTS)
        self.OpaqSkyCvr = self.field("OpaqSkyCvr", 0, Roles.OUTPUTS)
        self.Visibility = self.field("Visibility", 0, Roles.OUTPUTS)
        self.Ceiling = self.field("Ceiling", 0, Roles.OUTPUTS)
        self.presweathobs = self.field("presweathobs", 0, Roles.OUTPUTS)
        self.presweathcodes = self.field("presweathcodes", 0, Roles.OUTPUTS)
        self.precipwtr = self.field("precipwtr", 0, Roles.OUTPUTS)
        self.aerosoloptdepth = self.field("aerosoloptdepth", 0, Roles.OUTPUTS)
        self.snowdepth = self.field("snowdepth", 0, Roles.OUTPUTS)
        self.dayslastsnow = self.field("dayslastsnow", 0, Roles.OUTPUTS)
        self.albedo = self.field("albedo", 0, Roles.OUTPUTS)
        self.rain = self.field("rain", 0, Roles.OUTPUTS)
        self.rain_hr = self.field("rain_hr", 0, Roles.OUTPUTS)

    def initialize(self):

        self.weather_data, self.latitude, self.longitude, self.solar_direct, self.solar_diffuse, self.ext_temperature = import_epw_weather(self.weather_file)

        if self.constant_ground_temperature is not None:
            self.ground_temperature = self.constant_ground_temperature * np.ones(self.weather_data['ground_temperature'].shape)
        else:
            self.ground_temperature = self.weather_data['ground_temperature']

        self.sky_temperature = self.weather_data['sky_temperature']
        time_window = 48
        self.rolling_external_temperature = self.ext_temperature.rolling(time_window).mean()
        self.rolling_external_temperature[0:time_window] = self.rolling_external_temperature[time_window:2 * time_window]

    def run(self, time_step: int = 0, n_iteration: int = 0):
        self.Text = self.ext_temperature[time_step]
        pass

    def simulation_done(self, time_step: int = 0):
        pass

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        pass

def ground_temperature_kusuda(air_temperature, ground_diffusivity, depth):

    if len(air_temperature) != 8760:
        time_window = 168 * 4
        ground_temperature = air_temperature.rolling(time_window).mean()
        ground_temperature[0:time_window] = ground_temperature[time_window:2 * time_window]

    else:
        ext_temperature_smoothed = air_temperature.rolling(int(24. * 30.5)).mean().fillna(method='bfill')
        ground_deltaT = (max(ext_temperature_smoothed) - min(ext_temperature_smoothed)) / 2.
        ground_av_temperature = np.mean(ext_temperature_smoothed)
        time = (np.array(list(range(len(air_temperature)))) + 1.) / 24.
        phase_shift = int(air_temperature.idxmin() / 24)
        # Kusuda equation 1965
        gnd_temp = ground_av_temperature - ground_deltaT \
                   * np.exp(- depth * np.sqrt(np.pi / (ground_diffusivity * 365.))) \
                   * np.cos(2 * np.pi / 365. * (time - phase_shift - depth / 2. * np.sqrt(365. / (np.pi * ground_diffusivity))))

    return gnd_temp


def sun_heigh_etc(weather_data, latitude, longitude, tz='America/Denver'):
    start = '2018-01-01 00:00'
    end = '2018-12-31 23:00'
    weather_index = pd.date_range(start=start, end=end, freq='1h', tz=tz)
    # we define the position from which the sun is observed
    sun_observer = ephem.Observer()
    sun_observer.lon, sun_observer.lat = str(longitude), str(latitude)

    # we obtain the UTC time in datetime format
    utc_index = weather_index.tz_convert(tz='UTC')

    # we compute the height and azimuth of the sun
    sun = ephem.Sun()
    sun_height = np.zeros((len(weather_index), 1), dtype=np.float32)
    sun_azimuth = np.zeros((len(weather_index), 1), dtype=np.float32)

    for i, date_obs in enumerate(utc_index):
        sun_observer.date = date_obs
        sun_observer.date += ephem.minute * 30
        sun.compute(sun_observer)
        sun_height[i, 0] = sun.alt * 180. / np.pi
        sun_azimuth[i, 0] = sun.az * 180. / np.pi
    return sun_height, sun_azimuth, weather_index


def import_epw_weather(epf_file):
    weather_dir = resource_filename('colibri', os.path.join('data', 'weather'))
    EPW_vars = ('year', 'month', 'day', 'hour', 'minute', 'datasource', 'temperature', 'DewPoint',
                'RelHum', 'pressure', 'ExtHorzRad', 'ExtDirRad', 'HorzIRSky', 'GloHorzRad', 'direct_radiation',
                'diffuse_radiation', 'GloHorzIllum', 'DirNormIllum', 'DifHorzIllum',
                'ZenLum', 'wind_direction', 'wind_speed', 'TotSkyCvr', 'OpaqSkyCvr', 'Visibility', 'Ceiling',
                'presweathobs', 'presweathcodes', 'precipwtr', 'aerosoloptdepth', 'snowdepth',
                'dayslastsnow', 'albedo', 'rain', 'rain_hr')
    weather_file = os.path.join(weather_dir, 'epw', epf_file)
    weather_data    = pd.read_csv(weather_file, skiprows=8, header=None, names=EPW_vars)
    latitude, longitude = tuple(pd.read_csv(weather_file, header=None, nrows=1).loc[:, 6:7].values.flatten().tolist())
    solar_direct    = weather_data['direct_radiation']
    solar_diffuse   = weather_data['diffuse_radiation']
    ext_temperature = weather_data.temperature
    pressure        = weather_data['pressure']
    relative_humidity = weather_data['RelHum']

    # calculate sky temperature
    dew_temperature = weather_data['DewPoint']
    opaque_sky_cover = weather_data['OpaqSkyCvr']
    sigma = 5.66797e-8
    N = opaque_sky_cover / 10.
    sky_emissivity = (0.787 + 0.764 * np.log((dew_temperature + 273.15) / 273.15)) * (
                1 + 0.0224 * N - 0.0035 * N ** 2 + 0.00028 * N ** 3)
    horizontal_IR = sky_emissivity * sigma * (weather_data['temperature'] + 273.15) ** 4
    sky_temperature = (horizontal_IR / sigma) ** 0.25 - 273.15
    weather_data['sky_temperature'] = np.array(sky_temperature.values)
    weather_data['opaque_sky_cover'] = np.array(opaque_sky_cover.values)
    # calculate ground temperature
    depth = 0.25
    ground_diffusivity = 0.645e-6 * 3600.
    weather_data['ground_temperature'] = ground_temperature_kusuda(air_temperature=weather_data['temperature'],
                                                                   ground_diffusivity=ground_diffusivity,
                                                                   depth=depth)

    return weather_data, latitude, longitude, solar_direct, solar_diffuse, ext_temperature


def solar_processor(weather_data, latitude, longitude, Boundary_list, Space_list, time_zone):
    sun_height, sun_azimuth, weather_index = sun_heigh_etc(weather_data, latitude, longitude, time_zone)
    extra_terrestrial = pvlib.irradiance.get_extra_radiation(weather_index).values
    direct_radiation = weather_data['direct_radiation'].values.flatten()
    diffuse_radiation = weather_data['diffuse_radiation'].values.flatten()
    solar_bound_arriving_flux_matrix = np.zeros((len(Boundary_list), len(weather_data)))
    solar_transmitted_flux_matrix = np.zeros((len(Space_list), len(weather_data)))
    i = 0
    for bound in Boundary_list:
        inclination = bound.tilt
        angle = bound.azimuth
        diffuse_radiation_on_plane, direct_radiation_on_plane, angle_of_incidence = \
            radiation_process(angle, inclination, direct_radiation, diffuse_radiation, sun_height, sun_azimuth.flatten(),
                              extra_terrestrial, albedo=0.2)
        bound.direct_radiation = direct_radiation_on_plane
        bound.diffuse_radiation = diffuse_radiation_on_plane
        bound.angle_of_incidence = angle_of_incidence
        solar_bound_arriving_flux_matrix[i, :] = direct_radiation_on_plane + diffuse_radiation_on_plane
        i += 1

    i = 0  # space indexing
    for space in Space_list:
        for env in space.envelope_list:
            if space.envelope_list[env]['type'] == 'window':
                #_search for boundary for tilt and orientation
                for bound in Boundary_list:
                    if bound.label == space.envelope_list[env]['boundary_name']:
                        inclination = bound.tilt
                        angle = bound.azimuth
                        diffuse_radiation_on_plane, direct_radiation_on_plane, angle_of_incidence = \
                            radiation_process(angle, inclination, direct_radiation, diffuse_radiation, sun_height,
                                              sun_azimuth.flatten(),
                                              extra_terrestrial, albedo=0.2)
                        space.envelope_list[env]['direct_radiation'] = direct_radiation_on_plane
                        space.envelope_list[env]['diffuse_radiation'] = diffuse_radiation_on_plane
                        space.envelope_list[env]['angle_of_incidence'] = angle_of_incidence
                        window_transmission_factor = space.envelope_list[env]['transmittance']

                        # transmission through windows from dimosim
                        transmission_coeff = np.clip(((1. - (angle_of_incidence / 90.) ** 5) * window_transmission_factor), 0., 1.)
                        direct_transmission = transmission_coeff * direct_radiation_on_plane
                        diffuse_transmission = 0.894 * window_transmission_factor * diffuse_radiation_on_plane  # [Brau88]
                        solar_transmitted_flux_matrix[i, :] += (direct_transmission + diffuse_transmission) * space.envelope_list[env]['area']
        i += 1

    return solar_bound_arriving_flux_matrix, solar_transmitted_flux_matrix


def radiation_process(angle, inclination, direct_radiation, diffuse_radiation, sun_height, sun_azimuth,
                      extra_terrestrial, albedo, diffuse_radiation_model='perez'):

    # """
    # We use the simulators from pvlib for radiation processing
    # :param angle:
    # """
    # # We take into account the influence of shading masks on direct radiation
    # # mask = mask_on_direct(shading_mask.astype(np.float64), sun_height.astype(np.float64), sun_azimuth.astype(np.float64))
    # # direct_radiation = direct_radiation * mask
    #
    # # We consider the influence of masks on diffuse radiation by applying to it a correction factor equal to the
    # # percentage of the sky that is not shaded, with a formula from Bernard & Bocher (2018)
    # # In this case the reflection on the other buildings are not considerate
    # # Be careful, I think there is already a 0.5 factor for the walls, that's why there isn't a factor 2
    # # sky_view = min(1 - 1. / 180. * (sum(np.sin(np.radians(shading_mask)) ** 2) - 180.), 1.)
    # # diffuse_radiation = diffuse_radiation * sky_view

    # we obtain the zenith from the sun height
    zenith = 90. - sun_height.flatten()

    # Calculation of ground direct
    direct_radiation_horizontal = direct_radiation.flatten() * np.sin(sun_height.flatten() * np.pi / 180.)
    direct_radiation_horizontal[direct_radiation_horizontal < 0] = 0

    # Calculation of ground diffuse
    ground_global = diffuse_radiation + direct_radiation_horizontal
    ground_diffuse = pvlib.irradiance.get_ground_diffuse(inclination, ground_global, albedo=albedo)

    # Calculation of sky diffuse on plane
    if diffuse_radiation_model == 'perez':
        relative_airmass = pvlib.atmosphere.get_relative_airmass(zenith, model='kastenyoung1989')
        sky_diffuse_perez = pvlib.irradiance.perez(inclination, angle, diffuse_radiation, direct_radiation,
                                                   extra_terrestrial, zenith, sun_azimuth, relative_airmass)
        sky_diffuse = np.where(np.isnan(sky_diffuse_perez), 0, sky_diffuse_perez)
        # Just in case, there was problem with some Georgios' files
    elif diffuse_radiation_model == 'isotropic':
        sky_diffuse_isotropic = pvlib.irradiance.isotropic(inclination, diffuse_radiation)
        sky_diffuse = sky_diffuse_isotropic
    # Too simple sky model, with no calculation gains
    else:
        raise ValueError('Invalid value for diffuse_radiation_model : ' + str(diffuse_radiation_model))

    # Angle of incidence calculation
    angle_of_incidence = pvlib.irradiance.aoi(inclination, angle, zenith, sun_azimuth)

    # Calculation of total radiation on the surface
    radiation_on_plane = pvlib.irradiance.poa_components(angle_of_incidence, direct_radiation, sky_diffuse,
                                                        ground_diffuse)

    diffuse_radiation_on_plane = radiation_on_plane['poa_diffuse']
    direct_radiation_on_plane = radiation_on_plane['poa_direct']

    return diffuse_radiation_on_plane, direct_radiation_on_plane, angle_of_incidence
