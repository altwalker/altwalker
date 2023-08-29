
class Simple:

    def setUpModel(self):
        self.actions = ["Simple.setUpModel"]

    def vertex_a(self):
        self.actions.append("Simple.vertex_a")

    def vertex_b(self):
        self.actions.append("Simple.vertex_b")

    def edge_a(self):
        self.actions.append("Simple.edge_a")

    def edge_b(self):
        self.actions.append("Simple.edge_b")
