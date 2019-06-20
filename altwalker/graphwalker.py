import subprocess
import logging
import time
import json

import requests

from altwalker._utils import kill, get_command
from altwalker.exceptions import GraphWalkerException

logger = logging.getLogger(__name__)


def _create_command(command_name, model_path=None, models=None, port=None, service=None, start_element=None,
                    verbose=False, unvisited=False, blocked=None):
    """Create a list containing the executable, command and the list of options for a GraphWalker command.

    Args:
        command_name: The name of the GraphWalker command.
        model_path: A path to a model.
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        port: The port number.
        services: The type of service to run, RESTFUL or WEBSOCKET.
        start_element: A starting element for the first model.
        verbose: Run the command with the verbose flag.
        unvisited: Run the command with the unvisited flag.
        blocked: Run the command with the blcoked flag.

    Returns:
        A list containing the executable followed command and options.
    """

    command = get_command("gw")
    command.append(command_name)

    if model_path:
        command.extend(("--model", model_path))

    if models:
        for path, stop_condition in models:
            command.extend(("--model", path, stop_condition))

    if port:
        command.extend(("--port", str(port)))

    if service:
        command.extend(("--service", service))

    if start_element:
        command.extend(("--start-element", start_element))

    if verbose:
        command.append("--verbose")

    if unvisited:
        command.append("--unvisited")

    if blocked is not None:
        command.extend(("--blocked", str(blocked)))

    return command


def _execute_command(command, model_path=None, models=None, start_element=None, verbose=False, unvisited=False,
                     blocked=None):
    """Execute a GraphWalker commands that return output like offline and check.

    Args:
        command: The name of the GraphWalker command.
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        start_element: A starting element for the first model.
        verbose: Run the command with the verbose flag.
        unvisited: Run the command with the unvisited flag.
        blocked: Run the command with the blcoked flag.

    Returns:
        Return the output of the command.

    Raises:
        GraphWalkerException: If GraphWalker return an error.
    """

    command = _create_command(command, model_path=model_path, models=models, start_element=start_element,
                              verbose=verbose, unvisited=unvisited, blocked=blocked)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        error = error.decode("utf-8")
        raise GraphWalkerException(
            "GraphWalker responded with the error: `{}`.".format(error))

    return output.decode("utf-8")


def offline(models, start_element=None, verbose=False, unvisited=False, blocked=None):
    """Execute the offline command.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        start_element: A starting element for the first model.
        verbose: Run the command with the verbose flag.
        unvisited: Run the command with the unvisited flag.
        blocked: Run the command with the blcoked flag.

    Returns:
        Return a list of steps.

    Raises:
        GraphWalkerException: If an error occured while running the command, or
            the command outputs to ``stderr``.
    """

    # Always call the commmand with the verbose flag to get the modelName for each step
    output = _execute_command("offline", models=models, start_element=start_element,
                              verbose=True, unvisited=unvisited, blocked=blocked)

    steps = []
    for line in output.split("\n"):
        if line:
            step = json.loads(line)

            if not verbose:
                step.pop("data", None)
                step.pop("properties", None)

            if verbose:
                step["data"] = {k: v for data in step["data"] for k, v in data.items()}

            step["id"] = step.pop("currentElementID")
            step["name"] = step.pop("currentElementName")

            steps.append(step)

    return steps


def check(models, blocked=None):
    """Execute the check command.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        blocked: Run the command with the blcoked flag.

    Returns:
        Returns the output form GraphWalker check.

    Raises:
        GraphWalkerException: If an error occured while running the command, or
            the command outputs to ``stderr``.
    """

    return _execute_command("check", models=models, blocked=blocked)


def methods(model_path, blocked=False):
    """Execute the methods command.

    Args:
        model_path: A path to a model.
        blcked: Run the command with the blcoked flag.

    Returns:
        A list of unique names of vertices and edges in the model.

    Raises:
        GraphWalkerException: If an error occured while running the command, or
            the command outputs to ``stderr``.
    """

    output = _execute_command("methods", model_path=model_path, blocked=blocked)
    return output.strip("\n").split("\n")


