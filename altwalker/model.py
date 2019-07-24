"""A collection of util functions for validating model(s) and code."""

import os
import json
import keyword

import altwalker.graphwalker as graphwalker
from altwalker.executor import create_executor
from altwalker.exceptions import ValidationException


PYTHON_KEYWORDS = {element.lower() for element in keyword.kwlist}

CSHARP_KEYWORDS = {
    "abstract", "add", "alias", "as", "ascending", "async", "await", "base",
    "bool", "break", "by", "byte", "case", "catch", "char", "checked", "class",
    "const", "continue", "decimal", "default", "delegate", "descending", "do",
    "double", "dynamic", "else", "enum", "equals", "event", "explicit", "extrem",
    "false", "finally", "fixed", "float", "for", "foreach", "from", "get", "global",
    "goto", "group", "if", "implicit", "in", "int", "interface", "internal", "into",
    "is", "join", "let", "lock", "long", "nameof", "namespace", "new", "null", "object",
    "on", "operator", "orderby", "out", "override", "params", "partial", "private",
    "protected", "public", "readonly", "ref", "remove", "return", "sbyte", "sealed",
    "select", "set", "short", "static", "struct", "switch", "this", "throw", "true",
    "try", "typeof", "uint", "ulong", "unchecked", "value", "var", "virtual", "void",
    "volatile", "when", "where", "while", "yield"
}


def _read_json(path):
    """Deserialize json file from a path into an object."""

    with open(path) as fp:
        try:
            data = json.load(fp)
        except ValueError as error:
            raise ValidationException("Invalid json file: {}: {}.".format(path, str(error)))

    return data


def _is_keyword(name):
    """Check if the name is a keyword."""

    normalized = name.lower()
    return normalized in PYTHON_KEYWORDS or normalized in CSHARP_KEYWORDS


def validate_element(name):
    """Validate name as a python identifier."""

    return not _is_keyword(name) and name.isidentifier()


def validate_model(model_json):
    """Validate modules, vertices and edges as python identifiers.

    Raises:
        ValidationException: If the model is not a valid model.
    """

    message = ""
    error = "Invalid {} name: {}.\n"

    for model in model_json["models"]:
        if not validate_element(model["name"]):
            message += error.format("model", model["name"])

        for vertex in model["vertices"]:
            if not validate_element(vertex["name"]):
                message += error.format("vertex", vertex["name"])

        for edge in model["edges"]:
            if not validate_element(edge["name"]):
                message += error.format("edge", edge["name"])

    if message:
        raise ValidationException(message)


def validate_models(models_path):
    """Validate models from a list of paths.

    Args:
        model_paths: A sequence of path to model files.

    Raises:
        ValidationException: If the model is not a valid model.
    """

    for model_path in models_path:
        model = _read_json(model_path)
        validate_model(model)


def validate_code(executor, methods):
    """Validate code against a dict of methods.

    Raises:
        ValidationException: If the code is not valid.
    """

    message = ""

    for model, elements in methods.items():

        if not executor.has_model(model):
            message += "Expected to find class {}.\n".format(model)

        for element in elements:
            if not executor.has_step(model, element):
                message += "Expected to find {} method in class {}.\n".format(element, model)

    if message:
        raise ValidationException(message)


def verify_code(path, executor, model_paths, url):
    """Verify test code against the model(s).

    Args:
        path: The path to the project root.
        package: The name of the package inside the project root.
        model_paths: A sequence of path to model files.

    Raises:
        GraphWalkerException: If an error is raised by the methods command.
        ValidationException: If the model(s) or the code are not a valid.
    """

    executor = create_executor(path, executor, url)
    try:
        validate_models(model_paths)
        methods = get_methods(model_paths)

        validate_code(executor, methods)
    finally:
        executor.kill()


def _is_element_blocked(element, blocked=False):
    return not (blocked and element.get("properties", {}).get("blocked", False))


def _json_methods(model_path, blocked=False):
    """Return for each model its name and a list of unique names of vertices and edges in the model."""

    result = dict()
    models = _read_json(model_path)

    for model in models["models"]:
        name = model["name"]

        vertices = [vertex["name"] for vertex in model["vertices"] if _is_element_blocked(vertex, blocked=blocked)]
        edges = [edge["name"] for edge in model["edges"] if _is_element_blocked(edge, blocked=blocked)]

        result[name] = sorted(set(vertices + edges))

    return result


def _graphml_methods(model_path, blocked=False):
    """Return the model name and a list of unique names of vertices and edges in the model."""

    _, file_name = os.path.split(model_path)
    model_name = file_name.replace(".graphml", "")

    result = dict()
    result[model_name] = sorted(set(graphwalker.methods(model_path, blocked=blocked)))

    return result


def get_methods(model_paths, blocked=False):
    """Return all requrired methods for all models.

    Args:
        model_paths: A sequence of path to model files.

    Returns:
        A dict containing each model name as a key and a lsit containing its required methods as values.
    """

    result = dict()

    for path in model_paths:
        if path.endswith(".json"):
            result.update(_json_methods(path, blocked=blocked))
        elif path.endswith(".graphml"):
            result.update(_graphml_methods(path, blocked=blocked))

    return result


def check_models(models, blocked=False):
    """Check and analyze the model(s) for issues.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.

    Raises:
        GraphWalkerException: If an error is raised by the check command.
        ValidationException: If the model is not a valid model.
    """

    validate_models([model_path for model_path, _ in models if model_path.endswith(".json")])

    output = graphwalker.check(models, blocked=blocked)
    if not output.startswith("No issues found with the model(s)"):
        raise ValidationException(output)


def get_models(model_paths):
    """Combine all models in one json object for GraphWalker REST /load.

    Args:
        model_paths: A sequence of path to model files, only ``.json`` files.

    Returns:
        A json object containing all models.

    Raises:
        ValidationException: If the model is not a valid model.
    """

    models = {
        "models": []
    }

    for path in model_paths:
        model = _read_json(path)
        models["models"].extend(model["models"])

        if not models.get("name"):
            models["name"] = model["name"]

    return models
