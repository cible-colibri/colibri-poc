from core.variable import Variable


class VariableList:

    def __init__(self, model, sizing_variable_name: str, variables: list):
        self.model = model
        self.name = sizing_variable_name
        self.variables = variables

    def expand(self):
        sizing_variable = self.model.get(self.name)
        size = int(sizing_variable.value)
        new_variables = [self]
        for i in range(size):
            j = 1
            for v in self.variables:
                if len(self.variables) >1:
                    variable_name = v.name + "-" + str(i+1) + "-" + str(j)
                else:
                    variable_name = v.name + "-" + str(i+1)
                new_variables.append(Variable(variable_name))
                j = j+1
        return new_variables

    def add(self, variable, sizing_variable):
        self.variables.append((variable, sizing_variable))
