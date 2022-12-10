"""A collection of util classes and functions for generating code form model(s)."""

import os
import re
import abc
import shutil
import logging
import warnings

from jinja2 import Environment

from altwalker.__version__ import VERSION
from altwalker._utils import get_resource, has_git, Factory
from altwalker.code import get_methods


logger = logging.getLogger(__name__)


def _normalize_namespace(string):
    """Normalize string for a namespace."""

    namespace = re.sub(r'[\-\ ]', ".", string)
    namespace = re.sub(r'\.+', ".", namespace)

    return namespace.title()


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
    """Abstract base class for generating a new AltWalker project.

    Args:
        output_path (:obj:`str`): The path to the project root.
        models_path (:obj:`str`): A sequence of paths to model files.
        git (:obj:`bool`): If set to ``True`` will initialize a git repository and commit the files.

    """

    BASE_GITIGNORE = get_resource("data/templates/generate/gitignore/base.txt")
    DEFAULT_MODEL = get_resource("data/models/default.json")

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

    @property
    def gitignore(self):
        return self.BASE_GITIGNORE

    def copy_default_model(self):
        self.model_paths = [os.path.join(self.output_path, "models", "default.json")]
        os.makedirs(os.path.join(self.output_path, "models"))

        with open(os.path.join(self.output_path, "models/default.json"), "w") as fp:
            fp.write(self.DEFAULT_MODEL)

    def copy_models(self):
        os.makedirs(os.path.join(self.output_path, "models"))

        for model_path in self.model_paths:
            file_name = os.path.basename(model_path)
            shutil.copyfile(model_path, os.path.join(self.output_path, "models", file_name))

    def git_init(self):
        self.generate_gitignore()
        _git_init(self.output_path)

    def generate_models(self):
        if self.model_paths:
            self.copy_models()
        else:
            self.copy_default_model()

    def generate_gitignore(self):
        with open(os.path.join(self.output_path, ".gitignore"), "w") as fp:
            fp.write(self.gitignore)

    @abc.abstractclassmethod
    def generate_methods(cls, *args, **kwargs):
        pass

    @abc.abstractclassmethod
    def generate_class(cls, *args, **kwargs):
        pass

    @abc.abstractclassmethod
    def generate_code(cls, *args, **kwargs):
        pass

    @abc.abstractmethod
    def generate_tests(self, *args, **kwargs):
        pass

    def init_package(self):
        self.generate_tests(get_methods(self.model_paths))

    def init_project(self):
        if os.path.exists(self.output_path):
            raise FileExistsError("The '{}' directory already exists.".format(self.output_path))

        os.makedirs(self.output_path)

        try:
            self.generate_models()
            self.generate_tests(get_methods(self.model_paths))

            if self.git:
                self.git_init()
        except Exception as error:
            logger.exception(error)
            shutil.rmtree(self.output_path)
            raise


class EmptyGenerator(Generator):
    """A class for generating an empty AltWalker project."""

    @classmethod
    def generate_methods(cls, *args, **kwargs):
        return ""

    @classmethod
    def generate_class(cls, *args, **kwargs):
        return ""

    @classmethod
    def generate_code(cls, *args, **kwargs):
        return ""

    def generate_tests(self, classes, package_name="tests"):
        os.makedirs(os.path.join(self.output_path, package_name))


class PythonGenerator(Generator):
    """A class for generating an AltWalker project for python."""

    METHODS_TEMPLATE = get_resource("data/templates/generate/python/methods.jinja")
    CLASS_TEMPLATE = get_resource("data/templates/generate/python/class.jinja")
    PYTHON_GITIGNORE = get_resource("data/templates/generate/gitignore/python.txt")

    REQUIREMENTS = get_resource("data/templates/generate/python/requirements.txt")

    @property
    def gitignore(self):
        return "{}\n{}".format(super().gitignore, self.PYTHON_GITIGNORE)

    @classmethod
    def generate_methods(cls, methods):
        env = Environment()
        template = env.from_string(cls.METHODS_TEMPLATE)
        return template.render(methods=methods)

    @classmethod
    def generate_class(cls, class_name, methods):
        env = Environment(trim_blocks=True)
        template = env.from_string(cls.CLASS_TEMPLATE)
        return template.render(class_name=class_name, methods=methods)

    @classmethod
    def generate_code(cls, classes):
        code = [cls.generate_class(class_name, methods) for class_name, methods in classes.items()]
        return "\n{}".format("\n\n".join(code))

    def generate_requirements(self):
        with open(os.path.join(self.output_path, "requirements.txt"), "w") as fp:
            fp.write(self.REQUIREMENTS)

    def generate_tests(self, classes, package_name="tests"):
        self.generate_requirements()

        base_path = os.path.join(self.output_path, package_name)
        os.makedirs(base_path)

        open(os.path.join(base_path, "__init__.py"), "w").close()

        with open(os.path.join(base_path, "test.py"), "w") as fp:
            fp.write(self.generate_code(classes))


