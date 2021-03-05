"""A collection of util functions for validating model(s)."""

import json
import keyword
import itertools
from collections import defaultdict

from altwalker.exceptions import ValidationException
import altwalker.graphwalker as graphwalker


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


def get_models(model_paths):
    """Combine all models in one json object for GraphWalker REST /load.

    Args:
        model_paths: A sequence of path to model files, only ``.json`` files.

    Returns:
        dict: A json object containing all models.

    Raises:
        ValidationException: If the model is not a valid json.
    """

    models = {
        "models": []
    }

    for path in model_paths:
        model = _read_json(path)

        current_models = model.get("models", [])
        for model in current_models:
            model["sourceFile"] = path

        models["models"].extend(current_models)

        if not models.get("name"):
            models["name"] = model.get("name", "")

    if not models.get("name"):
        models["name"] = "Unnamed Model Suite"

    return models


def _is_keyword(name):
    """Check if the name is a keyword."""

    normalized = name.lower()
    return normalized in PYTHON_KEYWORDS or normalized in CSHARP_KEYWORDS


def _validate_element_name(name):
    issues = set()

    if _is_keyword(name):
        issues.add("Name '{}' is a reserve keyword.".format(name))

    if not name.isidentifier():
        issues.add("Name '{}' is not a valid identifier.".format(name))

    return issues


def _validate_actions(element_id, actions_json):
    issues = set()

    if not isinstance(actions_json, list):
        issues.add(
            "Edge '{}' has invalid actions. Actions must be a list of strings."
            .format(element_id)
        )
        return issues

    for action in actions_json:
        if not isinstance(action, str):
            issues.add(
                "Edge '{}' has an invalid action. Each action must be a string."
                .format(element_id)
            )
        elif not action:
            issues.add(
                "Edge '{}' has an invalid action. Action cannot be an empty string."
                .format(element_id)
            )

    return issues


def _validate_requirements(element_id, requirements_json):
    issues = set()

    if not isinstance(requirements_json, list):
        issues.add(
            "Vertex '{}' has invalid requirements. Requirements must be a list of strings."
            .format(element_id)
        )
        return issues

    for requirement in requirements_json:
        if not isinstance(requirement, str):
            issues.add(
                "Vertex '{}' has an invalid requirement. Each requirements must be a string."
                .format(element_id)
            )
        elif not requirement:
            issues.add(
                "Vertex '{}' has an invalid requirement. Requirement cannot be an empty string."
                .format(element_id)
            )

    return issues


def _validate_weight(element_id, weight):
    issues = set()

    if weight and (not isinstance(weight, float) or weight < 0 or weight > 1):
        issues.add(
            "Edge '{}' has an ivalid weight of: {}. The weight must be a value between 0 and 1."
            .format(element_id, weight)
        )

    return issues


def _validate_dependency(element_id, dependency):
    if not dependency:
        return set()

    if isinstance(dependency, str) and dependency.isdigit():
        return set()

    if isinstance(dependency, int):
        return set()

    return {
        "Edge '{}' has an ivalid dependency of: {}. The dependency must be a valid integer number."
        .format(element_id, dependency)
    }


def _validate_vertex(vertex_json):
    issues = set()

    id = vertex_json.get("id", "")
    if not id:
        issues.add("Each vertex must have an id.")
        return issues

    name = vertex_json.get("name", "")
    if not name:
        issues.add("Vertex '{}' doesn't have a name.".format(id))
    else:
        issues.update(_validate_element_name(name))

    shared_state = vertex_json.get("sharedState", "")
    if not isinstance(shared_state, str):
        issues.add("Vertex '{}' has an invalid sharedState. Shared states must be strings.".format(id))

    return issues


