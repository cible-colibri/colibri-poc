from core.link import Link


class Project:
    models = []
    links = []

    def add(self, m):
        self.models.append(m)

    def connect(self, model1, variable1, model2, variable2):
        link = Link(model1, variable1, model2, variable2)
        self.links.append(link)

    def link(self, model1, model2, connector):
        for c in connector.connections:
            link = Link(model1, c[0], model2, c[1])
            self.links.append(link)

    def run(self):
        print()
        for i in range(2):
            print("Iteration ", i)
            for m in self.models:
                print("computing ", m.name)
                m.run()

            for l in self.links:
                print("substituting ", l)

        print("Result is 42.")