class GraphWalkerService:
    """Starts and kills a proccess running the GraphWalker REST service."""

    def __init__(self, models=None, port=8887, unvisited=False, blocked=False, output_file="graphwalker-service.log"):
        """Will run the GraphWalker online command and start the GraphWalker REST service.

        Note:
            The GraphWalker REST Service is always started with the verbose flag to get the
            ``modelName`` for each step.

        Args:
            port: Will start the service on the given port.
            unvisited: Will start the service with the unvisited flag set to True.
            blocked: Will start the service with the blocked flag set to True.
            output_file: If set will save the output of the command in a file.
        """

        self.port = port
        self.output_file = output_file

        command = _create_command("online", models=models, port=port, service="RESTFUL",
                                  verbose=True, unvisited=unvisited, blocked=blocked)

        logger.debug("Starting GraphWalker Service on port: {}".format(self.port))
        logger.debug("Command: {}".format(command))

        self._process = subprocess.Popen(
            command, stdout=open(output_file, "w"), stderr=subprocess.STDOUT)

        self._read_logs()

    def _read_logs(self):
        """Read logs to check if the service started correctly."""

        fp = open(self.output_file)

        while 1:
            where = fp.tell()
            line = fp.readline()
            if not line:
                time.sleep(0.1)
                fp.seek(where)
            else:
                if "[HttpServer] Started" in line:
                    break

            if self._process.poll() is not None:
                logger.debug("Could not start GraphWalker Service on port: {}.".format(self.port))
                logger.debug("Process exit code: {}".format(self._process.poll()))

                raise GraphWalkerException(
                        "Could not start GraphWalker Service on port: {}\nCheck the log file at: {}"
                        .format(self.port, self.output_file))

        fp.close()

    def kill(self):
        """Send the SIGINT signal to the GraphWalker service to kill the process and free the port."""

        logger.debug("Kill the GraphWalker Service on port: {}".format(self.port))
        kill(self._process.pid)


class GraphWalkerClient:
    """A client for the GraphWalker REST service."""

    def __init__(self, host="127.0.0.1", port=8887, verbose=False):
        """Inits the GraphWalkerClient.

        Note:
            Because the GraphWalker REST service is always started with the verbouse flag,
            the client by default will filter out the ``data`` and ``properties``
            for ``get_next``.

        Args:
            host: The ip address of the GraphWalker REST service.
            port: The port of the GraphWalker REST servie.
            verbose: If set will not filter out the ``data`` and ``properties``
                for ``get_next``.
        """

        self.host = host
        self.port = port

        self.verbose = verbose

        self.base = "http://" + host + ":" + str(port) + "/graphwalker"

    def _validate_response(self, response):
        if not response.status_code == 200:
            raise GraphWalkerException(
                "GraphWalker responded with status code: {}.".format(str(response.status_code)))

    def _get_body(self, response):
        body = response.json()

        if body["result"] == "ok":
            body.pop("result")
            return body

        if "error" in body:
            raise GraphWalkerException(
                "GraphWalker responded with the error: {}.".format(body["error"]))

        if body["result"] == "nok":
            raise GraphWalkerException(
                "GraphWalker responded with an nok status.")

        raise GraphWalkerException(
            "GraphWalker did not respond with an ok status.")

    def _get(self, path):
        response = requests.get(self.base + path)
        self._validate_response(response)
        return self._get_body(response)

    def _put(self, path):
        response = requests.put(self.base + path)
        self._validate_response(response)
        return self._get_body(response)

    def _post(self, path, data=None):
        response = requests.post(self.base + path, data=data)
        self._validate_response(response)
        return self._get_body(response)

    def load(self, model):
        """Call POST/load."""

        self._post("/load", data=json.dumps(model))

    def has_next(self):
        """Call GET/hasNext, and return the response."""

        body = self._get("/hasNext")
        return body["hasNext"] == "true"

    def get_next(self):
        """Call GET/getNext, and return the next step."""

        step = self._get("/getNext")

        if not self.verbose:
            step.pop("data", None)
            step.pop("properties", None)

        if self.verbose:
            step["data"] = {k: v for data in step["data"] for k, v in data.items()}

        step["id"] = step.pop("currentElementID")
        step["name"] = step.pop("currentElementName")

        return step

    def get_data(self):
        """Call GET/getData, and return the data."""

        body = self._get("/getData")
        return body["data"]

    def set_data(self, key, value):
        """Call PUT/setData."""

        if isinstance(value, str):
            normalize = "\"" + value + "\""
        else:
            normalize = str(value)

        self._put("/setData/" + key + "=" + normalize)

    def restart(self):
        """Call PUT/restart."""

        self._put("/restart")

    def fail(self, message):
        """Call PUT/fail."""

        requests.put(self.base + "/fail/" + message)

    def get_statistics(self):
        """Call GET/getStatistcs, and return the statistcs."""

        return self._get("/getStatistics")
