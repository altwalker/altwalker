
class Simple:

    def setUpModel(self):
        self.actions = ["Simple.setUpModel"]

    def vertex_A(self):
        self.actions.append("Simple.vertex_A")

    def vertex_B(self):
        self.actions.append("Simple.vertex_B")

    def edge_A(self):
        self.actions.append("Simple.edge_A")

    def edge_B(self):
        self.actions.append("Simple.edge_B")
