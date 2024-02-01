# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================

import pathlib
import pandas

# ========================================
# Internal imports
# ========================================

from core.file         import File
from core.inputs       import Inputs
from core.model        import Model
from core.parameters   import Parameters
from core.outputs      import Outputs
from core.variable     import Variable
from utils.enums_utils import (
                                Roles,
                                Units,
                               )

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

    def __init__(self, name: str, inputs: Inputs = None, outputs: Outputs = None,  parameters: Parameters = None):
        self.name              = name
        self.project           = None
        self.inputs            = [] if inputs is None else inputs.to_list()
        self.outputs           = [] if outputs is None else outputs.to_list()
        self.parameters        = [] if parameters is None else parameters.to_list()
        self.year              = Variable("year", 0, Roles.OUTPUTS)
        self.month             = Variable("month", 0, Roles.OUTPUTS)
        self.day               = Variable("day", 0, Roles.OUTPUTS)
        self.hour              = Variable("hour", 0, Roles.OUTPUTS)
        self.minute            = Variable("minute", 0, Roles.OUTPUTS)
        self.datasource        = Variable("datasource", 0, Roles.OUTPUTS)
        self.temperature       = Variable("temperature", 0, Roles.OUTPUTS, unit=Units.DEGREE_CELSIUS)
        self.DewPoint          = Variable("DewPoint", 0, Roles.OUTPUTS)
        self.RelHum            = Variable("RelHum", 0, Roles.OUTPUTS)
        self.pressure          = Variable("pressure", 0, Roles.OUTPUTS)
        self.ExtHorzRad        = Variable("ExtHorzRad", 0, Roles.OUTPUTS)
        self.ExtDirRad         = Variable("ExtDirRad", 0, Roles.OUTPUTS)
        self.HorzIRSky         = Variable("HorzIRSky", 0, Roles.OUTPUTS)
        self.GloHorzRad        = Variable("GloHorzRad", 0, Roles.OUTPUTS)
        self.direct_radiation  = Variable("direct_radiation", 0, Roles.OUTPUTS)
        self.diffuse_radiation = Variable("diffuse_radiation", 0, Roles.OUTPUTS)
        self.GloHorzIllum      = Variable("GloHorzIllum", 0, Roles.OUTPUTS)
        self.DirNormIllum      = Variable("DirNormIllum", 0, Roles.OUTPUTS)
        self.DifHorzIllum      = Variable("DifHorzIllum", 0, Roles.OUTPUTS)
        self.ZenLum            = Variable("ZenLum", 0, Roles.OUTPUTS)
        self.wind_direction    = Variable("wind_direction", 0, Roles.OUTPUTS)
        self.wind_speed        = Variable("wind_speed", 0, Roles.OUTPUTS)
        self.TotSkyCvr         = Variable("TotSkyCvr", 0, Roles.OUTPUTS)
        self.OpaqSkyCvr        = Variable("OpaqSkyCvr", 0, Roles.OUTPUTS)
        self.Visibility        = Variable("Visibility", 0, Roles.OUTPUTS)
        self.Ceiling           = Variable("Ceiling", 0, Roles.OUTPUTS)
        self.presweathobs      = Variable("presweathobs", 0, Roles.OUTPUTS)
        self.presweathcodes    = Variable("presweathcodes", 0, Roles.OUTPUTS)
        self.precipwtr         = Variable("precipwtr", 0, Roles.OUTPUTS)
        self.aerosoloptdepth   = Variable("aerosoloptdepth", 0, Roles.OUTPUTS)
        self.snowdepth         = Variable("snowdepth", 0, Roles.OUTPUTS)
        self.dayslastsnow      = Variable("dayslastsnow", 0, Roles.OUTPUTS)
        self.albedo            = Variable("albedo", 0, Roles.OUTPUTS)
        self.rain              = Variable("rain", 0, Roles.OUTPUTS)
        self.rain_hr           = Variable("rain_hr", 0, Roles.OUTPUTS)

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

    def run(self, time_step: int = 0, n_iteration: int = 0):
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
