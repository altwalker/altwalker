import os
import io
import sys
import abc
import time
import copy
import inspect
import traceback
import logging
import subprocess
import importlib
import importlib.util
from contextlib import redirect_stdout

import requests

from altwalker._utils import kill, get_command, url_join
from altwalker.exceptions import ExecutorException

logger = logging.getLogger(__name__)


def get_output(callable, *args, **kargs):
    """Call a callable object and return the output from stdout, error message and
    traceback if an error occurred.

    Args:
        callable: The callable object to call.
        *args: The list of args for the calable.
        **kargs: The dict of kargs for the callable.

    Returns:
        A dict containing the output of the callable, and the error message with the trace
        if an error occurred::

            {
                "output": "",
                "error": {
                    "message": "",
                    "trace": ""
                }
            }
    """

    result = {}
    output = io.StringIO()

    with redirect_stdout(output):
        try:
            callable(*args, **kargs)
        except Exception as e:
            result["error"] = {
                "message": str(e),
                "trace": str(traceback.format_exc())
            }

    result["output"] = output.getvalue()
    output.close()

    return result


def load(path, package, module):
    """Load a module form a package at a given path."""

    importlib.invalidate_caches()

    # load package
    spec = importlib.util.spec_from_file_location(package, os.path.join(path, package, "__init__.py"))
    loaded_module = spec.loader.load_module()
    spec.loader.exec_module(loaded_module)

    sys.modules[spec.name] = loaded_module

    # load module
    spec = importlib.util.spec_from_file_location(
        "{}.{}".format(package, module),
        os.path.join(path, package, "{}.py".format(module)))
    loaded_module = spec.loader.load_module()
    spec.loader.exec_module(loaded_module)

    return loaded_module


class Executor(metaclass=abc.ABCMeta):
    """An abstract class that defines the executor protocol."""

    @abc.abstractmethod
    def kill(self):
        """Cleanup resources and kill processes if needed."""

    @abc.abstractmethod
    def reset(self):
        """Reset the current execution."""

    @abc.abstractmethod
    def load(self, path):
        """Load the test code from a path.

        Args:
            path (:obj:`str`): The path to the test code.
        """

    @abc.abstractmethod
    def has_model(self, model_name):
        """Return True if the model is available.

        Args:
            model_name (:obj:`str`): The name of the model.

        Returns:
            bool: True if the model is available, False otherwise.
        """

    @abc.abstractmethod
    def has_step(self, model_name, name):
        """Return True if the step from the model is available.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.

        Note:
            If ``model_name`` is ``None`` the step is a fixture.

        Returns:
            bool: True if the step from the model is available, False otherwise.
        """

    @abc.abstractmethod
    def execute_step(self, model_name, name, data=None):
        """Execute a step from a model.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.
            data (:obj:`dict`): The current graph data.

        Note:
            If ``model_name`` is ``None`` the step is a fixture.

        Returns:
            dict: The graph data, the output of the step, and the error message with the trace
            if an error occurred::

                {
                    "output": "",
                    "data": {},
                    "error": {
                        "message": "",
                        "trace": ""
                    }
                }

            If no error occured the ``error`` key can be omitted or set to ``None``.

            If the graph data is not used or modiffied the ``data`` key can be omitted or set to ``None``.
        """


