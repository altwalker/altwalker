from .base.base import Base

actions = []


def setUpRun():
    global actions
    actions = ["setUpRun"]


def tearDownRun():
    global actions
    actions.append("tearDownRun")


class ComplexA(Base):

    def setUpModel(self):
        global actions
        self.actions = actions

        self.actions.append("ComplexA.setUpModel")

    def tearDownModel(self):
        self.actions.append("ComplexA.tearDownModel")

    def vertex_a(self):
        self.actions.append("ComplexA.vertex_a")

    def vertex_b(self):
        self.actions.append("ComplexA.vertex_b")

    def vertex_c(self):
        self.actions.append("ComplexA.vertex_c")

    def edge_a(self):
        self.actions.append("ComplexA.edge_a")

    def edge_b(self):
        self.actions.append("ComplexA.edge_b")


class ComplexB(Base):

    def setUpModel(self):
        global actions
        self.actions = actions

        self.actions.append("ComplexB.setUpModel")

    def tearDownModel(self):
        self.actions.append("ComplexB.tearDownModel")

    def vertex_d(self):
        self.actions.append("ComplexB.vertex_d")

    def vertex_e(self):
        self.actions.append("ComplexB.vertex_e")

    def edge_c(self):
        self.actions.append("ComplexB.edge_c")

    def edge_d(self):
        self.actions.append("ComplexB.edge_d")
