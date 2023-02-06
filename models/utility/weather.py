# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib
import pandas

# ========================================
# Internal imports
# ========================================

from core.file     import File
from core.model    import Model
from core.variable import Variable

# ========================================
# Constants
# ========================================


# ========================================
# Variables
# ========================================


# ========================================
# Classes
# ========================================

class Weather(Model):

    # TODO: Define variables here, with information inside the Variable class about where it belongs (inputs, outputs, etc.), then
    #       add them to the proper lists instead of starting from the list then setting the variables (as attributes)
    #       The Model class will be less complex (_define_inputs, _define_outputs, etc.) will be removed, keeping only _define_variables
    def _define_variables(self) -> None:
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.datasource = None
        self.temperature = None
        self.DewPoint = None
        self.RelHum = None
        self.pressure = None
        self.ExtHorzRad = None
        self.ExtDirRad = None
        self.HorzIRSky = None
        self.GloHorzRad = None
        self.direct_radiation = None
        self.diffuse_radiation = None
        self.GloHorzIllum = None
        self.DirNormIllum = None
        self.DifHorzIllum = None
        self.ZenLum = None
        self.wind_direction = None
        self.wind_speed = None
        self.TotSkyCvr = None
        self.OpaqSkyCvr = None
        self.Visibility = None
        self.Ceiling = None
        self.presweathobs = None
        self.presweathcodes = None
        self.precipwtr = None
        self.aerosoloptdepth = None
        self.snowdepth = None
        self.dayslastsnow = None
        self.albedo = None
        self.rain = None
        self.rain_hr = None

    def _define_inputs(self) -> list:
        inputs = []
        return inputs

    def _define_outputs(self) -> list:
        outputs = [
                       Variable("year"),
                       Variable("month"),
                       Variable("day"),
                       Variable("hour"),
                       Variable("minute"),
                       Variable("datasource"),
                       Variable("temperature"),
                       Variable("DewPoint"),
                       Variable("RelHum"),
                       Variable("pressure"),
                       Variable("ExtHorzRad"),
                       Variable("ExtDirRad"),
                       Variable("HorzIRSky"),
                       Variable("GloHorzRad"),
                       Variable("direct_radiation"),
                       Variable("diffuse_radiation"),
                       Variable("GloHorzIllum"),
                       Variable("DirNormIllum"),
                       Variable("DifHorzIllum"),
                       Variable("ZenLum"),
                       Variable("wind_direction"),
                       Variable("wind_speed"),
                       Variable("TotSkyCvr"),
                       Variable("OpaqSkyCvr"),
                       Variable("Visibility"),
                       Variable("Ceiling"),
                       Variable("presweathobs"),
                       Variable("presweathcodes"),
                       Variable("precipwtr"),
                       Variable("aerosoloptdepth"),
                       Variable("snowdepth"),
                       Variable("dayslastsnow"),
                       Variable("albedo"),
                       Variable("rain"),
                       Variable("rain_hr"),
                   ]
        return outputs

    def _define_conditions(self) -> list:
        conditions = []
        return conditions

    def _define_parameters(self) -> list:
        parameters = []
        return parameters

    def initialize(self) -> None:
        # TODO: Modify when we wil have a package structure
        colibrisuce_path   = pathlib.Path(__file__).parents[2]
        print(colibrisuce_path)
        epw_file_path      = colibrisuce_path / "config" / "data" / "weather" / "epw" / "Paris.epw"
        self.files         = [File("weather_data", epw_file_path, "Weather data in EPW format")]
        self.epw_variables = [variable.name for variable in self.outputs]
        self.epw_path      = self.get_file("weather_data").path
        self.climate_data  = pandas.read_csv(str(self.epw_path.absolute()), skiprows = 8, header = None, names = self.epw_variables)

    def check_units(self) -> None:
        pass

    def run(self, time_step: int = 0):
        for variable in self.outputs:
            setattr(self, variable.name, self.climate_data[variable.name][time_step])

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        for output in self.outputs:
            print(f"{output.name}={getattr(self, output.name)}")

    def iteration_done(self, time_step: int = 0):
        pass

    def timestep_done(self, time_step: int = 0):
        pass

    def simulation_done(self, time_step: int = 0):
        print(f"{self.name}:")
        print(f'Mean temperature during simulation: {self.climate_data["temperature"][0:time_step].mean()}')

    def get_file(self, name: str) -> object:
        for f in self.files:
            if f.name == name:
                return f


# ========================================
# Functions
# ========================================
