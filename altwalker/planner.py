import warnings

from altwalker.graphwalker import GraphWalkerService, GraphWalkerClient


class OnlinePlanner:
    """Plan a path using the GraphWalker REST service and client.

    The path generation is done at run-time, one step at a time, using
    the GraphWalker REST Service. This adds a bit of complexity, but
    the advantages is that you can interact with the grpah data using
    :func:`get_data` and :func:`set_data` methods.

    Attributes:
        steps: The sequence of executed steps.
        failed_step: A failed step.
        failed_fixutes: A list of failed fixtures.
    """

    def __init__(self, service, client):
        """Inits OnlinePlanner with ``GraphWalkerService`` and ``GraphWalkerClient``."""

        self._service = service
        self._client = client

        self.steps = []
        self.failed_step = {}
        self.failed_fixtures = []

    def kill(self):
        """Stop the GraphWalkerService process."""

        self._service.kill()

    def load(self, models):
        """Load the module(s) and reset the execution and the statistics."""

        self._client.load(models)

    def has_next(self):
        """Check if there is an available step in the current path."""

        return self._client.has_next()

    def get_next(self):
        """Get the next step in the current path."""

        step = self._client.get_next()
        self.steps.append({
            "id": step["id"],
            "name": step["name"],
            "modelName": step["modelName"]
        })

        return step

    def get_data(self):
        """Get the current data values for the current model."""

        return self._client.get_data()

    def set_data(self, key, value):
        """Set data in the current model."""

        self._client.set_data(key, value)

    def restart(self):
        """Will rests the execution and the statistics."""

        self.steps = []

        self.failed_step = {}
        self.failed_fixtures = []

        self._client.restart()

    def fail(self, step, message):
        """Will mark the step as a failure and the current model."""

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

    def __init__(self, path):
        """Inits OfflinePlanner with sequence of steps.

        Args:
            path: A sequens of steps. A setep is a dict containing a ``name``
                and a ``modelName``.
        """

        self._path = list(path)
        self._position = 0

        self.failed_step = {}
        self.failed_fixtures = []

    @property
    def steps(self):
        """Return a sequence of executed steps."""

        return self._path[:self._position]

    @property
    def path(self):
        """Return the path, the original sequence of steps."""

        return self._path

    @path.setter
    def path(self, path):
        self._path = path
        self.restart()

    def has_next(self):
        """Check if there are more element in path."""

        return self._position < len(self._path)

    def get_next(self):
        """Get the next element form the path."""

        step = self._path[self._position]
        self._position += 1

        return dict(step)

    def get_data(self):
        """Is not supported and will return an empty ``dict``."""

        return {}

    def set_data(self, key, value):
        """Is not supported and will thorow a warning."""

        warnings.warn(
            "The set_data and get_data are not supported in offline mode so calls to them have no effect.", UserWarning)

    def fail(self, step, message):
        """Will mark the step as a failure."""

        if "id" in step:
            self.failed_step = step
        else:
            self.failed_fixtures.append(step)

    def restart(self):
        """Will rests the executed steps sequence and the statistics."""

        self.failed_step = {}
        self.failed_fixtures = []

        self._position = 0

    def get_statistics(self):
        return {
            "steps": self.steps,
            "failedStep": self.failed_step,
            "failedFixtures": self.failed_fixtures
        }

    def kill(self):
        pass


def create_planner(models=None, steps=None, port=8887, verbose=False, unvisited=False,
                   blocked=False):
    if steps:
        return OfflinePlanner(steps)

    service = GraphWalkerService(port=port, models=models,
                                 unvisited=unvisited, blocked=blocked)
    client = GraphWalkerClient(port=port, verbose=verbose)

    return OnlinePlanner(service, client)
