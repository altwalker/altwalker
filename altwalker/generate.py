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

_PYTHON_METHOD_TEMPLATE = get_resource("data/templates/generate/python/method.txt")
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
        repo.index.commit("Initial commit from AltWalker CLI {}".format(VERSION))
    else:
        warnings.warn("Git is not installed.")


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
        return '{}({!r}, {!r}, {!r})'.format(
           self.__class__.__name__,
           self.output_path, self.model_paths, self.git
        )

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

    def generate_requirements(self, output_path):
        with open(os.path.join(output_path, "requirements.txt"), "w") as fp:
            fp.write("altwalker")

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
        code = [self.generate_class(class_name, methods) for class_name, methods in classes.items()]
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
            fp.write(self.generate_code(classes, namespace=namespace))


GENERATOR_FACTORY = Factory({
    "python": PythonGenerator,
    "dotnet": DotnetGenerator,
    "c#": DotnetGenerator,
}, default=EmptyGenerator)


def create_generator(language=None):
    return GENERATOR_FACTORY.get(language)


def get_supported_languages():
    return GENERATOR_FACTORY.keys()


def generate_methods(methods, language=None):
    cls = GENERATOR_FACTORY.get(language)
    return cls.generate_methods(methods)


def generate_class(class_name, methods, language=None):
    cls = GENERATOR_FACTORY.get(language)
    return cls.generate_class(class_name, methods)


def generate_code(output_path, model_paths=None, language=None):
    cls = GENERATOR_FACTORY.get(language)
    generator = cls(output_path, model_paths=model_paths)
    return generator.generate_code()


def generate_tests(output_path, model_paths=None, language=None):
    cls = GENERATOR_FACTORY.get(language)
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

    cls = GENERATOR_FACTORY.get(language)
    generator = cls(output_path, model_paths=model_paths, git=git)
    return generator.init_project()