class DotnetGenerator(Generator):
    """A class for generating an AltWalker project for dotnet."""

    VERSION_WILDCARD = ".".join(VERSION.split(".")[:2]) + ".*"
    CSPROJ_TEMPLATE = get_resource("data/templates/generate/dotnet/csproj.jinja")

    METHOD_TEMPLATE = get_resource("data/templates/generate/dotnet/method.txt")
    CLASS_TEMPLATE = get_resource("data/templates/generate/dotnet/class.txt")
    NAMESPACE_TEMPLATE = get_resource("data/templates/generate/dotnet/namespace.txt")
    MAIN_TEMPLATE = get_resource("data/templates/generate/dotnet/main.txt")

    DOTNET_GITIGNORE = get_resource("data/templates/generate/gitignore/dotnet.txt")

    @property
    def gitignore(self):
        return "{}\n{}".format(super().gitignore, self.DOTNET_GITIGNORE)

    @classmethod
    def generate_methods(cls, methods):
        code = [cls.METHOD_TEMPLATE.format(name) for name in methods]
        return "\n".join(code)

    @classmethod
    def generate_class(cls, class_name, methods):
        return cls.CLASS_TEMPLATE.format(class_name, cls.generate_methods(methods))

    @classmethod
    def generate_csproj(cls):
        env = Environment()
        template = env.from_string(cls.CSPROJ_TEMPLATE)
        return template.render(version=cls.VERSION_WILDCARD)

    @classmethod
    def generate_code(cls, classes, namespace="Tests"):
        code = [cls.generate_class(class_name, methods) for class_name, methods in classes.items()]
        code = "\n{}\n".format("\n\n".join(code))

        code += cls.MAIN_TEMPLATE.format(
            "\n".join(["            service.RegisterModel<{}>();".format(name) for name in classes.keys()])
        )

        return cls.NAMESPACE_TEMPLATE.format(namespace, code)

    def generate_tests(self, classes, package_name="tests"):
        base_path = os.path.join(self.output_path, package_name)
        namespace = _normalize_namespace("{}.{}".format(self.project_name, package_name))

        os.makedirs(base_path)

        with open(os.path.join(base_path, "{}.csproj".format(package_name)), "w") as fp:
            fp.write(self.generate_csproj())

        with open(os.path.join(base_path, "Program.cs"), "w") as fp:
            fp.write(self.generate_code(classes, namespace=namespace))


GeneratorFactory = Factory({
    "python": PythonGenerator,
    "py": PythonGenerator,
    "dotnet": DotnetGenerator,
    "c#": DotnetGenerator,
}, default=EmptyGenerator)


def get_supported_languages():
    return GeneratorFactory.keys()


def generate_methods(methods, language=None):
    cls = GeneratorFactory.get(language)
    return cls.generate_methods(methods)


def generate_class(class_name, methods, language=None):
    cls = GeneratorFactory.get(language)
    return cls.generate_class(class_name, methods)


def generate_code(model_paths=None, language=None):
    cls = GeneratorFactory.get(language)
    return cls.generate_code(model_paths=model_paths)


def generate_tests(output_path, model_paths=None, language=None):
    cls = GeneratorFactory.get(language)
    generator = cls(output_path, model_paths=model_paths)
    return generator.init_package()


def init_project(output_path, model_paths=None, language=None, git=True):
    """Initiates a new project.

    Args:
        output_path: The path to the project root.
        model_paths: A sequence of path to model files.
        language: The language of the project (e.g. python).
        git: If set to ``True`` will initialize a git repository and commit the files.

    Raises:
        FileExistsError: If the path ``output_path`` already exists.
    """

    cls = GeneratorFactory.get(language)
    generator = cls(output_path, model_paths=model_paths, git=git)
    return generator.init_project()
