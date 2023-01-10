class Link:

    def __init__(self):
        self.from_model = None
        self.to_model = None
        self.from_variable = None
        self.to_variable = None

    def __init__(self, model1, variable1, model2, variable2):
        self.from_model = model1
        self.to_model = model2
        self.from_variable = variable1
        self.to_variable = variable2
