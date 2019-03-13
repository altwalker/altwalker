import os
import io
import sys
import inspect
import traceback
import importlib
import importlib.util
from contextlib import redirect_stdout


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

    def has_function(self, name):
        func = getattr(self._module, name, None)

        if callable(func):
            return True

        return False

    def has_class(self, class_name):
        cls = getattr(self._module, class_name, None)

        if isinstance(cls, type):
            return True

        return False

    def has_method(self, class_name, name):
        cls = getattr(self._module, class_name, None)

        if isinstance(cls, type):
            method = getattr(cls, name, None)

            if callable(method):
                return True

        return False

    def has_step(self, class_name, name):
        """Check if the module has a callable. If class_name is not None it will check
        for a method, and if class_name is None it will check for a function.

        Args:
            cls_name: The name of the class.
            name: The name of the method/function.

        Returns:
            Returns true if the module has the callable.
        """
        if class_name is None:
            return self.has_function(name)

        return self.has_method(class_name, name)

    def execute_step(self, class_name, name, *args):
        """Execute the callable and returns the output.

        Args:
            class_name: The name of the class, if None will execute
                a function.
            name: The name of the method/function.
            *args: The args will be passed to the callable.

        Returns:
            The output of the callable.
        """
        if class_name is None:
            func = getattr(self._module, name)
            nr_args = len(inspect.getfullargspec(func).args)
        else:
            self._setup_class(class_name)

            func = getattr(self._instances[class_name], name)
            # substract the self argument of the method
            nr_args = len(inspect.getfullargspec(func).args) - 1

        return get_output(func, *args[:nr_args])


def create_executor(path, package="tests", module="test"):
    """Load a module form a package at a given path, and return an Executor."""

    module = load(path, package, module)
    return Executor(module)
