"""Module for importing and loading Python modules and packages from paths."""

import abc
import importlib
import importlib.util
import itertools
import logging
import sys
from pathlib import Path
from types import ModuleType

from ._utils import Factory
from .exceptions import AltWalkerTypeError, AltWalkerValueError

logger = logging.getLogger(__name__)


def module_name_from_path(path, root):
    """Return a dotted module name based on the given path, anchored on root.

    Args:
        path (Path): The path to the module or package file.
        root (Path): The root directory from which loading is performed.

    Returns:
        str or None: The dotted module name based on the given path, anchored on root.

    Example:
        >>> module_name_from_path(Path("projects/src/tests/test_foo.py"), Path("/projects"))
        'src.tests.test_foo'
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


def resolve_package_path(path):
    """Return the path to the Python package containing the given module or package file.

    This function looks for the last directory upwards from the provided path
    that still contains an '__init__.py' file, indicating a Python package.

    Args:
        path (Path-like): The path to a Python module or package file.

    Returns:
        Path or None: The path to the Python package directory if found, or None if
        it cannot be determined.

    Example:
        >>> resolve_package_path(Path("my_package/submodule.py"))
        Path('my_package')

        >>> resolve_package_path(Path("my_package/__init__.py"))
        Path('my_package')
    """

    result = None
    for parent in itertools.chain((path,), path.parents):
        if parent.is_dir():
            if not parent.joinpath("__init__.py").is_file():
                break
            if not parent.name.isidentifier():
                break
            result = parent
    return result


def resolve_package_info(path):
    """Resolve package information for a given Python module or package file.

    Args:
        path (Path-like): The path to the Python module or package file.

    Returns:
        Tuple[Path, str]: A tuple containing the package root directory (Path) and
        the fully-qualified module name (str). If the provided path is a Python module,
        the module name is derived from its relative location within the package.

    Example:
        >>> resolve_package_info(Path("my_package/submodule.py"))
        (Path('my_package'), 'submodule')

        >>> resolve_package_info(Path("my_package/__init__.py"))
        (Path('my_package'), 'my_package')
    """

    pkg_path = resolve_package_path(path)
    if pkg_path is not None:
        pkg_root = pkg_path.parent
        names = list(path.with_suffix("").relative_to(pkg_root).parts)
        if names[-1] == "__init__":
            names.pop()
        module_name = ".".join(names)
    else:
        pkg_root = path.parent
        module_name = path.stem

    return pkg_root, module_name


class Loader(metaclass=abc.ABCMeta):
    """Abstract base class for Altwalker's module loaders.

    This class defines the interface for loading Python modules from paths.
    Subclasses of this class must implement the 'load' method.
    """

    @abc.abstractstaticmethod
    def load(p, root):
        """Abstract method for loading a module from a given path.

        Args:
            p (str, Path): The path to the module or package to load.
            root (str, Path): The root directory from which loading is performed.

        Returns:
            ModuleType: The loaded Python module.
        """


class ImportlibLoader(Loader):

    @staticmethod
    def insert_missing_modules(modules, module_name):
        """Used by ``load`` to create intermediate modules.

        When we want to import a module as "src.tests.test_foo" for example, we need
        to create empty modules "src" and "src.tests" after inserting "src.tests.test_foo",
        otherwise "src.tests.test_foo" is not importable by ``__import__``.

        Args:
            modules (dict): A dictionary of loaded modules.
            module_name (str): The fully-qualified module name.

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

    @staticmethod
    def load_module(p, root):
        """Import and return a module from the given path, which can be a file (a module) or a directory (a package).

        Args:
            p (Path): The path to the module or package file.
            root (Path): The root directory from which loading is performed.

        Returns:
            ModuleType: The loaded Python module.

        Raises:
            ImportError: If the module cannot be found or loaded.
        """

        path = Path(p)
        module_name = module_name_from_path(path, root)

        for meta_importer in sys.meta_path:
            spec = meta_importer.find_spec(module_name, [str(path.parent)])
            if spec is not None:
                break
        else:
            spec = importlib.util.spec_from_file_location(module_name, str(path))

        if spec is None:
            raise ImportError("Can't find module '{}' at location '{}'.".format(module_name, path))

        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        ImportlibLoader.insert_missing_modules(sys.modules, module_name)

        return mod

    @staticmethod
    def load(p, root):
        """Import and return a module from the given path, which can be a file (a module) or a directory (a package).

        This function tries to import a module and if it fails due to a 'ModuleNotFoundError',
        it will try to import the missing module and retry importing the original module.

        Args:
            p (str, Path): The path to the module or package to load.
            root (str, Path): Used as an anchor to obtain a unique name for the module being imported so it can safely
                be stored into ``sys.modules``.

        Returns:
            ModuleType: The loaded Python module.
        """

        while True:
            try:
                return ImportlibLoader.load_module(p, root)
            except ModuleNotFoundError as error:
                error_message = str(error)
                module_name = error_message[error_message.find("'") + 1:error_message.rfind("'")]
                ImportlibLoader.load(module_name, root)


