from core.link import Link


class Project:
    models = []
    links = []

    def add(self, m):
        self.models.append(m)

    def link(self, model1, arg2, *connection):
        if len(connection) ==2:
            model2 = connection[0]
            variable2 = connection[1]
            link = Link(model1, arg2, model2, variable2)
            self.links.append(link)
        else:
            connector = connection[0]
            for c in connector.connections:
                link = Link(model1, c[0], arg2, c[1])
                self.links.append(link)

    def run(self):
        print()
        for i in range(2):
            print("Iteration ", i)
            for m in self.models:
                print("computing ", m.name)
                m.run()

            for l in self.links:
                print("substituting ", l.from_model + "." + l.from_variable + "->"
                      + l.to_model + "." + l.to_variable)

        print("Result is 42.")