def _validate_edge(edge_json, is_start_element=False):
    issues = set()

    element_id = edge_json.get("id")
    if not element_id:
        issues.add("Each edge must have an id.")
        return issues

    name = edge_json.get("name")
    if name:
        issues.update(_validate_element_name(name))

    if not is_start_element and not edge_json.get("sourceVertexId"):
        issues.add(
            "Edge '{}' is not a start element and it doesn't have a sourceVertexId."
            .format(element_id)
        )

    if not edge_json.get("targetVertexId"):
        issues.add("Edge '{}' doesn't have a targetVertexId.".format(element_id))

    guard = edge_json.get("guard")
    if guard is not None and not isinstance(guard, str):
        issues.add("Edge '{}' has an ivalid guard. The guard must be a string.".format(element_id))

    issues.update(_validate_weight(element_id, edge_json.get("weight")))
    issues.update(_validate_dependency(element_id, edge_json.get("dependency")))

    return issues


def _validate_model(model_json):
    issues = set()

    has_start_element = False
    start_element_found = False
    has_shared_state = False

    name = model_json.get("name")
    if not name:
        issues.add("Each model must have a name.")
    else:
        issues.update(_validate_element_name(name))

    generator = model_json.get("generator")
    if not generator:
        issues.add("Each model must have a generator.")
    elif not isinstance(generator, str):
        issues.add("The generator must be a string.")

    start_element_id = model_json.get("startElementId")
    if start_element_id:
        has_start_element = True

    vertices = model_json.get("vertices", None)
    if vertices is None:
        issues.add("Each model must have a list of vertices.")
    else:
        for vertex in vertices:
            element_id = vertex.get("id")

            if start_element_id and element_id == start_element_id:
                start_element_found = True

            shared_state = vertex.get("sharedState")
            if shared_state:
                has_shared_state = True

            issues.update(_validate_vertex(vertex))

    edges = model_json.get("edges", None)
    if edges is None:
        issues.add("Each model must have a list of edges.")
    else:
        for edge in edges:
            element_id = edge.get("id")

            if start_element_id and element_id == start_element_id:
                start_element_found = True

            issues.update(_validate_edge(edge, is_start_element=element_id == start_element_id))

    if not has_start_element and not has_shared_state:
        issues.add("Model has neither a starting element nor a shared state.")

    if start_element_id and not start_element_found:
        issues.add("Starting element '{}' was not found.".format(start_element_id))

    return issues


def _validate_models(models_json):
    models = models_json.get("models", None)

    issues = defaultdict(set)
    ids = defaultdict(int)

    if not models:
        issues["global"].add("No models found.")

    for model in models:
        key = "{}::{}".format(model.get("sourceFile", "UnknownSourceFile"), model.get("name", "UnnamedModel"))
        issues[key].update(_validate_model(model))

        for element in itertools.chain(model.get("edges", []), model.get("vertices", [])):
            element_id = element.get("id")

            if element_id:
                ids[element_id] += 1

            if element_id and ids[element_id] > 1:
                issues[key].add("Id '{}' is not unique.".format(element_id))

    return issues


def validate_json_models(model_json):
    """Validate modules, vertices and edges as python identifiers.

    Args:
        model_json (:obj:`dict`): A models object.

    Raises:
        ValidationException: If the model is not a valid model.
    """

    issues = _validate_models(model_json)
    issues_messages = set(itertools.chain(*issues.values()))

    if issues_messages:
        raise ValidationException("\n".join(issues_messages))


def validate_models(model_paths):
    """Validate models from a list of paths.

    Args:
        model_paths (:obj:`list`): A sequence of path to model files.

    Raises:
        ValidationException: If the model is not a valid model.
    """

    json_models = get_models(model_paths)
    validate_json_models(json_models)


def check_models(models, blocked=False):
    """Check and analyze the model(s) for issues.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        blocked (:obj:`bool`): If set to true will filter out elements with the keyword ``blocked``.

    Raises:
        GraphWalkerException: If an error is raised by the check command.
        ValidationException: If the models are not valid models.
    """

    validate_models([model_path for model_path, _ in models if model_path.endswith(".json")])

    output = graphwalker.check(models, blocked=blocked)

    if not output.startswith("No issues found with the model(s)"):
        raise ValidationException(output)