class HttpExecutor(Executor):
    """Http client for an executor service.

    Args:
        url (:obj:`str`): The URL of the executor service (e.g http://localhost:5000).
    """

    ERROR_CODES = {
        404: "Not Found",
        460: "Model Not Found",
        461: "Step Not Found",
        462: "Invalid Step Handler",
        463: "Path Not Found",
        464: "Load Error",
        465: "Test Code Not Loaded"
    }

    def __init__(self, url):
        self.url = url
        self.base = url_join(self.url, "altwalker/")

        logging.debug("Initate an HttpExecutor to connect to {} service".format(self.url))

    def _validate_response(self, response):
        if not response.status_code == 200:
            status_code = response.status_code
            error = response.json().get("error")

            error_type = self.ERROR_CODES.get(status_code, "Unknown Error")
            error_message = "The executor from {} responded with status code: {} {}.".format(
                self.url, status_code, error_type)

            if error:
                error_message += "\nMessage: {}\nTrace: {}".format(error["message"], error.get("trace"))

            raise ExecutorException(error_message)

    def _get_payload(self, response):
        try:
            body = response.json()
        except ValueError:
            body = {}

        return body.get("payload", {})

    def _get(self, path, params=None):
        response = requests.get(url_join(self.base, path), params=params)
        self._validate_response(response)

        return self._get_payload(response)

    def _put(self, path):
        response = requests.put(url_join(self.base, path))
        self._validate_response(response)

        return self._get_payload(response)

    def _post(self, path, params=None, data=None):
        HEADERS = {'Content-Type': 'application/json'}
        response = requests.post(url_join(self.base, path), params=params, json=data, headers=HEADERS)
        self._validate_response(response)

        return self._get_payload(response)

    def kill(self):
        """This method does nothing."""

    def load(self, path):
        """Makes a POST request at ``/load``.

        Args:
            path (:obj:`str`): The path to the test code.
        """

        self._post("load", data={"path": os.path.abspath(path)})

    def reset(self):
        """Makes an PUT at ``/reset``."""

        self._put("reset")

    def has_model(self, name):
        """Makes a GET request at ``/hasModel?modelName=<model_name>``.

        Args:
            model_name (:obj:`str`): The name of the model.

        Returns:
            bool: True if the model is available, False otherwise.
        """

        payload = self._get("hasModel", params={"name": name})
        has_model = payload.get("hasModel", None)

        if has_model is None:
            raise ExecutorException("Invaild response. The payload must include the key: hasModel.")

        return payload["hasModel"]

    def has_step(self, model_name, name):
        """Makes a GET request at ``/hasStep?modelName=<model_name>&name=<name>``.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.

        Returns:
            bool: True if the step from the model is available, False otherwise.
        """

        payload = self._get("hasStep", params={"modelName": model_name, "name": name})
        has_step = payload.get("hasStep", None)

        if has_step is None:
            raise ExecutorException("Invaild response. The payload must include the key: hasStep.")

        return has_step

    def execute_step(self, model_name, name, data=None):
        """Makes a POST request at ``/executeStep?modelName=<model_name>&name=<name>``.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.
            data (:obj:`dict`): The current graph data.

        Returns:
            dict: The graph data, the output of the step, and the error message with the
            trace if an error occurred::

                {
                    "output": "",
                    "data: {},
                    "error": {
                        "message": "",
                        "trace": ""
                    }
                }
        """

        payload = self._post("executeStep", params={"modelName": model_name, "name": name}, data=data)

        if payload.get("output") is None:
            raise ExecutorException("Invaild response. The payload must include the key: output.")

        return payload


class PythonExecutor(Executor):
    """Execute methods or functions from a model like object."""

    def __init__(self, module=None):
        self._module = module
        self._instances = {}

    def _get_instance(self, class_name):
        cls = getattr(self._module, class_name)
        return cls()

    def _setup_class(self, class_name):
        if class_name not in self._instances:
            self._instances[class_name] = self._get_instance(class_name)

    def _has_function(self, name):
        func = getattr(self._module, name, None)

        if callable(func):
            return True

        return False

    def _has_method(self, class_name, name):
        cls = getattr(self._module, class_name, None)

        if isinstance(cls, type):
            method = getattr(cls, name, None)

            if callable(method):
                return True

        return False

    def kill(self):
        """This method does nothing."""

    def load(self, path):
        self.reset()

        path, package = os.path.split(path)
        self._module = load(path, package, "test")

    def reset(self):
        self._instances = {}

    def has_model(self, name):
        """Check if the module has a class named ``name``.

        Args:
            name: The name of the class

        Returns:
            bool: True if the module has a class named `name`, False otherwise.
        """
        cls = getattr(self._module, name, None)

        if isinstance(cls, type):
            return True

        return False

    def has_step(self, model_name, name):
        """Check if the module has a class named ``model_name`` with a method named.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.

        Note:
            If ``model_name`` is ``None`` the step is a fixture.

        Returns:
            bool: True if the step from the model is available, False otherwise.
        """

        if model_name is None:
            return self._has_function(name)

        return self._has_method(model_name, name)

    def execute_step(self, model_name, name, data=None):
        """Execute a step from a model.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.
            data (:obj:`dict`): The current graph data.

        Note:
            If ``model_name`` is ``None`` the step is a fixture.

        Returns:
            A dict containing the graph data, the output of the step, and the error message with the trace
            if an error occurred::

                {
                    "output": "",
                    "data": {},
                    "error": {
                        "message": "",
                        "trace": ""
                    }
                }

            If no error occured the ``error`` key can be omitted or set to ``None``.

            If the graph data is not used or modiffied the ``data`` key can be omitted or set to ``None``.
        """

        data = copy.deepcopy(data) if data else {}

        if model_name is None:
            func = getattr(self._module, name)
            nr_args = len(inspect.getfullargspec(func).args)
        else:
            self._setup_class(model_name)

            func = getattr(self._instances[model_name], name)
            nr_args = len(inspect.getfullargspec(func).args) - 1  # substract the self argument of the method

        if nr_args == 0:
            output = get_output(func)
        elif nr_args == 1:
            output = get_output(func, data)
        else:
            func_name = "{}.{}".format(model_name, name) if model_name else name
            type_ = "method" if model_name else "function"

            error_message = "The {} {} must take {} or {} parameters but it expects {} parameters."

            raise ExecutorException(error_message.format(func_name, type_, 0, 1, nr_args))

        output["data"] = data
        return output


