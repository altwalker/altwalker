import os
import io
import time
import sys
import copy
import inspect
import traceback
import importlib
import importlib.util
import subprocess
from contextlib import redirect_stdout

import requests

from altwalker._utils import kill, get_command
from altwalker.exceptions import ExecutorException


def get_output(callable, *args, **kargs):
    """Call a callable object and return the output from stdout, error message and
    traceback if an error occurred.
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

    # load package
    spec = importlib.util.spec_from_file_location(package, os.path.join(path, package, "__init__.py"))
    loaded_module = spec.loader.load_module()
    spec.loader.exec_module(loaded_module)

    sys.modules[spec.name] = loaded_module

    # load module
    spec = importlib.util.spec_from_file_location(package + "." + module, os.path.join(path, package, module + ".py"))
    loaded_module = spec.loader.load_module()
    spec.loader.exec_module(loaded_module)

    return loaded_module


class Executor:
    """Default executor."""

    def kill(self):
        """Cleanup resources and kill processes if needed."""

    def reset(self):
        """Reset the current execution."""

    def load(self, path):
        """Load the test code from a path."""

    def has_model(self, model_name):
        """Return true if the model is availabel."""

    def has_step(self, model_name, name):
        """Return true if the step from the model is availabel.

        Note:
            If ``model_name`` is ``None`` the step is a fixture.
        """

    def execute_step(self, model_name, name, data=None):
        """Execute a step from a model.

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


class HttpExecutor(Executor):
    """Http client for an executor service."""

    ERROR_CODES = {
        404: "Not Found",
        460: "Model Not Found",
        461: "Step Not Found",
        462: "Invalid Step Handler",
        463: "Path Not Found",
        464: "Load Error",
        465: "Test Code Not Loaded"
    }

    def __init__(self, host="127.0.0.1", port=5000):
        """Initialize an HttpExecutor with the ``host`` and ``port`` of the executor service."""

        self.host = host
        self.port = port

        self.base = "http://{}:{}/altwalker/".format(host, port)

    def _validate_response(self, response):
        if not response.status_code == 200:
            status_code = response.status_code
            error = response.json().get("error", None)

            error_type = self.ERROR_CODES.get(status_code, "Unknown Error")
            error_message = "The executor from {} responded with status code: {} {}.".format(
                self.base, status_code, error_type)

            if error:
                error_message += "\nMessage: {}\nTrace: {}".format(error["message"], error["trace"])

            raise ExecutorException(error_message)

    def _get_body(self, response):
        body = response.json()
        return body.get("payload", {})

    def _get(self, path, params=None):
        response = requests.get(self.base + path, params=params)
        self._validate_response(response)

        return self._get_body(response)

    def _put(self, path):
        response = requests.put(self.base + path)
        self._validate_response(response)

        return self._get_body(response)

    def _post(self, path, params=None, data=None):
        HEADERS = {'Content-Type': 'application/json'}
        response = requests.post(self.base + path, params=params, json=data, headers=HEADERS)
        self._validate_response(response)

        return self._get_body(response)

    def load(self, path):
        """Makes a POST request at ``/altwalker/load```."""

        self._post("load", data={"path": path})

    def reset(self):
        """Makes an PUT at ``/altwalker/reset``."""

        self._put("reset")

    def has_model(self, name):
        """Makes a GET  request at ``/altwalker/hasModel?name=<name>``.

        Returns:
            True, if the executor has the model, False otherwise.
        """

        payload = self._get("hasModel", params=(("name", name)))
        has_model = payload.get("hasModel", None)

        if has_model is None:
            raise ExecutorException("Invaild response. The payload must include the key: hasModel.")

        return payload["hasModel"]

    def has_step(self, model_name, name):
        """Makes a GET request at ``/altwalker/hasStep?modelName=<model_name>&name=<name>``.

        Returns:
            True, if the executor has the step, False otherwise.
        """

        payload = self._get("hasStep", params=(("modelName", model_name), ("name", name)))
        has_step = payload.get("hasStep", None)

        if has_step is None:
            raise ExecutorException("Invaild response. The payload must include the key: hasStep.")

        return has_step

    def execute_step(self, model_name, name, data=None):
        """Makes a POST request at ``/altwalker/executeStep?modelName=<model_name>&name=<name>``.

        Returns:
            A ``dict`` containing the graph data, the output of the step, and the error message with the
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

        payload = self._post("executeStep", params=(("modelName", model_name), ("name", name)), data=data)

        if payload.get("output", None) is None:
            raise ExecutorException("Invaild response. The payload must include the key: output.")

        return payload


class PythonExecutor(Executor):
    """Execute methods/functions from a model like object."""

    def __init__(self, module):
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
            Returns true if the module has a class named `name`
        """
        cls = getattr(self._module, name, None)

        if isinstance(cls, type):
            return True

        return False

    def has_step(self, model_name, name):
        """Check if the module has a callable. If model_name is not ``None`` it will check
        for a method, and if model_name is ``None`` it will check for a function.

        Args:
            cls_name: The name of the class.
            name: The name of the method/function.

        Returns:
            Returns true if the module has the callable.
        """
        if model_name is None:
            return self._has_function(name)

        return self._has_method(model_name, name)

    def execute_step(self, model_name, name, data=None):
        """Execute the callable and returns the output.

        Args:
            model_name: The name of the class, if ``None`` will execute
                a function.
            name: The name of the method/function.
            data: The data will be passed to the callable.

        Returns:
            The data changed by callable and output of the callable.
        """

        if model_name is None:
            func = getattr(self._module, name)
            nr_args = len(inspect.getfullargspec(func).args)
        else:
            self._setup_class(model_name)

            func = getattr(self._instances[model_name], name)
            nr_args = len(inspect.getfullargspec(func).args) - 1  # substract the self argument of the method

        if data is None:
            data = {}
        else:
            data = copy.deepcopy(data)

        if nr_args == 0:
            output = get_output(func)
        elif nr_args == 1:
            output = get_output(func, data)
        else:
            raise ExecutorException(
                "The {}.{} function must take 0 or 1 parameters but it expects more than one parameter."
                .format(model_name, name))

        output["data"] = data
        return output