class PrependLoader(Loader):

    @staticmethod
    def load(p, root):
        """Import and return a module from the given path.

        The directory path containing the module will be inserted into the beginning of ``sys.path`` if not already
        there, and then imported with the ``__import__`` builtin.

        Args:
            p (str, Path): The path to the module or package to load.
            root (str, Path): Not used.

        Returns:
            ModuleType: The loaded Python module.
        """

        path = Path(p)

        if not path.exists():
            raise ImportError(path)

        pkg_root, module_name = resolve_package_info(path)

        if str(pkg_root) != sys.path[0]:
            sys.path.insert(0, str(pkg_root))

        importlib.import_module(module_name)
        mod = sys.modules[module_name]

        return mod


class AppendLoader(Loader):

    @staticmethod
    def load(p, root):
        """Import and return a module from the given path.

        The directory containing the module is appended to the end of ``sys.path`` if not already there, and then
        imported with the ``__import__`` builtin.

        Args:
            p (str, Path): The path to the module or package to load.
            root (str, Path): Not used.

        Returns:
            ModuleType: The loaded Python module.
        """

        path = Path(p)

        if not path.exists():
            raise ImportError(path)

        pkg_root, module_name = resolve_package_info(path)

        if str(pkg_root) not in sys.path:
            sys.path.append(str(pkg_root))

        importlib.import_module(module_name)
        mod = sys.modules[module_name]

        return mod


class ImportModes:
    """Possible values for ``mode`` parameter of ``create_loader``."""

    IMPORTLIB = "importlib"
    PREPEND = "prepend"
    APPEND = "append"


LoaderFactory = Factory({
    ImportModes.IMPORTLIB: ImportlibLoader,
    ImportModes.PREPEND: PrependLoader,
    ImportModes.APPEND: AppendLoader
}, default=ImportlibLoader)


def get_supported_loaders():
    return LoaderFactory.keys()


def create_loader(mode=None):
    """Create a loader for AltWalker.

    Args:
        mode (str): The importing mode (e.g., 'importlib', 'prepend', 'append').

    Raises:
        AltWalkerException: If the executor_type is not supported.
    """

    if mode is None:
        return LoaderFactory.default

    if not isinstance(mode, str):
        raise AltWalkerTypeError("Supported importing modes are: {}.".format(LoaderFactory.keys()))

    mode_lower_case = mode.lower()
    if mode_lower_case not in LoaderFactory.keys():
        raise AltWalkerValueError("Importing mode '{}' is not supported. Supported importing modes are: {}.".format(
            mode, LoaderFactory.keys()
        ))

    logger.info("Created loader with mode: {}".format(mode_lower_case))
    return LoaderFactory.get(mode_lower_case)
