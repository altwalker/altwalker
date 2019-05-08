import os
import re
import shutil

from git import Repo

from altwalker.model import get_methods, check_models
from altwalker.__version__ import VERSION


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

_CSHARP_CSPROJ = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>netcoreapp2.2</TargetFramework>
    <AspNetCoreHostingModel>InProcess</AspNetCoreHostingModel>
    <RootNamespace>{}</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="AltWalker.Executor" Version="{}" />
  </ItemGroup>
</Project>
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

    repo = Repo.init(path)

    repo.git.add("--all")
    repo.index.commit("Initial commit")


def generate_empty_tests(output_dir, tests_dir="tests"):
    """Generate an empty tests directory."""

    os.makedirs(os.path.join(output_dir, tests_dir))


def generate_python_tests(output_dir, methods, package_name="tests"):
    """Generate a python test package from the models."""

    os.makedirs(os.path.join(output_dir, package_name))

    with open(os.path.join(output_dir, package_name, "__init__.py"), "w"):
        pass

    with open(os.path.join(output_dir, package_name, "test.py"), "w") as fp:
        for model_name, methods in methods.items():
            fp.write("\n")
            fp.write("class {}:\n\n".format(model_name))

            for method in methods:
                fp.write("\tdef {}(self):\n".format(method))
                fp.write("\t\tpass\n")
                fp.write("\n")


def generate_csharp_tests(output_dir, methods, package_name="tests"):
    """Generate a C# test package from the models."""

    _, project_name = os.path.split(output_dir)
    namespace = _normalize_namespace(project_name + "." + package_name)
    project_path = os.path.join(output_dir, package_name)

    os.makedirs(project_path)

    with open(os.path.join(project_path, "{}.csproj".format(package_name)), "w") as fp:
        fp.write(_CSHARP_CSPROJ.format(namespace, VERSION))

    with open(os.path.join(project_path, "Program.cs"), "w") as program:
        program.write("using Altom.AltWalker;\n\n")
        program.write("namespace {} {{\n\n".format(namespace))
        program.write("\tpublic class Program {\n\n")
        program.write("\t\tpublic static void Main(string[] args) {\n")
        program.write("\t\t\tExecutorService service = new ExecutorService();\n")
        for model_name, methods in methods.items():
            program.write("\t\t\tservice.RegisterModel<{}>();\n".format(model_name))

            with open(os.path.join(project_path, "{}.cs".format(model_name)), "w") as model:
                model.write("namespace {} {{\n\n".format(namespace))
                model.write("\tpublic class {} {{\n\n".format(model_name))

                for method in methods:
                    model.write("\t\tpublic void {}() {{\n".format(method))
                    model.write("\t\t}\n")
                    model.write("\n")

                model.write("\t}\n")
                model.write("}\n")

        program.write("\t\t\tservice.Run(args);\n")
        program.write("\t\t}\n")
        program.write("\t}\n")
        program.write("}\n")


def generate_tests(output_dir, model_paths, language=None):
    """Generate tests for an language."""

    methods = get_methods(model_paths)

    try:
        if language == "python":
            return generate_python_tests(output_dir, methods)
        if language == "c#" or language == "dotnet":
            return generate_csharp_tests(output_dir, methods)
        if not language:
            return generate_empty_tests(output_dir)
    except Exception:
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        raise

    raise ValueError("'{}' is not a supported language.".format(language))


def init_project(output_dir, language, model_paths=None, git=True):
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
        raise FileExistsError("The {} directory already exists.".format(output_dir))

    if model_paths:
        check_models([(model_path, "random(never)") for model_path in model_paths])

    os.makedirs(output_dir)

    try:
        if model_paths:
            _copy_models(os.path.join(output_dir, "models"), model_paths)
        else:
            _create_default_model(os.path.join(output_dir, "models"))
            model_paths = [os.path.join(output_dir, "models", "default.json")]

        generate_tests(output_dir, model_paths, language)

        if git:
            _git_init(output_dir)
    except Exception:
        shutil.rmtree(output_dir)
        raise
