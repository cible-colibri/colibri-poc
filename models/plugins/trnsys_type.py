import os.path

from core.model import Model
from core.variable import Variable
from core.variable_list import VariableList
import ctypes as ctypes

class TrnsysType(Model):
    def __init__(self, name):
        self.name = name
        self.trnsys_dir = "/Trnsys18"
        self.dll_path = os.path.join(self.trnsys_dir, 'UserLib\ReleaseDLLs')
        self.dll_name = 'trnDLL.dll'

        self.inputs = []
        self.outputs = []

        self.inputs.append(Variable("Number of inputs", 1))
        self.inputs.extend(
            VariableList(self, "Number of inputs",
                [Variable("Input")]).expand())

        self.outputs.append(Variable("Number of outputs", 1))
        self.outputs.extend(
            VariableList(self, "Number of outputs",
                [Variable("Output")]).expand())

    def call_trnsys(self, type):
        # todo: implement something like this:
        # type_function = ctypes.CDLL(os.path.join(self.dll_path, self.dll_name))
        # info_array = ...
        # inputs = [i.value for i in self.inputs]
        # result = type_function.type1(inputs, info_array))
        # for r in results:
        #     self.outputs
        pass

    def run(self):
        # todo: implement something like this:
        # for r in results:
        #     self.outputs
        pass
