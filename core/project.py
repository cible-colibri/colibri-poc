from core.link import Link


class Project:
    models = []
    links = []

    def add(self, m):
        self.models.append(m)

    def link(self, model1, variable1, model2, variable2):
        link = Link(model1, variable1, model2, variable2)
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
