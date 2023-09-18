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

import abc
import copy
import io
import logging
import os
import time
import traceback
from contextlib import redirect_stdout
from inspect import signature

import requests

from altwalker._utils import Command, Factory, url_join
from altwalker.exceptions import (AltWalkerException, AltWalkerTypeError,
                                  AltWalkerValueError, ExecutorException)
from altwalker.loader import create_loader

logger = logging.getLogger(__name__)


def get_step_result(callable, *args, **kwargs):
    """Call a callable object and return the output from stdout, error message and
    traceback if an error occurred.

    Args:
        callable: The callable object to call.
        *args: The list of args for the callable.
        **kwargs: The dict of kwargs for the callable.

    Returns:
        dict: A dict containing the output of the callable, and the error message with the trace
            if an error occurred::

            {
                "result": Any
                "output": "",
                "error": {
                    "message": "",
                    "trace": ""
                }
            }
    """

    step_result = {}
    output = io.StringIO()

    with redirect_stdout(output):
        try:
            ret = callable(*args, **kwargs)
            if ret is not None:
                step_result["result"] = ret
        except (KeyboardInterrupt, Exception) as e:
            step_result["error"] = {
                "message": str(e) or type(e).__name__,
                "trace": str(traceback.format_exc())
            }

    step_result["output"] = output.getvalue()
    output.close()

    return step_result


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
    def execute_step(self, model_name, name, data=None, step=None):
        """Execute a step from a model.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.
            data (:obj:`dict`): The current graph data.
            step (:obj:`dict`): The current step.

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

            If no error occurred the ``error`` key can be omitted or set to ``None``.

            If the graph data is not used or modified the ``data`` key can be omitted or set to ``None``.
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

    def __init__(self, url="http://localhost:5000", **kwargs):
        self.url = url or "http://localhost:5000"
        self.base = url_join(self.url, "altwalker/")

        logging.debug(f"Initiate an HttpExecutor to connect to {self.url} service")

    def _validate_response(self, response):
        if not response.status_code == 200:
            status_code = response.status_code
            error = response.json().get("error")

            error_type = self.ERROR_CODES.get(status_code, "Unknown Error")
            error_message = f"The executor from {self.url} responded with status code: {status_code} {error_type}."

            if error:
                error_message += f"\nMessage: {error['message']}\nTrace: {error.get('trace')}"

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

    def _post(self, path, params=None, json=None):
        HEADERS = {'Content-Type': 'application/json'}
        response = requests.post(url_join(self.base, path), params=params, json=json, headers=HEADERS)
        self._validate_response(response)

        return self._get_payload(response)

    def kill(self):
        """This method does nothing."""

    def load(self, path):
        """Makes a POST request at ``/load``.

        Args:
            path (:obj:`str`): The path to the test code.
        """

        self._post("load", json={"path": path})

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
            raise ExecutorException("Invalid response. The payload must include the key: hasModel.")

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
            raise ExecutorException("Invalid response. The payload must include the key: hasStep.")

        return has_step

    def execute_step(self, model_name, name, data=None, step=None):
        """Makes a POST request at ``/executeStep?modelName=<model_name>&name=<name>``.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.
            data (:obj:`dict`): The current graph data.
            step (:obj:`dict`): The current step.

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

        payload = self._post(
            "executeStep",
            params={"modelName": model_name, "name": name},
            json={"data": data, "step": step}
        )

        if payload.get("output") is None:
            raise ExecutorException("Invalid response. The payload must include the key: output.")

        return payload


class PythonExecutor(Executor):
    """Execute methods or functions from a model like object."""

    def __init__(self, module=None, loader=None, import_mode=None, **kwargs):
        self._loader = loader or create_loader(import_mode)
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
        """Load the test code from a path and reset the current execution."""

        self.reset()

        self._module = self._loader.load(os.path.join(path, "test.py"), ".")
        self.reset()

    def reset(self):
        """Reset the current execution."""

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

    def execute_step(self, model_name, name, data=None, step=None):
        """Execute a step from a model.

        Args:
            model_name (:obj:`str`): The name of the model.
            name (:obj:`str`): The name of the step.
            data (:obj:`dict`): The current graph data.
            step (:obj:`dict`): The current step.

        Note:
            If ``model_name`` is ``None`` the step is a fixture.

        Returns:
            A dict containing the graph data, the output of the step, the result returned by the step method,
            and the error message with the trace if an error occurred::

                {
                    "output": "",
                    "data": {},
                    "result": Any,
                    "error": {
                        "message": "",
                        "trace": ""
                    }
                }

            If no error occurred the ``error`` key can be omitted or set to ``None``.

            If the graph data is not used or modified the ``data`` key can be omitted or set to ``None``.
        """

        data = copy.deepcopy(data) if data else {}

        if model_name:
            self._setup_class(model_name)
            func = getattr(self._instances[model_name], name)
        else:
            func = getattr(self._module, name)

        spec = signature(func)
        nr_args = len(spec.parameters)

        if nr_args == 0:
            step_result = get_step_result(func)
        elif nr_args == 1:
            step_result = get_step_result(func, data)
        elif nr_args == 2:
            step_result = get_step_result(func, data, step)
        else:
            func_name = f"{model_name}.{name}" if model_name else name
            type_ = "method" if model_name else "function"

            raise ExecutorException(
                f"The {func_name} {type_} must take 0, 1 or 2 parameters but it expects {nr_args} parameters."
            )

        step_result["data"] = data
        return step_result


