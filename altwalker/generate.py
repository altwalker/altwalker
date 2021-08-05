"""A collection of util functions for generating code form model(s)."""

import os
import re
import abc
import shutil
import logging
import warnings

from altwalker.__version__ import VERSION
from altwalker._utils import get_resource, has_git, Factory
from altwalker.exceptions import AltWalkerException
from altwalker.code import get_methods


logger = logging.getLogger(__name__)

MINOR_VERSION = ".".join(VERSION.split(".")[:2]) + ".*"

_PYTHON_METHOD_TEMPLATE =  get_resource("data/templates/generate/python/method.txt")
_PYTHON_CLASS_TEMPLATE = get_resource("data/templates/generate/python/class.txt")

_DOTNET_METHOD_TEMPLATE = get_resource("data/templates/generate/dotnet/method.txt")
_DOTNET_CLASS_TEMPLATE = get_resource("data/templates/generate/dotnet/class.txt")
_DOTNET_NAMESPACE_TEMPLATE = get_resource("data/templates/generate/dotnet/namespace.txt")
_DOTNET_MAIN_TEMPLATE = get_resource("data/templates/generate/dotnet/main.txt")

_DEFAULT_MODEL = get_resource("data/models/default.json")
_DOTNET_CSPROJ = get_resource("data/templates/generate/dotnet/csproj.txt")

_BASE_GIT_IGNORE = get_resource("data/templates/generate/gitignore/base.txt")
_PYTHON_GIT_IGNORE = get_resource("data/templates/generate/gitignore/python.txt")
_DOTNET_GIT_IGNORE = get_resource("data/templates/generate/gitignore/dotnet.txt")


def _normalize_namespace(string):
    """Normalize string for a namespace."""

    namespace = re.sub(r'[\-\ ]', ".", string)
    namespace = re.sub(r'\.+', ".", namespace)

    return namespace.title()


def _copy_models(output_dir, model_paths):
    """Copy all models in ``output_dir``."""

    os.makedirs(output_dir)

    for model_path in model_paths:
        _, file_name = os.path.split(model_path)
        shutil.copyfile(model_path, os.path.join(output_dir, file_name))


def _create_default_model(output_dir):
    """Save the default model in ``output_dir``."""

    os.makedirs(output_dir)

    with open(os.path.join(output_dir, "default.json"), "w") as fp:
        fp.write(_DEFAULT_MODEL)


def _git_init(path):
    """Create a local repository and commit all files."""

    if has_git():
        from git import Repo

        repo = Repo.init(path)

        repo.git.add("--all")
        repo.index.commit("Initial commit")
    else:
        warnings.warn("Git is not installed.")


def generate_empty_tests(output_dir, methods=None, package_name="tests"):
    """Generate an empty tests directory."""

    os.makedirs(os.path.join(output_dir, package_name))


def generate_python_methods(methods_list):
    methods_code = [_PYTHON_METHOD_TEMPLATE.format(name) for name in methods_list]
    return "\n".join(methods_code)


def generate_python_class(class_name, methods_list):
    return _PYTHON_CLASS_TEMPLATE.format(class_name, generate_python_methods(methods_list))


def generate_python_code(methods):
    """Generate python source code from the ``dict`` of methods.

    Args:
        methods (:obj:`dict`): The keys are class names and the values are all
            methods for that class.

    Returns:
        str: The python source code.
    """

    classes_code = [generate_python_class(class_name, methods_list) for class_name, methods_list in methods.items()]
    return "\n{}".format("\n\n".join(classes_code))


def generate_python_tests(output_dir, methods, package_name="tests"):
    """Generate a python test package from the models."""

    os.makedirs(os.path.join(output_dir, package_name))

    with open(os.path.join(output_dir, package_name, "__init__.py"), "w"):
        pass

    with open(os.path.join(output_dir, package_name, "test.py"), "w") as fp:
        fp.write(generate_python_code(methods))


def generate_dotnet_methods(methods_list):
    methods_code = [_DOTNET_METHOD_TEMPLATE.format(name) for name in methods_list]
    return "\n".join(methods_code)


def generate_dotnet_class(class_name, methods_list):
    return _DOTNET_CLASS_TEMPLATE.format(class_name, generate_dotnet_methods(methods_list))


def generate_dotnet_code(methods, namespace="Tests"):
    classes_code = [generate_dotnet_class(class_name, methods_list) for class_name, methods_list in methods.items()]
    classes_code = "\n{}\n".format("\n\n".join(classes_code))

    classes_code += _DOTNET_MAIN_TEMPLATE.format(
        "\n".join(["            service.RegisterModel<{}>();".format(name) for name in methods.keys()])
    )

    return _DOTNET_NAMESPACE_TEMPLATE.format(namespace, classes_code)


