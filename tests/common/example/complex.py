
actions = []


def setUpRun():
    global actions
    actions = ["setUpRun"]


def tearDownRun():
    global actions
    actions.append("tearDownRun")


class Complex_A:

    def setUpModel(self):
        global actions
        self.actions = actions

        self.actions.append("Complex_A.setUpModel")

    def tearDownModel(self):
        self.actions.append("Complex_A.tearDownModel")

    def vertex_0(self):
        self.actions.append("Complex_A.vertex_0")

    def vertex_1(self):
        self.actions.append("Complex_A.vertex_1")

    def vertex_2(self):
        self.actions.append("Complex_A.vertex_2")

    def edge_0(self):
        self.actions.append("Complex_A.edge_0")

    def edge_1(self):
        self.actions.append("Complex_A.edge_1")


class Complex_B:

    def setUpModel(self):
        global actions
        self.actions = actions

        self.actions.append("Complex_B.setUpModel")

    def tearDownModel(self):
        self.actions.append("Complex_B.tearDownModel")

    def vertex_3(self):
        self.actions.append("Complex_B.vertex_3")

    def vertex_4(self):
        self.actions.append("Complex_B.vertex_4")

    def edge_2(self):
        self.actions.append("Complex_B.edge_2")

    def edge_3(self):
        self.actions.append("Complex_B.edge_3")
