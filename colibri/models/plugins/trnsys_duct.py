import os.path

from colibri.core.variables.variable import Variable

from colibri.models.plugins.trnsys_type import TrnsysType

# code automatically generated by Trnsy Simulation Studio
class TrnsysDuctType145(TrnsysType):
    def __init__(self, name):
        self.name = name
        self.trnsys_dir = "/Trnsys18"
        self.dll_path = os.path.join(self.trnsys_dir, 'UserLib\ReleaseDLLs')
        self.dll_name = 'trnDLL.dll'

        self.inputs = []
        self.outputs = []

        self.inputs.append(Variable("Inlet temperature", 10.0))
        self.inputs.append(Variable("Inlet humidity ratio", 0.0))
        self.inputs.append(Variable("Inlet relative humidity", 50))
        self.inputs.append(Variable("Inlet flow rate", 100.0))
        self.inputs.append(Variable("Inlet pressure", 1))
        self.inputs.append(Variable("Environment temperature", 10.0))

        self.outputs.append(Variable("Temperature", 0))
        self.outputs.append(Variable("Dimensionless", 0))
        self.outputs.append(Variable("Percentage", 0))
        self.outputs.append(Variable("Flow Rate", 0))
        self.outputs.append(Variable("Pressure", 0))
        self.outputs.append(Variable("Power", 0))
        self.outputs.append(Variable("Power", 0))
        self.outputs.append(Variable("Energy", 0))
        self.outputs.append(Variable("Temperature", 0))
        self.outputs.append(Variable("Dimensionless", 0))
        self.outputs.append(Variable("Power", 0))

    def run(self):
        # todo: implement something like this:
        # result = self.call_trnsys(145) # see class TrnsysType
        # for r in results:
        #     self.outputs
        pass