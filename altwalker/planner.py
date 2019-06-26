import warnings

from altwalker.graphwalker import GraphWalkerService, GraphWalkerClient


class OnlinePlanner:
    """Plan a path using the GraphWalker REST service and client.

    The path generation is done at run-time, one step at a time, using
    the GraphWalker REST Service. This adds a bit of complexity, but
    the advantages is that you can interact with the graph data using
    :func:`get_data` and :func:`set_data` methods.

    Note:
        The planner requires the GraphWalker service to be started with
        the ``verbouse`` flag.
    """

    def __init__(self, client, service=None):
        self._service = service
        self._client = client

    def kill(self):
        """Stop the GraphWalkerService process if needed."""

        if self._service:
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

        return step

    def get_data(self):
        """Get the current data values for the current model."""

        return self._client.get_data()

    def set_data(self, key, value):
        """Set data in the current model."""

        self._client.set_data(key, value)

    def restart(self):
        """Will rests the execution and the statistics."""

        self._client.restart()

    def fail(self, message):
        """Will mark the step as a failure and the current model."""

        self._client.fail(message)

    def get_statistics(self):
        statistics = self._client.get_statistics()

        return statistics


class OfflinePlanner:
    """Plan a path from a list of steps.

    Args:
        path: A sequens of steps. A setep is a dict containing a ``name``
            and a ``modelName``.
    """

    def __init__(self, path):
        self._path = list(path)
        self._position = 0

    @property
    def steps(self):
        """Return a sequence of executed steps."""

        return list(self._path[:self._position])

    @property
    def path(self):
        """Return the path, the original sequence of steps."""

        return list(self._path)

    @path.setter
    def path(self, path):
        self._path = list(path)
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
        """Is not supported and will throw a warning."""

        warnings.warn(
            "The set_data and get_data are not supported in offline mode so calls to them have no effect.", UserWarning)

    def fail(self, message):
        """This method does nothing."""

    def restart(self):
        """Will rests the executed steps sequence and the statistics."""

        self._position = 0

    def get_statistics(self):
        """This method returns an empty ``dict``."""

        return {}

    def kill(self):
        """This method does nothing."""


def create_planner(models=None, steps=None, host=None, port=8887, start_element=None,
                   verbose=False, unvisited=False, blocked=False):
    """Create a planner object.

    Args:
        models (:obj:`list`): A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        steps (:obj:`list`): If step is set will create a :class:`OfflinePlanner`.
        host (:obj:`str`): If the host is set will not start a GraphWalker service (e.g. `127.0.0.1`).
        port (:obj:`int`): The port of the GraphWalker service, to start on or to listen (e.g. 8887).
        start_element (:obj:`str`): A starting element for the first model.
        verbose (:obj:`bool`): If set will start the GraphWalker service with the verbose flag.
        unvisited (:obj:`bool`): If set will start the GraphWalker service with the unvisited flag.
        blocked (:obj:`bool`): If set will start the GraphWalker service with the blocked flag.

    Note:
        If the ``host`` or ``steps`` parameters are set ``models``, ``verbose``, ``unvisited``
        and ``blocked`` have no effect.

    Note:
        If you start a GraphWalker service start it with the ``verbouse`` flag.
    """

    if steps:
        return OfflinePlanner(steps)

    if host:
        client = GraphWalkerClient(host=host, port=port, verbose=verbose)
        return OnlinePlanner(client)

    service = GraphWalkerService(port=port, models=models, start_element=start_element,
                                 unvisited=unvisited, blocked=blocked)
    client = GraphWalkerClient(port=port, verbose=verbose)

    return OnlinePlanner(client, service=service)
