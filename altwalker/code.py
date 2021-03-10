"""A collection of util functions for validating code against model(s)."""

import os
import itertools

import altwalker.graphwalker as graphwalker
from altwalker.exceptions import ValidationException
from altwalker.model import _read_json, validate_models
from altwalker.executor import create_executor


def _is_element_blocked(element, blocked=False):
    return blocked and element.get("properties", {}).get("blocked", False)


def _json_methods(model_path, blocked=False):
    """Return for each model its name and a list of unique names of vertices and edges in the model."""

    methods = dict()
    models = _read_json(model_path)

    for model in models["models"]:
        name = model["name"]

        vertices = {vertex["name"] for vertex in model["vertices"] if not _is_element_blocked(vertex, blocked=blocked)}
        edges = {edge["name"] for edge in model["edges"] if not _is_element_blocked(edge, blocked=blocked)}

        edges = edges.difference(vertices)

        methods[name] = sorted(vertices) + sorted(edges)

    return methods


def _graphml_methods(model_path, blocked=False):
    """Return the model name and a list of unique names of vertices and edges in the model."""

    _, file_name = os.path.split(model_path)
    model_name = file_name.replace(".graphml", "")

    methods = dict()
    methods[model_name] = set(graphwalker.methods(model_path, blocked=blocked))

    return methods


def get_methods(model_paths, blocked=False):
    """Return all required methods for all models.

    Args:
        model_paths (:obj:`list`): A sequence of path to model files.
        blocked (:obj:`bool`): If set to true will filter out elements with the keyword ``blocked``.

    Returns:
        dict: A dict containing each model name as a key and a list containing its required methods as values.
    """

    methods = dict()

    for path in model_paths:
        if path.endswith(".json"):
            methods.update(_json_methods(path, blocked=blocked))
        elif path.endswith(".graphml"):
            methods.update(_graphml_methods(path, blocked=blocked))

    return methods


def get_missing_methods(executor, methods):
    """Return all not implemented methods for all models."""

    missing_methods = dict()

    for model, elements in methods.items():
        missing_methods[model] = set()

        for element in elements:
            if not executor.has_step(model, element):
                missing_methods[model].add(element)

        if not missing_methods[model]:
            missing_methods.pop(model)

    return missing_methods


def _validate_code(executor, methods):
    issues = dict()

    for model, elements in methods.items():
        issues[model] = set()

        if not executor.has_model(model):
            issues[model].add("Expected to find class '{}'.".format(model))

        for element in elements:
            if not executor.has_step(model, element):
                issues[model].add("Expected to find method '{}' in class '{}'.".format(element, model))

    return issues


def validate_code(executor, methods):
    """Validate code against a dict of methods.

    Args:
        executor (:obj:`~altwalker.executor.Executor`): An executor object.
        methods (:obj:`dict`): A dict of methods.

    Raises:
        ValidationException: If the code is not valid.
    """

    issues = _validate_code(executor, methods)
    issues_messages = set(itertools.chain(*issues.values()))

    if issues_messages:
        raise ValidationException("\n".join(issues_messages))


def verify_code(path, executor, model_paths, url):
    """Verify test code against the model(s).

    Args:
        path (:obj:`str`): The path to the project root.
        executor (:obj:`str`): The type of executor.
        model_paths (:obj:`list`): A sequence of path to model files.
        url (:obj:`str`): The URL of the executor service (e.g http://localhost:5000/).

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
