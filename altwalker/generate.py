"""A collection of util functions for generating code form model(s)."""

import os
import re
import shutil
import logging
import warnings

from altwalker.__version__ import VERSION
from altwalker._utils import has_git
from altwalker.exceptions import AltWalkerException
from altwalker.code import get_methods


logger = logging.getLogger(__name__)

MINOR_VERSION = ".".join(VERSION.split(".")[:2]) + ".*"

_PYTHON_CLASS_TEMPLATE = """\
class {}:

{}
"""

_PYTHON_METHOD_TEMPLATE = """\
    def {}(self):
        pass
"""

_DOTNET_NAMESPACE_TEMPLATE = """\
using Altom.AltWalker;

namespace {}
{{
{}
}}
"""

_DOTNET_MAIN_TEMPLATE = """\
    public class Program
    {{

        public static void Main(string[] args)
        {{
            ExecutorService service = new ExecutorService();
{}
            service.Run(args);
        }}
    }}
"""

_DOTNET_CLASS_TEMPLATE = """\
    public class {}
    {{

{}
    }}
"""

_DOTNET_METHOD_TEMPLATE = """\
        public void {}()
        {{
        }}
"""

_DOTNET_CSPROJ = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>netcoreapp2.1</TargetFramework>
    <AspNetCoreHostingModel>InProcess</AspNetCoreHostingModel>
    <RootNamespace>{}</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="AltWalker.Executor" Version="{}" />
  </ItemGroup>
</Project>
"""

_DEFAULT_MODEL = """\
{
    "name": "Default model",
    "models": [
        {
            "name": "ModelName",
            "generator": "random(edge_coverage(100) && vertex_coverage(100))",
            "startElementId": "v0",
            "vertices": [
                {
                    "id": "v0",
                    "name": "vertex_A"
                },
                {
                    "id": "v1",
                    "name": "vertex_B"
                }
            ],
            "edges": [
                {
                    "id": "e0",
                    "name": "edge_A",
                    "sourceVertexId": "v0",
                    "targetVertexId": "v1"
                }
            ]
        }
    ]
}
"""


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


def init_project(output_dir, model_paths=None, language=None, git=True):
    """Initiates a new project.

    Args:
        output_dir: The path to the project root.
        language: The language of the project (e.g. python).
        model_paths: A sequence of path to model files.
        git: If set to ``True`` will initialize a git repository and commit the files.

    Raises:
        FileExistsError: If the path ``output_dir`` already exists.
    """

    if os.path.exists(output_dir):
        raise FileExistsError("The '{}' directory already exists.".format(output_dir))

    os.makedirs(output_dir)

    try:
        if model_paths:
            _copy_models(os.path.join(output_dir, "models"), model_paths)
        else:
            _create_default_model(os.path.join(output_dir, "models"))
            model_paths = [os.path.join(output_dir, "models", "default.json")]

        generate_tests(output_dir, model_paths, language=language)

        if git:
            _git_init(output_dir)
    except Exception as ex:
        logger.exception(ex)
        shutil.rmtree(output_dir)
        raise
