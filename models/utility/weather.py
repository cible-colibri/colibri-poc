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
