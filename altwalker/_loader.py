"""Import and return a module from the given path, which can be a file (a module) or a directory (a package)."""

import abc
import importlib
import importlib.util
import sys
from enum import Enum, unique
from pathlib import Path
from types import ModuleType


def module_name_from_path(path, root):
    """Return a dotted module name based on the given path, anchored on root.

    For example: path="projects/src/tests/test_foo.py" and root="/projects", the
    resulting module name will be "src.tests.test_foo".
    """

    path = path.with_suffix("")
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        # If we can't get a relative path to root, use the full path, except
        # for the first part ("d:\\" or "/" depending on the platform, for example).
        path_parts = path.parts[1:]
    else:
        # Use the parts for the relative path to the root path.
        path_parts = relative_path.parts

    return ".".join(path_parts)


def insert_missing_modules(modules, module_name):
    """Used by ``import_path`` to create intermediate modules when using mode=importlib.

    When we want to import a module as "src.tests.test_foo" for example, we need
    to create empty modules "src" and "src.tests" after inserting "src.tests.test_foo",
    otherwise "src.tests.test_foo" is not importable by ``__import__``.
    """

    module_parts = module_name.split(".")

    while module_name:
        if module_name not in modules:
            try:
                # If sys.meta_path is empty, calling import_module will issue
                # a warning and raise ModuleNotFoundError. To avoid the
                # warning, we check sys.meta_path explicitly and raise the error
                # ourselves to fall back to creating a dummy module.
                if not sys.meta_path:
                    raise ModuleNotFoundError
                importlib.import_module(module_name)
            except ModuleNotFoundError:
                module = ModuleType(
                    module_name,
                    doc="Empty module created by altwalker.",
                )
                modules[module_name] = module

        module_parts.pop(-1)
        module_name = ".".join(module_parts)


def load_module(p, root):
    """Import and return a module from the given path, which can be a file (a module) or a directory (a package)."""

    path = Path(p)
    module_name = module_name_from_path(path, root)

    for meta_importer in sys.meta_path:
        spec = meta_importer.find_spec(module_name, [str(path.parent)])
        if spec is not None:
            break
    else:
        spec = importlib.util.spec_from_file_location(module_name, str(path))

    if spec is None:
        raise ImportError(f"Can't find module '{module_name}' at location '{path}'.")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    insert_missing_modules(sys.modules, module_name)

    return mod


def load(p, root):
    """Import and return a module from the given path, which can be a file (a module) or a directory (a package).

    This function tries to import a module and if it fails due to a `ModuleNotFoundError`, it will try to import
    the missing module and retry importing the original module.
    """

    while True:
        try:
            return load_module(p, root)
        except ModuleNotFoundError as error:
            print("HERE")

            error_message = str(error)
            module_name = error_message[error_message.find("'") + 1:error_message.rfind("'")]
            load(module_name, root)


# -----------------


class Loader(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load(module, root):
        pass


class ImportlibLoader(Loader):

    def load(module, root):
        return {}


class RecursiveImporter(Loader):
    pass


class PrependLoader(Loader):

    def load(module, root):
        return {}


class AppendLoader(Loader):

    def load(module, root):
        return {}


@unique
class ImportingModes(Enum):
    IMPORTLIB = "importlib"
    PREPEND = "prepend"
    APPEND = "append"


def create_loader(mode):
    pass
