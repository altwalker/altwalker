#    Copyright(C) 2023 Altom Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

"""A collection of function and class that interact with the Graphwalker command and REST service."""

import json
import logging
import os
import re
import time
import urllib.parse

import requests

from altwalker._utils import (Command, execute_command, get_resource_path,
                              has_command, url_join)
from altwalker.exceptions import GraphWalkerException

logger = logging.getLogger(__name__)

LOG_LEVEL_MAP = {
    "NOTSET": "ALL",
    "CRITICAL": "TRACE",
    "ERROR": "ERROR",
    "WARNING": "WARN",
    "INFO": "INFO",
    "DEBUG": "DEBUG",
}


def _get_log_level(level):
    """Map a Python log level to an equivalent GraphWalker log level."""

    return LOG_LEVEL_MAP.get(level.upper(), "OFF")


def _get_error_message(logs):
    """Get the error message from GraphWalker logs."""

    result = re.search(r"An error occurred when running command:.*[\r\n]+([^\r\n]+)", logs)
    if result:
        return result.group(1)

    return None


def _normalize_step(step, verbose=False):
    """Normalize the step returned by the ``getNext`` request or the offline command."""

    normalized_step = {}

    if verbose:
        normalized_step["data"] = {k: v for data in step["data"] for k, v in data.items()}
        normalized_step["properties"] = step.get("properties")

    if step.get("actions"):
        normalized_step["actions"] = [action.get("Action") for action in step["actions"]]

    normalized_step["id"] = step.get("currentElementID")
    normalized_step["name"] = step.get("currentElementName")
    normalized_step["modelName"] = step.get("modelName")

    return normalized_step


def _create_command(command_name, model_path=None, models=None, port=None, service=None, start_element=None,
                    verbose=False, unvisited=False, blocked=None, debug=None):
    """Create a list containing the executable, command and the list of options for a GraphWalker command.

    Args:
        command_name (:obj:`str`): The name of the GraphWalker command.
        model_path (:obj:`str`): A path to a model.
        models (:obj:`list`): A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        port (:obj:`int`): The port number.
        services (:obj:`str`): The type of service to run, RESTFUL or WEBSOCKET.
        start_element (:obj:`str`): A starting element for the first model.
        verbose (:obj:`bool`): Run the command with the verbose flag.
        unvisited (:obj:`bool`): Run the command with the unvisited flag.
        blocked (:obj:`bool`): Run the command with the blocked flag.
        debug (:obj:`str`): Sets the log level.

    Returns:
        list: A list containing the executable followed command and options.
    """

    if has_command(["gw", "--version"], timeout=1):
        command = ["gw"]
    else:
        command = ["java", "-jar", get_resource_path("data/graphwalker/graphwalker-cli.jar")]

    if debug:
        command.extend(("--debug", _get_log_level(debug)))

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
    """Execute a GraphWalker commands and return the output.

    Args:
        command (:obj:`str`): The name of the GraphWalker command.
        models (:obj:`list`): A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        start_element (:obj:`str`): A starting element for the first model.
        verbose (:obj:`bool`): Run the command with the verbose flag.
        unvisited (:obj:`bool`): Run the command with the unvisited flag.
        blocked (:obj:`bool`): Run the command with the blocked flag.

    Returns:
        string: The output of the command.

    Raises:
        GraphWalkerException: If GraphWalker return an error.
    """

    full_command = _create_command(command, model_path=model_path, models=models, start_element=start_element,
                                   verbose=verbose, unvisited=unvisited, blocked=blocked)

    logger.debug(f"Executed command: '{' '.join(full_command)}'.")
    output, error = execute_command(full_command)

    logger.debug(f"Output: '{output}'")
    logger.debug(f"Error: '{error}'")

    if error:
        error = error.decode("utf-8").strip()
        raise GraphWalkerException(error)

    return output.decode("utf-8")


def get_version():
    """Retrieves the version of the GraphWalker command by executing the "gw --version" command.

    Returns:
        A tuple representing the version, where the first three elements are the major,
        minor, and patch version numbers (as strings), and the remaining elements are any
        additional version information (such as a release candidate or build number).

    Example:
        >>> get_version()
        (4, 3, 3, 'SNAPSHOT', '21bb711')

    """

    output = _execute_command("--version").split(os.linesep)[0]

    version_string = output.rpartition(":")[-1].strip()
    version, *suffix = version_string.split("-")
    version = (int(x) for x in version.split("."))

    return (*version, *suffix)


def check(models, blocked=None):
    """Execute the check command.

    Args:
        models (:obj:`list`): A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        blocked (:obj:`bool`): Run the command with the blocked flag.

    Returns:
        str: The output form GraphWalker check.

    Raises:
        GraphWalkerException: If an error occurred while running the command, or
            the command outputs to ``stderr``.
    """

    return _execute_command("check", models=models, blocked=blocked)