class DotnetExecutorService:
    """Starts a C#/.NET executor service.

    * ``dotnet run -p <path>`` - is used to compile and run the console app project.
    * ``dotnet <path>`` - is used to run compiled exe or dll.

    Args:
        path: The path of the console application project, dll or exe, that starts an ``ExecutorService``.
        server_url: The url for the service to listen (e.g. http://localhost:5000/).
        output_file: A file for the output of the command.
    """

    def __init__(self, path, server_url="http://localhost:5000/", output_file="dotnet-executor.log"):
        self.path = path
        self.server_url = server_url or "http://localhost:5000/"
        self.output_file = output_file

        command = self._create_command(path, url=self.server_url)

        self._process = Command(command, self.output_file)

        logger.debug(f"Dotnet Executor Service started from '{self.path}' on {self.server_url}")
        logger.debug(f"Dotnet Executor Service started with command: {' '.join(command)}")
        logger.debug(f"Dotnet Executor Service running with pid: {self._process.pid}")

        # Ignore bare 'except' error because we re-raise the exception.
        try:
            self._read_logs()
        except:  # noqa: E722
            self.kill()
            raise

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
                    if "Now listening on:" in line:
                        break

                if self._process.poll() is not None:
                    self._raise_error()

    def _raise_error(self):
        logger.error(f"Could not start Dotnet Executor service from {self.path} on {self.server_url}")
        logger.error(f"Process exit code: {self._process.poll()}")

        raise ExecutorException(
            f"Could not start .NET Executor service from {self.path} on {self.server_url}\n"
            f"Check the log file at: {self.output_file}"
        )

    @staticmethod
    def _create_command(path, url="http://localhost:5000/"):
        command = ["dotnet"]

        if os.path.isdir(path):
            command.append("run")
            command.append("-p")

        command.append(path)
        command.append(f"--server.urls={url}")

        return command

    def kill(self):
        """Kill the .NET executor service process.

        Note:
            If the path given was a project path and the service was started with ``dotnet run``
            kills the main process and child process, because ``dotnet run`` starts the service
            in a child process.
        """

        logger.debug(f"Kill the .NET Executor Service from {self.path} on {self.server_url}")
        self._process.kill()


class DotnetExecutor(HttpExecutor):
    """Starts a C#/.NET executor service, and allows you to interact with it.

    Args:
        path: The path of the console application project, dll or exe, that starts an ``ExecutorService``.
        url: The url for the service to listen (e.g. http://localhost:5000/).
    """

    def __init__(self, path=None, url="http://localhost:5000/", **kwargs):
        super().__init__(url=url)
        self._service = None

        if path:
            self._service = DotnetExecutorService(path, server_url=url)

    def _ensure_service_is_running(self):
        if not self._service:
            raise AltWalkerException("Make sure you call the load method first to start the DotnetExecutorService.")

    def load(self, path):
        """Starts the executor service with the given project path, if a service is already running it will kill it
        before starting the new one.
        """

        logger.debug(f"Starting the .NET Executor service from {path} on {self.url}")

        if self._service:
            logger.debug("Killing the old .NET Executor service.")
            self._service.kill()

        self._service = DotnetExecutorService(path, server_url=self.url)

    def kill(self):
        """Kill the executor service."""

        self._service.kill()
        self._service = None

    def reset(self):
        """Reset the current execution."""

        self._ensure_service_is_running()
        return super().reset()

    def has_model(self, name):
        """Check if the module has a class named ``name``."""

        self._ensure_service_is_running()
        return super().has_model(name)

    def has_step(self, model_name, name):
        """Check if the module has a class named ``model_name`` with a method named."""

        self._ensure_service_is_running()
        return super().has_step(model_name, name)

    def execute_step(self, model_name, name, data=None, step=None):
        """Execute a step from a model."""

        self._ensure_service_is_running()
        return super().execute_step(model_name, name, data=data, step=step)


ExecutorFactory = Factory({
    "http": HttpExecutor,
    "python": PythonExecutor,
    "py": PythonExecutor,
    "dotnet": DotnetExecutor,
    "csharp": DotnetExecutor,
    "c#": DotnetExecutor,
}, default=PythonExecutor)


def get_supported_executors():
    return ExecutorFactory.keys()


def create_executor(executor_type, tests_path, **kwargs):
    """Create and initialize an executor for AltWalker.

    Args:
        executor_type (str): The type of the executor (e.g., 'http', 'python', 'dotnet').
        tests_path (str): The path to the tests.
        **kwargs: Additional keyword arguments passed to the executor constructor.

    Returns:
        Executor: An initialized executor instance.

    Raises:
        AltWalkerException: If the executor_type is not supported.
    """

    if executor_type is not None and not isinstance(executor_type, str):
        raise AltWalkerTypeError(f"Supported executor types are: {', '.join(ExecutorFactory.keys())}.")

    if executor_type is None:
        executor_cls = ExecutorFactory.default
    else:
        executor_type_lower_case = executor_type.lower()
        if executor_type_lower_case not in ExecutorFactory.keys():
            raise AltWalkerValueError(
                f"Executor type '{executor_type}' is not supported. "
                f"Supported executor types are: {', '.join(ExecutorFactory.keys())}."
            )

        executor_cls = ExecutorFactory.get(executor_type_lower_case)

    try:
        executor = executor_cls(**kwargs)
        executor.load(tests_path)

        logger.info(f"Created executor '{executor_type}' with tests path: '{tests_path}'")
        return executor
    except Exception as e:
        raise AltWalkerException(f"Failed to create executor: {e}")
