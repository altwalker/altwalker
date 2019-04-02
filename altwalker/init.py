import os
import shutil
from os.path import join as path_join

from git import Repo

from altwalker.model import get_methods, check_models
from altwalker.__version__ import VERSION


_DEFAULT_MODEL = """{
    "name": "Default model",
    "models": [{
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
    }]
}
"""


def _copy_models(output_dir, model_paths):
    """Copy al models in output_dir."""

    os.makedirs(output_dir)

    for model_path in model_paths:
        _, file_name = os.path.split(model_path)
        shutil.copyfile(model_path, path_join(output_dir, file_name))


def _create_default_model(output_dir):
    """Save the default model in output_dir."""

    os.makedirs(output_dir)

    with open(path_join(output_dir, "default.json"), "w") as fp:
        fp.write(_DEFAULT_MODEL)


def _git_init(output_dir):
    """Create a local repository and commit all files."""

    repo = Repo.init(output_dir)

    repo.git.add("--all")
    repo.index.commit("Initial commit")


def generate_tests(output_dir, model_paths, language):
    methods = get_methods(model_paths)

    try:
        if language == "python":
            return generate_tests_python(output_dir, methods)

        if language == "c#":
            return generate_tests_csharp(output_dir, methods)
    except Exception:
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        raise

    raise ValueError("{} is not supported.".format(language))


def generate_tests_csharp(output_dir, methods):
    """Generate a c# test package from the models."""
    _, tests_proj_name = os.path.split(output_dir)
    tests_proj_name = tests_proj_name+".Tests"
    tests_proj_path = path_join(output_dir, tests_proj_name)
    os.makedirs(tests_proj_path)

    with open(path_join(tests_proj_path, "{}.csproj".format(tests_proj_name)), "w") as proj:
        proj.write("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>netcoreapp2.2</TargetFramework>
    <AspNetCoreHostingModel>InProcess</AspNetCoreHostingModel>
    <RootNamespace>{}</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Altwalker.Executor" Version="{}" />
  </ItemGroup>
</Project>""".format(tests_proj_name, VERSION))

    with open(path_join(tests_proj_path, "Program.cs"), "w") as program:
        program.write("using Altom.Altwalker;\n")
        program.write("namespace {} {{\n".format(tests_proj_name))
        program.write("\tpublic class Program {\n")
        program.write("\t\tpublic static void Main (string[] args) {\n")
        program.write("\t\t\tExecutorService service = new ExecutorService();\n")
        for model_name, methods in methods.items():
            program.write("\t\t\tservice.RegisterModel<{}>();\n".format(model_name))

            with open(path_join(tests_proj_path, "{}.cs".format(model_name)), "w") as model:
                model.write("namespace {} {{\n".format(tests_proj_name))
                model.write("\tpublic class {} {{\n".format(model_name))

                for method in methods:
                    model.write("\t\tpublic void {}(){{\n".format(method))
                    model.write("\t\t}\n")
                    model.write("\n")

                model.write("\t}\n")
                model.write("}\n")
        program.write("\t\t\tservice.Run(args);\n")
        program.write("\t\t}\n")
        program.write("\t}\n")
        program.write("}\n")


def generate_tests_python(output_dir, methods, package_name="tests"):
    """Generate a python test package from the models."""

    os.makedirs(path_join(output_dir, package_name))

    with open(path_join(output_dir, package_name, "__init__.py"), "w"):
        pass

    with open(path_join(output_dir, package_name, "test.py"), "w") as fp:

        for model_name, methods in methods.items():

            fp.write("\n")
            fp.write("class {}:\n\n".format(model_name))

            for method in methods:
                fp.write("\tdef {}(self):\n".format(method))
                fp.write("\t\tpass\n")
                fp.write("\n")


def init_repo(output_dir, language, model_paths=None, no_git=False):
    """Initiates a new AltWalker git repository."""

    if os.path.exists(output_dir):
        raise FileExistsError("The {} directory already exists.".format(output_dir))

    if model_paths:
        check_models([(model_path, "random(never)") for model_path in model_paths])

    os.makedirs(output_dir)

    try:
        if model_paths:
            _copy_models(path_join(output_dir, "models"), model_paths)
        else:
            _create_default_model(path_join(output_dir, "models"))
            model_paths = [path_join(output_dir, "models", "default.json")]

        generate_tests(output_dir, model_paths, language)
        if not no_git:
            _git_init(output_dir)
    except Exception:
        shutil.rmtree(output_dir)
        raise