def methods(model_path, blocked=False):
    """Execute the methods command.

    Args:
        model_path (:obj:`list`): A path to a model.
        blocked (:obj:`bool`): Run the command with the blocked flag.

    Returns:
        list: A sequence of all unique names of vertices and edges in the model.

    Raises:
        GraphWalkerException: If an error occurred while running the command, or
            the command outputs to ``stderr``.
    """

    output = _execute_command("methods", model_path=model_path, blocked=blocked)

    if output:
        return output.strip(os.linesep).split(os.linesep)

    return []


def _parse_offline_output(output, verbose=False):
    """Parse the output of the offline command into a list of steps."""

    steps = []
    for line in output.split(os.linesep):
        if line:
            step = json.loads(line)
            steps.append(_normalize_step(step, verbose=verbose))

    return steps


def offline(models, start_element=None, verbose=False, unvisited=False, blocked=None):
    """Execute the offline command.

    Args:
        models (:obj:`list`): A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        start_element (:obj:`str`): A starting element for the first model.
        verbose (:obj:`bool`): Run the command with the verbose flag.
        unvisited (:obj:`bool`): Run the command with the unvisited flag.
        blocked (:obj:`bool`): Run the command with the blocked flag.

    Returns:
        list: A sequence of steps.

    Raises:
        GraphWalkerException: If an error occurred while running the command, or
            the command outputs to ``stderr``.
    """

    # Always call the command with the verbose flag to get the modelName for each step
    output = _execute_command("offline", models=models, start_element=start_element,
                              verbose=True, unvisited=unvisited, blocked=blocked)

    return _parse_offline_output(output, verbose=verbose)


class GraphWalkerService:
    """Starts and kills a process running the GraphWalker REST service.

    Will run the GraphWalker online command and start the GraphWalker REST service.

    Note:
        The GraphWalker REST Service is always started with the verbose flag to get the
        ``modelName`` for each step.

    Args:
        models (:obj:`list`): A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        port (:obj:`int`): Will start the service on the given port.
        start_element (:obj:`str`): A starting element for the first model.
        unvisited (:obj:`bool`): Will start the service with the unvisited flag set to True.
        blocked (:obj:`bool`): Will start the service with the blocked flag set to True.
        output_file (:obj:`str`): If set will save the output of the command in a file.
    """

    def __init__(self, models=None, port=8887, start_element=None, unvisited=False, blocked=False,
                 output_file="graphwalker-service.log"):

        self.port = port
        self.output_file = output_file

        self.debug = os.environ.get("GRAPHWALKER_LOG_LEVEL")

        command = _create_command("online", models=models, port=port, service="RESTFUL", start_element=start_element,
                                  verbose=True, unvisited=unvisited, blocked=blocked, debug=self.debug)

        self._process = Command(command, self.output_file)

        logger.debug(f"GraphWalker Service started with command: {' '.join(command)}")
        logger.debug(f"GraphWalker Service running on port: {self.port}")
        logger.debug(f"GraphWalker Service running with pid: {self._process.pid}")

        # Ignore bare 'except' error because we re-raise the exception.
        try:
            self._read_logs()
        except:  # noqa: E722
            self.kill()
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.kill()

    def _read_logs(self):
        """Read logs to check if the service started correctly."""

        with open(self.output_file) as fp:
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
                    self._raise_error()

    def _get_error_message(self):
        """Read logs to get the error message."""

        with open(self.output_file) as fp:
            return _get_error_message(fp.read())

    def _raise_error(self):
        error = self._get_error_message()

        logger.error(f"Could not start GraphWalker Service on port: {self.port}")
        logger.error(f"Process exit code: {self._process.poll()}")
        if error:
            logger.error(f"GraphWalker Service Error: {error}")

        more_info = f"For more information check the log file at: {self.output_file}"

        if error:
            raise GraphWalkerException(
                f"An error occurred while trying to start the GraphWalker Service on port: {self.port}\n{error}\n\n"
                f"{more_info}"
            )

        raise GraphWalkerException(f"Could not start the GraphWalker Service on port: {self.port}\n\n{more_info}")

    def kill(self):
        """Send the SIGINT signal to the GraphWalker service to kill the process and free the port."""

        logger.debug(f"Killing the GraphWalker Service on port: {self.port}")
        self._process.kill()


