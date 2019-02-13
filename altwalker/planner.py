import warnings

from altwalker.graphwalker import GraphWalkerService, GraphWalkerClient


class OnlinePlanner:
    """Plan a path using the GraphWalker REST service."""

    def __init__(self, service, client):
        self._service = service
        self._client = client

        self.steps = []
        self.failed_step = {}
        self.failed_fixtures = []

    def kill(self):
        self._service.kill()

    def load(self, models):
        self._client.load(models)

    def has_next(self):
        return self._client.has_next()

    def get_next(self):
        step = self._client.get_next()
        self.steps.append({
            "id": step["id"],
            "name": step["name"],
            "modelName": step["modelName"]
        })

        return step

    def get_data(self):
        return self._client.get_data()

    def set_data(self, key, value):
        self._client.set_data(key, value)

    def restart(self):
        self.steps = []

        self.failed_step = {}
        self.failed_fixtures = []

        self._client.restart()

    def fail(self, step, message):
        if "id" in step:
            self.failed_step = {
                "id": step["id"],
                "name": step["name"],
                "modelName": step["modelName"]
            }
        else:
            self.failed_fixtures.append(step)

        self._client.fail(message)

    def get_statistics(self):
        statistics = self._client.get_statistics()

        statistics["steps"] = self.steps
        statistics["failedStep"] = self.failed_step
        statistics["failedFixtures"] = self.failed_fixtures

        return statistics


class OfflinePlanner:
    """Plan a path from a list of steps."""

    def __init__(self, steps):
        self._path = list(steps)
        self._position = 0

        self.failed_step = {}
        self.failed_fixtures = []

    @property
    def steps(self):
        return self._path[:self._position]

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path
        self.restart()

    def has_next(self):
        return self._position < len(self._path)

    def get_next(self):
        step = self._path[self._position]
        self._position += 1

        return dict(step)

    def get_data(self):
        warnings.warn(
            "The set_data and get_data are not supported in offline mode so calls to them have no effect.", UserWarning)

    def set_data(self, key, value):
        warnings.warn(
            "The set_data and get_data are not supported in offline mode so calls to them have no effect.", UserWarning)

    def fail(self, step, message):
        if "id" in step:
            self.failed_step = step
        else:
            self.failed_fixtures.append(step)

    def restart(self):
        self.failed_step = {}
        self.failed_fixtures = []

        self._position = 0

    def get_statistics(self):
        return {
            "steps": self.steps,
            "failedStep": self.failed_step,
            "failedFixtures": self.failed_fixtures
        }


def create_planner(models=None, steps=None, port=8887, verbose=False, unvisited=False,
                   blocked=False):
    if steps:
        return OfflinePlanner(steps)

    service = GraphWalkerService(port=port, models=models,
                                 unvisited=unvisited, blocked=blocked)
    client = GraphWalkerClient(port=port, verbose=verbose)

    return OnlinePlanner(service, client)
