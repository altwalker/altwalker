import functools


def log(message=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(message)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class Simple:
    actions = []

    def setUpModel(self):
        print("Simple.setUpModel")

        self.actions = ["Simple.setUpModel"]

    def vertex_a(self, *args):
        print("Simple.vertex_a")
        print(args[0])

        self.actions.append("Simple.vertex_a")

    def vertex_b(self, data):
        print("Simple.vertex_b")
        print(data)

        self.actions.append("Simple.vertex_b")

    @log("Decorated method")
    def edge_a(self):
        print("Simple.edge_a")

        self.actions.append("Simple.edge_a")

    @log("Decorated method")
    def edge_b(self, data):
        print("Simple.edge_b")
        print(data)

        self.actions.append("Simple.edge_b")