class DotnetExecutorService:
    """Starts a .NET executor service.

    * ``dotnet run -p <path>`` - is used to compile and run the console app project.
    * ``dotnet <path>`` - is used to run compiled exe or dll.

    Args:
        path: The path of the console application project, dll or exe, that starts an ``ExecutorService``.
        server_url: The url for the service to listen (e.g. http://localhost:5000/).
        output_file: A file for the output of the command.
    """

    def __init__(self, path, server_url, output_file="dotnet-executor.log"):
        self.path = path
        self.server_url = server_url
        self.output_file = output_file

        command = self._create_command(path, server_url)

        logger.debug("Starting .NET Executor Service from {} on `{}`".format(path,  server_url))
        logger.debug("Command: {}".format(" ".join(command)))

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
                if "Now listening on:" in line:
                    break

            if self._process.poll() is not None:
                logger.debug(
                    "Could not start .NET Executor service from {} on `{}`"
                    .format(self.path, self.server_url))
                logger.debug("Process exit code: {}".format(self._process.poll()))

                raise ExecutorException(
                    "Could not start .NET Executor service from {} on {}\nCheck the log file at: {}"
                    .format(self.path, self.server_url, self.output_file))

        fp.close()

    @staticmethod
    def _create_command(path, url):
        command = get_command("dotnet")

        if os.path.isdir(path):
            command.append("run")
            command.append("-p")

        command.append(path)
        command.append("--server.urls={}".format(url))

        return command

    def kill(self):
        """Kill the .NET executor service process.

        Note:
            If the path given was a project path and the service was started with `dotnet run`
            kills the main process and child process, because `dotnet run` starts the service
            in a child process.
        """

        logger.debug("Kill the .NET Executor Service from {} on {}".format(self.path, self.server_url))
        kill(self._process.pid)


class DotnetExecutor(HttpExecutor):
    """Starts a .NET executor service, and alows you to interact with it.

    Args:
        path: The path of the console application project, dll or exe, that starts an ``ExecutorService``.
        url: The url for the service to listen (e.g. http://localhost:5000/).
    """

    def __init__(self, path, url):
        super().__init__(url)

        self._service = DotnetExecutorService(path, url)

    def load(self, path):
        """Kill the executor service and start a new one with the given path."""

        logger.debug("Restart the .NET Executor service from {} on {}".format(path, self.base))

        self._service.kill()
        self._service = DotnetExecutorService(path, self.base)

    def kill(self):
        """Kill the executor service."""

        self._service.kill()


def create_http_executor(path, url):
    """Creates a HTTP executor."""

    executor = HttpExecutor(url)
    executor.load(path)

    return executor


def create_dotnet_executor(path, url):
    """Creates a .NET executor."""

    return DotnetExecutor(path, url)


def create_python_executor(path):
    """Creates a Python executor."""

    path, package = os.path.split(path)
    module = load(path, package, "test")

    return PythonExecutor(module)


def create_executor(path, type_, url=None):
    """Creates an executor.

    Args:
        path: The path to the tests.
        type_: The type of the executor (e.g. http, python, dotnet).
        url: The url for the executor service.

    Raises:
        ValueError: If the ``type_`` is not supported.
    """

    if type_ == "http":
        return create_http_executor(path, url)
    elif type_ == "python":
        return create_python_executor(path)
    elif type_ == "dotnet" or type_ == "c#":
        return create_dotnet_executor(path, url)
    else:
        raise ValueError("{} is not a supported executor type.".format(type_))
