import subprocess
import platform
import json
import signal
import os

import psutil
import requests


class GraphWalkerException(Exception):
    pass


def _kill(pid):
    """Send the SIGINT signal to a process and all its children."""
    process = psutil.Process(pid)

    for child in process.children(recursive=True):
        os.kill(child.pid, signal.SIGINT)

    os.kill(process.pid, signal.SIGINT)


class GraphWalkerService:
    """Stops and kills a proccess running the GraphWalker REST service."""

    def __init__(self, models=None, port=8887, verbose=True, unvisited=False, blocked=False, output_file=None):
        command = _create_command("online", models=models, port=port, service="RESTFUL",
                                  verbose=verbose, unvisited=unvisited, blocked=blocked)

        self._process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=-1)
        self._wait_for_process_to_start(output_file)

    def _wait_for_process_to_start(self, output_file):
        success = False

        while True:
            # if gw process keeps on running and does not print `[HttpServer] Started` readline will hang
            line = self._process.stdout.readline().decode("utf-8")
            if output_file:
                output_file.write(line)

            if "[HttpServer] Started" in line:
                success = True
                break

            if line == "":
                break

        if not success:
            raise GraphWalkerException("Could not start GraphWalker Service")

    def kill(self):
        """Send the SIGINT signal to the GraphWalker service to kill the process and free the port."""
        _kill(self._process.pid)


class GraphWalkerClient:
    """A client for the GraphWalker REST service."""

    def __init__(self, host="127.0.0.1", port=8887):
        self.host = host
        self.port = port

        self.base = "http://" + host + ":" + str(port) + "/graphwalker"

    def _validate_response(self, response):
        if response.status_code is not 200:
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
        self._post("/load", data=json.dumps(model))

    def has_next(self):
        body = self._get("/hasNext")
        return body["hasNext"] == "true"

    def get_next(self):
        body = self._get("/getNext")

        return {
            "modelName": body["modelName"],
            "name": body["currentElementName"],
            "id": body["currentElementID"],
        }

    def get_data(self):
        body = self._get("/getData")
        return body["data"]

    def set_data(self, key, value):
        if isinstance(value, str):
            normalize = "\"" + value + "\""
        else:
            normalize = str(value)

        self._put("/setData/" + key + "=" + normalize)

    def restart(self):
        self._put("/restart")

    def fail(self, message):
        requests.put(self.base + "/fail/" + message)

    def get_statistics(self):
        return self._get("/getStatistics")


def _get_graphwalker_executable():
    command = ["cmd.exe", "/C"] if platform.system() == "Windows" else []
    command.append("gw")
    return command


def _create_command(command_name, model_path=None, models=None, port=None, service=None, start_element=None, verbose=False, unvisited=False, blocked=None):
    """Create a list containing the executable, command and the list of options for a GraphWalker command.

    Args:
        command_name: The name of the GraphWalker command.
        model_path: A path to a model.
        models: A sequence of tuples containing the model_path and the stop_condition.
        port: The port number.
        services: The type of service to run, RESTFUL or WEBSOCKET.
        start_element: A starting element for the first model.
        verbose: Run the command with the verbose flag.
        unvisited: Run the command with the unvisited flag.
        blocked: Run the command with the blcoked flag.

    Returns:
        A list containing the executable followed command and options.
    """

    command = _get_graphwalker_executable()
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


def _execute_command(command, model_path=None, models=None, start_element=None, verbose=False, unvisited=False, blocked=None):
    """Execute a GraphWalker commands that return output like offline and check.

    Args:
        command: The name of the GraphWalker command.
        models: A sequence of tuples containing the model_path and the stop_condition.
        start_element: A starting element for the first model.
        verbose: Run the command with the verbose flag.
        unvisited: Run the command with the unvisited flag.
        blocked: Run the command with the blcoked flag.

    Returns:
        Return the output of the command.

    Raises:
        GraphWalkerException: If GraphWalker return an error.
    """
    command = _create_command(command, model_path=model_path, models=models, start_element=start_element, verbose=verbose, unvisited=unvisited, blocked=blocked)
    process = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        error = error.decode("utf-8")
        raise GraphWalkerException(
            "GraphWalker responded with the error: {}.".format(error))

    return output.decode("utf-8")


def offline(models, start_element=None, verbose=False, unvisited=False, blocked=None):
    """Execute the offline command.

    Args:
        models: A sequence of tuples containing the model_path and the stop_condition
        start_element: A starting element for the first model.
        verbose: Run the command with the verbose flag.
        unvisited: Run the command with the unvisited flag.
        blocked: Run the command with the blcoked flag.

    Returns:
        Return a list of steps.
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

            step["id"] = step.pop("currentElementID")
            step["name"] = step.pop("currentElementName")

            steps.append(step)

    return steps


def check(models, blocked=None):
    """Execute the check command.

    Args:
        models: A sequence of tuples containing the model_path and the stop_condition
        blocked: Run the command with the blcoked flag.

    Returns:
        Returns the output form GraphWalker check.
    """
    return _execute_command("check", models=models, blocked=blocked)


def methods(model_path, blocked=False):
    """Execute the methods command.

    Args:
        model_path: A path to a model.
        blcked: Run the command with the blcoked flag.

    Returns:
        A list of unique names of vertices and edges in the model.
    """
    output = _execute_command("methods", model_path=model_path, blocked=blocked)
    return output.strip("\n").split("\n")