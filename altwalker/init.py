import os
import shutil

from git import Repo

from altwalker.model import get_methods, check_models


_DEFAULT_MODEL = """{
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


def _copy_models(output_dir, model_paths):
    """Copy al models in output_dir."""

    os.makedirs(output_dir)

    for model_path in model_paths:
        _, file_name = os.path.split(model_path)
        shutil.copyfile(model_path, os.path.join(output_dir, file_name))


def _create_default_model(output_dir):
    """Save the default model in output_dir."""

    os.makedirs(output_dir)

    with open(os.path.join(output_dir, "default.json"), "w") as fp:
        fp.write(_DEFAULT_MODEL)


def _git_init(output_dir):
    """Create a local repository and commit all files."""

    repo = Repo.init(output_dir)

    repo.git.add("--all")
    repo.index.commit("Initial commit")


def generate_tests(output_dir, model_paths, package_name="tests"):
    """Generate a test package form the methods."""

    methods = get_methods(model_paths)

    os.makedirs(os.path.join(output_dir, package_name))

    try:
        with open(os.path.join(output_dir, package_name, "__init__.py"), "w"):
            pass

        with open(os.path.join(output_dir, package_name, "test.py"), "w") as fp:

            for mode_name, methods in methods.items():

                fp.write("\n")
                fp.write("class {}:\n\n".format(mode_name))

                for method in methods:
                    fp.write("\tdef {}(self):\n".format(method))
                    fp.write("\t\tpass\n")
                    fp.write("\n")

    except Exception:
        shutil.rmtree(output_dir)
        raise


def init_repo(output_dir, model_paths=None, no_git=False):
    """Initiates a new AltWalker git repository."""

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

        generate_tests(output_dir, model_paths)
        if not no_git:
            _git_init(output_dir)
    except Exception:
        shutil.rmtree(output_dir)
        raise