class DotnetExecutorService:
    """Starts a dotnet executor service."""

    def __init__(self, path, host, port, output_file="dotnet-executor.log"):
        """Starts a dotnet tests execution service.

        ``dotnet run -p <path>`` is used to compile and run the console app project

        ``dotnet <path>`` is used to run compiled exe or dll.

        Args:
            path: The path of the console application project, dll or exe, that starts an ExecutorService
            host: The host for the service to listen.
            port: The port for the service to listen.
        """

        self.host = host
        self.port = port
        self.output_file = output_file

        command = self._create_command(path, host, port)
        print("Starting dotnet executor {} on http://{}:{}".format(path, host, port))
        self._process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                         stdout=open(output_file, "w"), stderr=subprocess.STDOUT)

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
                raise ExecutorException("Could not start dotnet Executor. Check {}".format(self.output_file))

    @staticmethod
    def _create_command(path, host, port):
        command = get_command("dotnet")

        if os.path.isdir(path):
            command.append("run")
            command.append("-p")

        command.append(path)
        command.append("--server.urls=http://{}:{}".format(host, port))

        return command

    def kill(self):
        """Kill the dotnet service.

        Note:
            If the path given was a project path and the service was started with `dotnet run`
            kills the main process and child process, because `dotnet run` starts the service
            in a child process.
        """

        kill(self._process.pid)


class DotnetExecutor(HttpExecutor):

    def __init__(self, path, host, port):
        super().__init__(host, port)

        self._service = DotnetExecutorService(path, host, port)

    def load(self, path):
        """Kill the executor service and start a new one with the given path."""

        self._service.kill()
        self._service = DotnetExecutorService(path, self.host, self.port)

    def kill(self):
        """Kill the executor service."""

        self._service.kill()


def create_http_executor(path, host, port):
    """Creates a HTTP executor."""

    executor = HttpExecutor(host=host, port=port)
    executor.load(path)

    return executor


def create_dotnet_executor(path, host, port):
    """Creates a .NET executor."""

    return DotnetExecutor(path, host, port)


def create_python_executor(path):
    """Creates a Python executor."""

    path, package = os.path.split(path)
    module = load(path, package, "test")

    return PythonExecutor(module)


def create_executor(path, language=None, host="127.0.0.1", port=5000):
    """Creates an executor.

    Args:
        path: The path to the tests.
        language: The language of the tests.
        host: The host for the executor service to listen.
        port: The port for the executor to listen.
    """

    if not language:
        return create_http_executor(path, host, port)
    elif language == "python":
        return create_python_executor(path)
    elif language == "c#":
        return create_dotnet_executor(path, host, port)
    else:
        raise ValueError("{} is not supported.".format(language))
