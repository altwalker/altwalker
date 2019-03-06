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

    def execute_step(self, model_name, name, *args):
        """Execute the callable and returns the output.

        Args:
            model_name: The name of the class, if None will execute
                a function.
            name: The name of the method/function.
            *args: The args will be passed to the callable.

        Returns:
            The output of the callable.
        """
        if model_name is None:
            func = getattr(self._module, name)
            nr_args = len(inspect.getfullargspec(func).args)
        else:
            self._setup_class(model_name)

            func = getattr(self._instances[model_name], name)
            # substract the self argument of the method
            nr_args = len(inspect.getfullargspec(func).args) - 1

        return get_output(func, *args[:nr_args])

    def reset(self):
        self._instances = {}


class DotnetExecutorService:
    """Starts a dotnet executor service. """

    def __init__(self, path, host, port):
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
        response = requests.post(self.base + path, params=params, data=data)
        print(response)
        return self._get_body(response)

    def has_model(self, name):
        response = self._get("hasModel", params=(("name", name)))
        return response["hasModel"] is True

    def has_step(self, model_name, name):
        response = self._get("hasStep", params=(("modelName", model_name), ("name", name)))
        return response["hasStep"] is True

    def execute_step(self, model_name, name, *args):
        response = self._post("executeStep", params=(("modelName", model_name), ("name", name)))
        return response["output"]

    def reset(self):
        return self._get("reset")


class HttpExecutor(HttpExecutorClient):
    def __init__(self, service, host, port):
        self.service = service
        return super().__init__(host, port)()

    def kill(self):
        self.service.kill()


class Executor(PythonExecutor):
    def __init__(self, module):
        return super().__init__(module)

    def kill(self):
        pass


def _create_python_executor(path):
    path, package = os.path.split(path)
    module = load(path, package, "test")
    return Executor(module)


def create_executor(path, language, host="127.0.0.1", port="5000"):
    if language == "python":
        return _create_python_executor(path)
    if language == "dotnet":
        service = DotnetExecutorService(path, host, port)
    else:
        raise ValueError("{} is not supported.".format(language))

    return HttpExecutor(service, host, port)
