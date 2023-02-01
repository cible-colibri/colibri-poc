import dataclasses
import json
import os
from typing import List

from core import data_path
from utils.singleton import Singleton


@dataclasses.dataclass
class Unit():
    name: str
    description: str
    addition_factor: float
    multiplication_factor: float
    si_code: str

    def __init__(self, name: str, description: str, addition_factor: float, multiplication_factor: float, si_code: str):
        self.name = name
        self.description = description
        self.addition_factor = float(addition_factor)
        self.multiplication_factor = float(multiplication_factor)
        self.si_code = si_code


@dataclasses.dataclass
class Dimension:
    name: str
    definition: str
    base_unit: Unit
    equivalent_units: List[Unit]

    def __init__(self, name: str, definition: str, base_unit: Unit, equivalent_units: List[Unit]):
        self.name = name
        self.definition = definition
        self.base_unit = Unit(**base_unit)
        self.equivalent_units = []
        for unit_def in equivalent_units:
            unit = Unit(**unit_def)
            self.equivalent_units.append(unit)



@dataclasses.dataclass
class UnitDictionary(metaclass=Singleton):

    dimensions: List[Dimension]

    def __init__(self, dimensions):
        self.dimensions = []
        for dimension_def in dimensions:
            d = Dimension(**dimension_def)
            self.dimensions.append(d)

    def get_unit(self, unit_name: str):
        for dimension in self.dimensions:
            if dimension.base_unit.name == unit_name:
                return dimension.base_unit
            else:
                for unit in dimension.equivalent_units:
                    if unit.name == unit_name:
                        return unit
        return None

    def convert(self, value: float, unit1_name: str, unit2_name: str) -> float:
        unit1 = self.get_unit(unit1_name)
        if not unit1:
            raise Exception("Unit " + unit1_name + " not found")
        unit2 = self.get_unit(unit2_name)
        if not unit2:
            raise Exception("Unit " + unit2_name + " not found")

        return ((value - unit1.addition_factor) / unit1.multiplication_factor) \
               * unit2.multiplication_factor + unit2.addition_factor


unit_dictionary_file = os.path.join(data_path['data'], 'unit_dictionary.json')
with open(unit_dictionary_file) as f:
   unit_dictionary_json = json.load(f)

unit_dictionary = UnitDictionary(**unit_dictionary_json)
