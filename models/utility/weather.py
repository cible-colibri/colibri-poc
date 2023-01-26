# -*- coding: utf-8 -*-

# ========================================
# External imports
# ========================================


# ========================================
# Internal imports
# ========================================
from math import exp

import pandas as pd

from core.file import File
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

    def __init__(self, name: str):
        self.name    = name
        self.inputs  = []
        self.outputs = [
            Variable('year'),
            Variable('month'),
            Variable('day'),
            Variable('hour'),
            Variable('minute'),
            Variable('datasource'),
            Variable('temperature'),
            Variable('DewPoint'),
            Variable('RelHum'),
            Variable('pressure'),
            Variable('ExtHorzRad'),
            Variable('ExtDirRad'),
            Variable('HorzIRSky'),
            Variable('GloHorzRad'),
            Variable('direct_radiation'),
            Variable('diffuse_radiation'),
            Variable('GloHorzIllum'),
            Variable('DirNormIllum'),
            Variable('DifHorzIllum'),
            Variable('ZenLum'),
            Variable('wind_direction'),
            Variable('wind_speed'),
            Variable('TotSkyCvr'),
            Variable('OpaqSkyCvr'),
            Variable('Visibility'),
            Variable('Ceiling'),
            Variable('presweathobs'),
            Variable('presweathcodes'),
            Variable('precipwtr'),
            Variable('aerosoloptdepth'),
            Variable('snowdepth'),
            Variable('dayslastsnow'),
            Variable('albedo'),
            Variable('rain'),
            Variable('rain_hr')
        ]

        self.files = [File('weather_data', 'C:\home\source\colibrisuce\data\weather\EnergyPlus\Paris.epw',
                      'Weather data in EPW format')]

    def initialize(self):
        self.EPW_vars = [v.name for v in self.outputs]
        weather_file = self.get_file('weather_data')
        self.epw_path = weather_file.path
        self.climate_data = pd.read_csv(self.epw_path, skiprows=8, header=None, names=self.EPW_vars)

    def run(self, time_step=0):
        for v in self.outputs:
            setattr(self, v.name, self.climate_data[v.name][time_step])

    def simulation_done(self, time_step=0):
        print(f"{self.name}:")
        print(f"Mean temperature during simulation: {self.climate_data['temperature'][0:time_step].mean()}")
