import os
import io
import sys
import inspect
import importlib
import importlib.util
import subprocess
from time import sleep
from contextlib import redirect_stdout

import requests

from altwalker._utils import kill, get_command
from altwalker.exceptions import ExecutorException


def get_output(callable, *args, **kargs):
    """Call a callable object and return the output from stdout."""

    output = io.StringIO()

    with redirect_stdout(output):
        callable(*args, **kargs)

    string = output.getvalue()
    output.close()

    return string


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

            If no error occured the ``error`` key is not pressent of set to ``None``.

            If the graph data is not used or modiffied the ``data`` key can be omitted or set to ``None``.
        """


class HttpExecutor(Executor):
    """Http client for an executor service."""

    def __init__(self, host, port):
        """Initialize an HttpExecutor with the ``host`` and ``port`` of the executor service."""

        self.host = host
        self.port = port

        self.base = "http://" + host + ":" + str(port) + "/altwalker/"

    def _get_body(self, response):
        body = response.json()

        if "error" in body:
            raise ExecutorException(body["error"])

        return body

    def _get(self, path, params=None):
        response = requests.get(self.base + path, params=params)
        return self._get_body(response)

    def _put(self, path):
        response = requests.put(self.base + path)
        return self._get_body(response)

    def _post(self, path, params=None, data=None):
        HEADERS = {'Content-Type': 'application/json'}
        response = requests.post(self.base + path, params=params, json=data, headers=HEADERS)
        return self._get_body(response)

    def has_model(self, name):
        """Makes a HTTP GET  request at ``/altwalker/hasModel?name=<name>``.

        Returns:
            True, if response["hasModel"] is True, where response is the json body returned by the api
            False, otherwise
        """

        response = self._get("hasModel", params=(("name", name)))
        return response["hasModel"]

    def has_step(self, model_name, name):
        """Makes a HTTP GET request at ``/altwalker/hasStep?modelName=<model_name>&name=<name>``.

        Returns:
            True, if response["hasStep"] is True, where response is the json body returned by the api
            False, otherwise
        """
        response = self._get("hasStep", params=(("modelName", model_name), ("name", name)))
        return response["hasStep"]

    def execute_step(self, model_name, name, data=None):
        """Makes a HTTP POST request at ``/altwalker/executeStep?modelName=<model_name>&name=<name>``.

        Returns:
            The data and the step execution output as returned by the api in json body.
        """

        response = self._post("executeStep", params=(("modelName", model_name), ("name", name)), data=data)

        return {
            "output": response["output"],
            "data": response["data"]
        }

    def reset(self):
        """Makes an HTTP GET at ``/altwalker/reset``."""

        self._get("reset")


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
            model_name: The name of the class, if None will execute
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
            # substract the self argument of the method
            nr_args = len(inspect.getfullargspec(func).args) - 1

        if data is None:
            data = {}

        if nr_args == 0:
            output = get_output(func)
        if nr_args == 1:
            output = get_output(func, data)
        if nr_args > 1:
            raise ExecutorException("{} {} takes 0 or 1 parameters but more than 1 were given".format(model_name, name))

        return {
            "output": output,
            "data": data
        }

    def reset(self):
        self._instances = {}

    def kill(self):
        pass


class DotnetExecutorService:
    """Starts a dotnet executor service."""

    def __init__(self, path, host, port):
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

        command = self._create_command(path, host, port)
        self._process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        sleep(5)

        # the process should be running and expecting http requests
        if self._process.poll() is not None:
            output, error = self._process.communicate()

            if error:
                error = error.decode("utf-8")
                output = output.decode("utf-8")
                raise ExecutorException("Service exited with error. Stderr: {}. Stdout: {}".format(error, output))

            raise ExecutorException("Service stopped. Stdout: {}".format(output))

    def _create_command(self, path, host, port):
        command = get_command("dotnet")

        if os.path.isdir(path):
            command.append("run")
            command.append("-p")
            self.dotnet_run = True

        command.append(path)
        command.append("--server.urls=http://{}:{}".format(self.host, self.port))

        return command

    def kill(self):
        """Kill the dotnet service. If the path given was a project path and the service was started with
        `dotnet run` kills the main process and child process, because `dotnet run` starts the service
        in a child process."""

        kill(self._process.pid)


class DotnetExecutor(HttpExecutor):

    def __init__(self, path, host, port):
        super().__init__(host, port)

        self._service = DotnetExecutorService(path, host, port)

    def load(self, path):
        self._service.kill()
        self._service = DotnetExecutorService(path, self.host, self.port)

    def kill(self):
        self._service.kill()


def create_dotnet_executor(path, host, port):
    return DotnetExecutor(path, host, port)


def create_python_executor(path):
    path, package = os.path.split(path)
    module = load(path, package, "test")

    return PythonExecutor(module)


def create_executor(path, language="python", host="127.0.0.1", port=5000):
    """Creates an executor.

    Args:
        path: The path to the tests.
        language: The language of the tests.
        host: The host for the executor service to listen.
        port: The port for the executor to listen.
    """

    if language == "python":
        return create_python_executor(path)
    if language == "c#":
        DotnetExecutor(path, host, port)
    else:
        raise ValueError("{} is not supported.".format(language))

    return HttpExecutor(host, port)