def generate_dotnet_tests(output_dir, methods, package_name="tests"):
    """Generate a .NET/C# test package from the models."""

    _, project_name = os.path.split(output_dir)
    namespace = _normalize_namespace(project_name + "." + package_name)
    project_path = os.path.join(output_dir, package_name)

    os.makedirs(project_path)

    with open(os.path.join(project_path, "{}.csproj".format(package_name)), "w") as fp:
        fp.write(_DOTNET_CSPROJ.format(namespace, MINOR_VERSION))

    with open(os.path.join(project_path, "Program.cs"), "w") as fp:
        fp.write(generate_dotnet_code(methods, namespace=namespace))


_GENERATE_METHODS_FUNCTIONS = {
    "python": generate_python_methods,
    "dotnet": generate_dotnet_methods,
    "c#": generate_dotnet_methods,
}

_GENERATE_CLASS_FUNCTIONS = {
    "python": generate_python_class,
    "dotnet": generate_dotnet_class,
    "c#": generate_dotnet_class,
}

_GENERATE_CODE_FUNCTIONS = {
    "python": generate_python_code,
    "dotnet": generate_dotnet_code,
    "c#": generate_dotnet_code,
}

_DEFAULT_GENERATE_TEST_FUNCTION = generate_empty_tests

_GENERATE_TESTS_FUNCTIONS = {
    "python": generate_python_tests,
    "dotnet": generate_dotnet_tests,
    "c#": generate_dotnet_tests,
}

SUPPORTED_LANGUAGES = _GENERATE_TESTS_FUNCTIONS.keys()


def _call_generate_function(language, functions, *args, **kwargs):
    try:
        generate_func = functions[language.lower()]
    except KeyError:
        raise AltWalkerException(
            "Language '{}' is not supported. Supported languages are: {}."
            .format(language, ", ".join(functions.keys()))
        )

    return generate_func(*args, **kwargs)


def generate_methods(language, *args, **kwargs):
    return _call_generate_function(language, _GENERATE_METHODS_FUNCTIONS, *args, **kwargs)


def generate_class(language, *args, **kwargs):
    return _call_generate_function(language, _GENERATE_CLASS_FUNCTIONS, *args, **kwargs)


def generate_code(language, *args, **kwargs):
    return _call_generate_function(language, _GENERATE_CODE_FUNCTIONS, *args, **kwargs)


def generate_tests(output_dir, model_paths, *args, language=None, package_name="tests", **kwargs):
    """Generate tests for an language.

    Args:
        output_dir: The path to the project root.
        model_paths: A sequence of path to model files.
        package_name: The name of the test package (e.g. tests).
        language: The language of the project (e.g. python).

    Raises:
        FileExistsError: If the path ``output_dir/package_name`` already exists.
    """

    package_path = os.path.join(output_dir, package_name)

    if os.path.exists(package_path):
        raise FileExistsError("The '{}' directory already exists.".format(package_path))

    methods = get_methods(model_paths)

    try:
        if not language:
            _DEFAULT_GENERATE_TEST_FUNCTION(output_dir, methods, package_name=package_name)
        else:
            _call_generate_function(language, _GENERATE_TESTS_FUNCTIONS, output_dir, methods, package_name=package_name)
    except Exception as ex:
        logger.exception(ex)
        if os.path.isdir(package_path):
            shutil.rmtree(package_path)
        raise



