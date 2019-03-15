import os
import io
import signal
import sys
import inspect
import importlib
import importlib.util
import psutil
import platform
from contextlib import redirect_stdout
import subprocess
from time import sleep

import requests

from .exceptions import AltWalkerException, ExecutorException


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


class PythonExecutor:
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

    def has_model(self, name):
        """Check if the module has a class `name`

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
        """Check if the module has a callable. If model_name is not None it will check
        for a method, and if model_name is None it will check for a function.

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
    """Starts and manages a dotnet executor service. """

    def __init__(self, path, host, port):
        """Starts a dotnet tests execution service

        `dotnet run -p path` - is used to compile and run the console app project

        `dotnet path` is used to run compiled exe or dll.

        Args:
            path: the path of the console application project, dll or exe, that starts an ExecutorService
            host: the host for the service to listen. Passed as argument to the console app.
            port: the port for the service to listen. Passed as argument to the console app.
        """
        self.host = host
        self.port = port
        cmd = ["cmd.exe", "/C"] if platform.system() == "Windows" else []
        cmd.append("dotnet")
        if os.path.isdir(path):
            cmd.append("run")
            cmd.append("-p")
            self.dotnet_run = True

        cmd.append(path)
        cmd.append("--server.urls=http://{}:{}".format(self.host, self.port))

        self._process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sleep(5)
        if self._process.poll() is not None:  # the process should be running and expecting http requests
            output, error = self._process.communicate()
            if error:
                error = error.decode("utf-8")
                output = output.decode("utf-8")
                raise AltWalkerException("Service exited with error. Stderr: {}. Stdout: {}".format(error, output))
            raise AltWalkerException("Service stopped. Stdout: {}".format(output))

    def kill(self):
        """
        Kills the dotnet executor service. If the path given was a project path and the service was started with
        `dotnet run` kills the main process and child process. `dotnet run` starts the service in a child process.
        """
        if self.dotnet_run:
            for child in psutil.Process(self._process.pid).children():
                child.kill()
        self._process.send_signal(signal.SIGINT)


class HttpExecutorClient:
    def __init__(self, host, port):
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
        """HTTP GET /altwalker/hasModel?name=`name`

        Returns:
            True, if response["hasModel"] is True, where response is the json body returned by the api
            False, otherwise
        """
        response = self._get("hasModel", params=(("name", name)))
        return response["hasModel"] is True

    def has_step(self, model_name, name):
        """HTTP GET /altwalker/hasStep?modelName=`model_name`&name=`name`

        Returns:
            True, if response["hasStep"] is True, where response is the json body returned by the api
            False, otherwise
        """
        response = self._get("hasStep", params=(("modelName", model_name), ("name", name)))
        return response["hasStep"] is True

    def execute_step(self, model_name, name, data=None):
        """POSTS the `data` dictionary to /altwalker/executeStep?modelName=`model_name`&name=`name`

        Returns:
            The data and the step execution output as returned by the api in json body.
            {
                "output": response["output"],
                "data": response["data"]
            }
        """
        response = self._post("executeStep", params=(("modelName", model_name), ("name", name)), data=data)
        return {
            "output": response["output"],
            "data": response["data"]
        }

    def reset(self):
        """HTTP GET /altwalker/reset"""
        return self._get("reset")


class HttpExecutor(HttpExecutorClient):
    def __init__(self, service, host, port):
        """Initialises the HttpExecutor
        Args:
            service: the service which executes the tests
        """
        super().__init__(host, port)
        self.service = service

    def kill(self):
        """Sends kill command to the tests executing service"""
        self.service.kill()


def _create_python_executor(path):
    path, package = os.path.split(path)
    module = load(path, package, "test")
    return PythonExecutor(module)


def create_executor(path, language, host="127.0.0.1", port=5000):
    """
    Creates a language specifc executor. Loads executor dependencies.
    For python it loads the module and then creates PythonExecutor
    For dotnet it creates DotnetExecutorService and then creates HttpExecutor

    Args:
        path: the path to the tests
        language: The language of the tests.
        host: the host for the executor service to listen
        port: the port for the executor to listen
    """
    if language == "python":
        return _create_python_executor(path)
    if language == "c#":
        service = DotnetExecutorService(path, host, port)
    else:
        raise ValueError("{} is not supported.".format(language))

    return HttpExecutor(service, host, port)
