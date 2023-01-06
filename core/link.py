class Link:

    def __init__(self):
        self.from_model = None
        self.to_model = None
        self.from_variable = None
        self.to_variable = None

    def __init__(self, model1, variable1, model2, variable2):
        self.from_model = model1
        self.to_model = variable1
        self.from_variable = model2
        self.to_variable = variable2