class Generator(metaclass=abc.ABCMeta):
    """Abstract base class for generating an AltWalker project.

    Args:
        output_path (:obj:`str`): The path to the project root.
        models_path (:obj:`str`): A sequence of paths to model files.
        git (:obj:`bool`): If set to ``True`` will initialize a git repository and commit the files.

    """

    def __init__(self, output_path, model_paths=None, git=False):
        self.output_path = output_path
        self.model_paths = model_paths or []

        self.git = git

    def __repr__(self):
        return ""

    @property
    def project_name(self):
        return os.path.basename(self.output_path)

    def copy_default_model(self):
        self.model_paths = [os.path.join(self.output_path, "models", "default.json")]
        os.makedirs(self.output_path)

        with open(os.path.join(self.output_path, "models/default.json"), "w") as fp:
            fp.write(_DEFAULT_MODEL)

    def copy_models(self):
        os.makedirs(self.output_path)

        for model_path in self.model_paths:
            file_name = os.path.basename(model_path)
            shutil.copyfile(model_path, os.path.join(self.output_path, file_name))

    def git_init(self):
        self.generate_gitignore()
        _git_init(self.output_path)

    def generate_models(self):
        if self.model_paths:
            self.copy_models()
        else:
            self.copy_default_model()

    def generate_gitignore(self):
        with open(os.path.join(self.output_path, '.gitignore'), 'w') as fp:
            fp.write(_BASE_GIT_IGNORE)

    @abc.abstractstaticmethod
    def generate_methods(self, *args, **kwargs):
        pass

    @abc.abstractstaticmethod
    def generate_class(self, *args, **kwargs):
        pass

    @abc.abstractstaticmethod
    def generate_code(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def generate_tests(self, *args, **kwargs):
        pass

    def init_project(self, *args, **kwargs):
        if os.path.exists(self.output_path):
            raise FileExistsError("The '{}' directory already exists.".format(self.output_path))

        os.makedirs(self.output_path)

        try:
            self.generate_models()

            if self.git:
                self.git_init()
        except Exception as error:
            logger.exception(error)
            shutil.rmtree(self.output_path)
            raise


class EmptyGenerator(Generator):

    def generate_methods(self, *args, **kwargs):
        return ""

    def generate_class(self, *args, **kwargs):
        return ""

    def generate_code(self, *args, **kwargs):
        return ""

    def generate_tests(self, package_name="tests"):
        os.makedirs(os.path.join(self.output_dir, package_name))


class PythonGenerator(Generator):

    def generate_methods(self, methods):
        code = [_PYTHON_METHOD_TEMPLATE.format(name) for name in methods]
        return "\n".join(code)

    def generate_class(self, class_name, methods):
        return _PYTHON_CLASS_TEMPLATE.format(class_name, self.generate_methods(methods))

    def generate_code(self, classes):
        code = [self.generate_class(class_name, methods) for class_name, methods in classes.items()]
        return "\n{}".format("\n\n".join(code))

    def generate_tests(self, classes, package_name="tests"):
        base_path = os.path.join(self.output_path, package_name)
        os.makedirs(base_path)

        open(os.path.join(base_path, "__init__.py"), "w").close()

        with open(os.path.join(base_path, "test.py"), "w") as fp:
            fp.write(self.generate_code(classes))


class DotnetGenerator(Generator):

    def generate_methods(self, methods):
        code = [_DOTNET_METHOD_TEMPLATE.format(name) for name in methods]
        return "\n".join(code)

    def generate_class(self, class_name, methods):
        return _DOTNET_CLASS_TEMPLATE.format(class_name, self.generate_methods(methods))

    def generate_code(self, classes, namespace="Tests"):
        code = [generate_dotnet_class(class_name, methods) for class_name, methods in classes.items()]
        code = "\n{}\n".format("\n\n".join(code))

        code += _DOTNET_MAIN_TEMPLATE.format(
            "\n".join(["            service.RegisterModel<{}>();".format(name) for name in classes.keys()])
        )

        return _DOTNET_NAMESPACE_TEMPLATE.format(namespace, code)

    def generate_tests(self, classes, package_name="tests"):
        namespace = _normalize_namespace(self.project_name + "." + package_name)
        base_path = os.path.join(self.output_path, package_name)

        os.makedirs(base_path)

        with open(os.path.join(base_path, "{}.csproj".format(package_name)), "w") as fp:
            fp.write(_DOTNET_CSPROJ.format(namespace, MINOR_VERSION))

        with open(os.path.join(base_path, "Program.cs"), "w") as fp:
            fp.write(generate_dotnet_code(classes, namespace=namespace))


_GENERATORS = Factory({
    "python": PythonGenerator,
    "dotnet": DotnetGenerator,
    "c#": DotnetGenerator,
}, default=EmptyGenerator)


def get_support_languages():
    return _GENERATORS.keys()


def generate_methods(methods, language=None):
    cls = _GENERATORS.get(language)
    return cls.generate_methods(methods)


def generate_class(class_name, methods, language=None):
    cls = _GENERATORS.get(language)
    return cls.generate_class(class_name, methods)


def generate_tests(output_path, model_paths=None, language=None):
    """ """

    cls = _GENERATORS.get(language)
    generator = cls(output_path, model_paths=model_paths)
    return generator.generate_tests()


def init_project(output_path, model_paths=None, language=None, git=True):
    """Initiates a new project.

    Args:
        output_path: The path to the project root.
        language: The language of the project (e.g. python).
        model_paths: A sequence of path to model files.
        git: If set to ``True`` will initialize a git repository and commit the files.

    Raises:
        FileExistsError: If the path ``output_dir`` already exists.
    """

    cls = _GENERATORS.get(language)
    generator = cls(output_path, model_paths=model_paths, git=git)
    return generator.init_project()