class GraphWalkerClient:
    """A client for the GraphWalker REST service.

    Note:
        Because the GraphWalker REST service is always started with the verbose flag,
        the client by default will filter out the ``data`` and ``properties``
        from the output of ``get_next``.

    Args:
        host (:obj:`str`): The host address of the GraphWalker REST service.
        port (:obj:`int`): The port of the GraphWalker REST service.
        verbose (:obj:`bool`): If set will not filter out the ``data`` and ``properties``
            from the output of ``get_next``.
    """

    def __init__(self, host="127.0.0.1", port=8887, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose

        self.base = f"http://{host}:{port}/graphwalker"
        logger.debug(f"Initializing a GraphWalkerClient on host: {self.base}")

    def _normalize_fail_message(self, message):
        """Make fail message safe for use a port of an URL."""

        if not message:
            message = "Unknown error."

        return urllib.parse.quote(message, safe="")

    def _normalize_data(self, key, value):
        """Make data safe for use as a port of an URL."""

        if isinstance(value, bool):
            # convert python boolean value to javascript boolean value
            normalized_value = "true" if value else "false"
        elif isinstance(value, str):
            normalized_value = f"\"{value}\""
        else:
            normalized_value = str(value)

        normalized_key = urllib.parse.quote(key, safe="")
        normalized_value = urllib.parse.quote(normalized_value, safe="")

        return normalized_key, normalized_value

    def _validate_response(self, response):
        if not response.status_code == 200:
            raise GraphWalkerException(f"GraphWalker responded with status code: {response.status_code}.")

    def _get_body(self, response):
        body = response.json()

        if body["result"] == "ok":
            body.pop("result")
            return body

        if "error" in body:
            raise GraphWalkerException(f"GraphWalker responded with the error: {body['error']}.")

        if body["result"] == "nok":
            raise GraphWalkerException(
                "GraphWalker responded with an nok status.")

        raise GraphWalkerException(
            "GraphWalker did not respond with an ok status.")

    def _get(self, path):
        response = requests.get(url_join(self.base, path))
        self._validate_response(response)
        return self._get_body(response)

    def _put(self, path):
        response = requests.put(url_join(self.base, path))

        self._validate_response(response)
        return self._get_body(response)

    def _post(self, path, data=None):
        response = requests.post(url_join(self.base, path), data=data)
        self._validate_response(response)
        return self._get_body(response)

    def load(self, model):
        """Loads a new model(s) in JSON format.

        Make a POST request at ``/load``.

        Args:
            model (:obj:`dict`): The JSON model.
        """

        logger.debug(f"Host {self.base} loads a new model")
        self._post("/load", data=json.dumps(model))

    def has_next(self):
        """Returns True if a new step is available. If True, then the fulfillment
        of the stop conditions has not yet been reached.

        Makes a GET request at ``/hasNext``.

        Returns:
            bool: True if a new step is available, False otherwise.
        """

        body = self._get("/hasNext")
        return body["hasNext"] == "true"

    def get_next(self):
        """Returns the next step from the path.

        Makes a GET request at ``/getNext``.

        Returns:
            dict: Depending of how the GraphWalker Service was started ``get_next`` will return different responses.

            * With the verbose flag::

                {
                    "id": step_id,
                    "name": step_name,
                    "modelName": model_name,
                    "data": [],
                    "properties": {}
                }

            * With the unvisited flag::

                {
                    "id": step_id,
                    "name": step_name,
                    "modelName": model_name,
                    "numberOfElements": number_of_element,
                    "numberOfUnvisitedElements": number_of_unvisited_elements,
                    "unvisitedElements": []
                }
        """

        step = self._get("/getNext")
        return _normalize_step(step, verbose=self.verbose)

    def get_data(self):
        """Returns the graph data.

        Makes a GET request at ``/getData``.

        Returns:
            dict: The graph data.
        """

        body = self._get("/getData")
        return body["data"]

    def set_data(self, key, value):
        """Sets data in the current model.

        Makes a PUT request at ``/setData``.

        Args:
            key (:obj:`str`): The key to update.
            value (:obj:`str`, :obj:`int`, :obj:`bool`): The value to set.
        """

        logger.debug(f"Host {self.base} sets {key} = {value}")

        normalize_key, normalize_value = self._normalize_data(key, value)
        self._put(f"/setData/{normalize_key}={normalize_value}")

    def restart(self):
        """Reset the currently loaded model(s) to it’s initial state.

        Makes a PUT request at ``/restart``.
        """

        self._put("/restart")

    def fail(self, message):
        """Marks a fail in the current model.

        Makes a PUT request at ``/fail``.

        Args:
            message (:obj:`str`): The error message.
        """

        logger.debug(f"Host {self.base} failed with message: {message}")

        normalized_message = self._normalize_fail_message(message)
        response = requests.put(f"{self.base}/fail/{normalized_message}")
        self._validate_response(response)

    def get_statistics(self):
        """Returns the statistics for the current session.

        Makes a GET request at ``/getStatistics``.

        Returns:
            dict: The statistics.
        """

        return self._get("/getStatistics")
