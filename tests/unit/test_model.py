import itertools
import json
import os
import unittest
import unittest.mock as mock

import pytest

from altwalker.model import (CSHARP_KEYWORDS, PYTHON_KEYWORDS,
                             ValidationException, _is_keyword, _read_json,
                             _validate_actions, _validate_edge,
                             _validate_element_name, _validate_model,
                             _validate_models, _validate_requirements,
                             _validate_vertex, _validate_weight, check_models,
                             get_models, validate_json_models, validate_models)

MOCK_MODELS = {
    "name": "Mock models for tests",
    "models": [
        {
            "name": "ModelA",
            "startElementId": "v0",
            "generator": "random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "vertex_1"
                },
                {
                    "id": "v1",
                    "name": "vertex_1",
                    "sharedState": "link"
                }
            ],
            "edges": [
            ]
        },
        {
            "name": "ModelA",
            "generator": "random(never)",
            "vertices": [
                {
                    "id": "v2",
                    "name": "vertex_1",
                    "sharedState": "link"
                }
            ],
            "edges": []
        }
    ]
}

NO_MODELS = {
    "name": "Mock models for tests",
    "models": []
}

NO_NAME_MODELS = {
    "models": []
}

DUPLICATE_IDS_MODELS = {
    "name": "Mock models for tests",
    "models": [
        {
            "name": "ModelA",
            "startElementId": "v0",
            "generator": "random(vertex_coverage(100))",
            "vertices": [
                {
                    "id": "v0",
                    "name": "vertex_1"
                },
                {
                    "id": "v1",
                    "name": "vertex_1"
                }
            ],
            "edges": []
        },
        {
            "name": "ModelA",
            "startElementId": "v0",
            "generator": "random(length(25))",
            "vertices": [
                {
                    "id": "v0",
                    "name": "vertex_1"
                }
            ],
            "edges": []
        }
    ]
}

MULTIPLE_ERRORS_MODELS = {
    "name": "Mock models for tests",
    "models": [
        {
            "name": "ModelA",
            "vertices": [
                {
                    "id": "v0",
                    "name": "vertex_1"
                },
                {
                    "id": "v1",
                    "name": "vertex_1"
                }
            ],
            "edges": []
        },
        {
            "name": "ModelA",
            "vertices": [
                {
                    "id": "v0",
                    "name": "vertex_1"
                },
                {
                    "name": "vertex_2"
                }
            ],
            "edges": []
        }
    ]
}

VALID_ELEMENT_NAMES = ["method_A", "Method_A", "Method_1"]
INVALID_ELEMENT_NAMES = ["0_method", "1_method", "method a"]
CHARACTERS = "!@#$%^&*+-/=<>~`,./;:'\"][}{)(|"


class TestReadJson:

    def test_error(self):
        file_name = "error.json"

        with open(file_name, "w") as fp:
            fp.write("{,}")

        with pytest.raises(ValidationException, match=f"Invalid json file: {file_name}: .*"):
            _read_json(file_name)

        os.remove(file_name)

    def test_valid(self):
        file_name = "valid.json"

        with open(file_name, "w") as fp:
            fp.write(json.dumps(NO_MODELS))

        json_models = _read_json(file_name)
        assert json_models == NO_MODELS

        os.remove(file_name)


class TestGetModels:

    def test_no_files(self):
        result = get_models([])
        models = {
            'name': 'Unnamed Model Suite',
            'models': []
        }

        assert result == models

    def test_no_models(self):
        result = get_models(["tests/common/models/no-models.json"])
        models = {
            'name': 'No models',
            'models': []
        }

        assert result == models

    def test_one_file(self):
        result = get_models(["tests/common/models/simple.json"])
        model = _read_json("tests/common/models/simple.json")
        model["models"][0]["sourceFile"] = "tests/common/models/simple.json"

        assert len(result["models"]) == 1
        assert result["models"] == model["models"]

    def test_two_files(self):
        result = get_models(["tests/common/models/simple.json", "tests/common/models/simple.json"])
        model = _read_json("tests/common/models/simple.json")
        model["models"][0]["sourceFile"] = "tests/common/models/simple.json"

        assert len(result["models"]) == 2
        assert result["models"] == model["models"] + model["models"]

    def test_no_name(self):
        result = get_models(["tests/common/models/no-name.json"])
        assert result["name"] == "Unnamed Model Suite"


class TestIsKeyword:

    @pytest.mark.parametrize("keyword", PYTHON_KEYWORDS | CSHARP_KEYWORDS)
    def test_keyword(self, keyword):
        assert _is_keyword(keyword)

    @pytest.mark.parametrize("not_keyword", ["not_a_keyword", "definitely_not_a_keyword"])
    def test_not_keywords(self, not_keyword):
        assert not _is_keyword(not_keyword)


class TestValidateElementName:

    @pytest.mark.parametrize("name", VALID_ELEMENT_NAMES)
    def test_valid_names(self, name):
        assert _validate_element_name(name) == set()

    @pytest.mark.parametrize("name", INVALID_ELEMENT_NAMES)
    def test_invalid_identifiers(self, name):
        assert _validate_element_name(name), {f"Name '{name}' is not a valid identifier."}

    @pytest.mark.parametrize("name", [
        *[f"{name} " for name in VALID_ELEMENT_NAMES],
        *[f" {name}" for name in VALID_ELEMENT_NAMES],
        *[f" {name} " for name in VALID_ELEMENT_NAMES],
    ])
    def test_extra_spaces(self, name):
        assert _validate_element_name(name) == {f"Name '{name}' is not a valid identifier."}

    @pytest.mark.parametrize("name", [
        *[x + y for (x, y) in itertools.product(VALID_ELEMENT_NAMES, CHARACTERS)],
        *[x + y for (x, y) in itertools.product(CHARACTERS, VALID_ELEMENT_NAMES)],
    ])
    def test_invalid_characters(self, name):
        assert _validate_element_name(name) == {f"Name '{name}' is not a valid identifier."}

    @pytest.mark.parametrize("keyword", PYTHON_KEYWORDS | CSHARP_KEYWORDS)
    def test_keywords(self, keyword):
        assert _validate_element_name(keyword) == {f"Name '{keyword}' is a reserve keyword."}


class TestValidateActions:

    def test_actions(self):
        actions = [
            "a = 1",
            "b = 2"
        ]
        assert _validate_actions("v0", actions) == set()

    def test_invalid_actions(self):
        issues = {"Edge 'v0' has invalid actions. Actions must be a list of strings."}
        assert _validate_actions("v0", {}) == issues

    def test_empty_action(self):
        actions = [
            "a = 1",
            ""
        ]

        issues = {"Edge 'v0' has an invalid action. Action cannot be an empty string."}
        assert _validate_actions("v0", actions) == issues

    @pytest.mark.parametrize("action", [1, {}, []])
    def test_invalid_action(self, action):
        assert _validate_actions("v0", [action]) == {"Edge 'v0' has an invalid action. Each action must be a string."}


class TestValidateRequirements:

    def test_valid_requirements(self):
        requirements = [
            "requirement1",
            "requirement2"
        ]
        assert _validate_requirements("v0", requirements) == set()

    def test_invalid_requirements(self):
        requirements = {}
        issues = {"Vertex 'v0' has invalid requirements. Requirements must be a list of strings."}

        assert _validate_requirements("v0", requirements) == issues

    def test_empty_requirement(self):
        requirements = [
            "requirement1",
            ""
        ]
        issues = {"Vertex 'v0' has an invalid requirement. Requirement cannot be an empty string."}

        assert _validate_requirements("v0", requirements) == issues

    @pytest.mark.parametrize("requirement", [1, {}, []])
    def test_invalid_requirement(self, requirement):
        issues = {"Vertex 'v0' has an invalid requirement. Each requirements must be a string."}
        assert _validate_requirements("v0", [requirement]) == issues


class TestValidateWeight:

    @pytest.mark.parametrize("weight", [x / 10.0 for x in range(0, 11, 1)])
    def test_valid_weight(self, weight):
        assert _validate_weight("e0", weight) == set()

    @pytest.mark.parametrize("weight", [
        *[x / 10.0 for x in range(-10, 0, 1)],
        *[x / 10.0 for x in range(11, 20, 1)]
    ])
    def test_invalid_weight(self, weight):
        issues = {f"Edge 'e0' has an invalid weight of: {weight}. The weight must be a value between 0 and 1."}
        assert _validate_weight("e0", weight) == issues


class TestValidateVertex:

    def test_valid(self):
        vertex = {
            "id": "v1",
            "name": "v_name"
        }

        assert _validate_vertex(vertex) == set()

    def test_no_id(self):
        vertex = {
            "name": "v_name"
        }

        assert _validate_vertex(vertex) == {"Each vertex must have an id."}

        vertex = {
            "id": "",
            "name": "v_name"
        }

        assert _validate_vertex(vertex) == {"Each vertex must have an id."}

    def test_no_name(self):
        vertex = {
            "id": "v0"
        }

        assert _validate_vertex(vertex) == {"Vertex 'v0' doesn't have a name."}

    def test_invalid_names(self):
        vertex = {
            "id": "v0",
            "name": "v name"
        }

        assert _validate_vertex(vertex) == {"Name 'v name' is not a valid identifier."}

    def test_keyword_name(self):
        vertex = {
            "id": "v0",
            "name": "return"
        }

        assert _validate_vertex(vertex) == {"Name 'return' is a reserve keyword."}

    def test_invalid_shared_state(self):
        vertex = {
            "id": "v1",
            "name": "v_name",
            "sharedState": {}
        }
        error_message = "Vertex 'v1' has an invalid sharedState. Shared states must be strings."

        assert _validate_vertex(vertex) == {error_message}


class TestValidateEdge:

    def test_valid_edge(self):
        edge = {
            "id": "e0",
            "name": "v_name",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        assert _validate_edge(edge) == set()

    def test_no_id(self):
        edge = {
            "name": "v_name",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        assert _validate_edge(edge) == {'Each edge must have an id.'}

    def test_no_name(self):
        edge = {
            "id": "e0",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        assert _validate_edge(edge) == set()

    def test_invalid_name(self):
        edge = {
            "id": "e0",
            "name": "e name",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        assert _validate_edge(edge) == {"Name 'e name' is not a valid identifier."}

    def test_keyword_name(self):
        edge = {
            "id": "e0",
            "name": "return",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        assert _validate_edge(edge) == {"Name 'return' is a reserve keyword."}

    def test_no_target_vertex_id(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v0"
        }

        assert _validate_edge(edge) == {"Edge 'e0' doesn't have a targetVertexId."}

    def test_no_source_vertex_id(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "targetVertexId": "v0"
        }

        assert _validate_edge(edge, is_start_element=True) == set()

    @pytest.mark.parametrize("weight", [
        *[x / 10.0 for x in range(0, 11, 1)]
    ])
    def test_weight(self, weight):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0",
            "weight": weight
        }

        assert _validate_edge(edge) == set()

    @pytest.mark.parametrize("weight", [-2, -1, 2, 3])
    def test_invalid_weight(self, weight):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0",
            "weight": weight
        }
        error_message = f"Edge 'e0' has an invalid weight of: {weight}. The weight must be a value between 0 and 1."

        assert _validate_edge(edge) == {error_message}

    def test_not_start_element(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "targetVertexId": "v0"
        }
        error_message = "Edge 'e0' is not a start element and it doesn't have a sourceVertexId."

        assert _validate_edge(edge, is_start_element=False) == {error_message}

    @pytest.mark.parametrize("dependency", [
        "a", "b", "c",
        "1a", "2b", "3c",
        "a1", "b2", "c3",
        "1.1", "2.2", "3.3",
        1.0, 2.0, 3.0,
        1.1, 2.2, 3.3
    ])
    def test_invalid_dependency(self, dependency):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0",
            "dependency": dependency
        }
        error_message = f"Edge 'e0' has an invalid dependency of: {dependency}. The dependency must be a valid integer number."

        assert _validate_edge(edge) == {error_message}

    @pytest.mark.parametrize("dependency", [
        "1", "2", "3", 1, 2, 3
    ])
    def test_dependency(self, dependency):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0",
            "dependency": dependency
        }

        assert _validate_edge(edge) == set()

    def test_guard(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "guard": "isTrue == true",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }

        assert _validate_edge(edge) == set()

    @pytest.mark.parametrize("guard", [1, 2, 3, {}, []])
    def test_invalid_guard(self, guard):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0",
            "guard": guard
        }

        assert _validate_edge(edge) == {"Edge 'e0' has an invalid guard. The guard must be a string."}


class TestValidateModel:

    def test_valid(self):
        model = {
            "name": "Model",
            "startElementId": "v0",
            "generator": "random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_name"
                }
            ],
            "edges": [

            ]
        }

        assert _validate_model(model) == set()

    def test_no_name(self):
        model = {
            "startElementId": "v0",
            "generator": "random(vertex_coverage(100))",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_name"
                }
            ],
            "edges": [

            ]
        }

        assert _validate_model(model) == {"Each model must have a name."}

    def test_empty_name(self):
        model = {
            "name": "",
            "startElementId": "v0",
            "generator": "quick_random(vertex_coverage(100))",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                }
            ],
            "edges": [

            ]
        }

        assert _validate_model(model) == {"Each model must have a name."}

    def test_invalid_name(self):
        model = {
            "name": "Model A",
            "startElementId": "v0",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                }
            ],
            "edges": [

            ]
        }

        assert _validate_model(model) == {"Name 'Model A' is not a valid identifier."}

    def test_keyword_name(self):
        model = {
            "name": "return",
            "startElementId": "v0",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_name"
                }
            ],
            "edges": [

            ]
        }

        assert _validate_model(model) == {"Name 'return' is a reserve keyword."}

    def test_no_vertices(self):
        model = {
            "name": "Model",
            "startElementId": "e0",
            "generator": "weighted_random(never)",
            "edges": [
                {
                    "id": "e0",
                    "name": "e_name",
                    "sourceVertexId": "v0",
                    "targetVertexId": "v1"
                }
            ]
        }

        assert _validate_model(model) == {'Each model must have a list of vertices.'}

    def test_no_edges(self):
        model = {
            "name": "Model",
            "startElementId": "v0",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_name"
                }
            ]
        }

        assert _validate_model(model) == {'Each model must have a list of edges.'}

    def test_invalid_vertex(self):
        model = {
            "name": "Model",
            "startElementId": "v0",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                },
                {
                    "name": "v_name"
                }
            ],
            "edges": [

            ]
        }

        assert _validate_model(model) == {'Each vertex must have an id.'}

    def test_invalid_edge(self):
        model = {
            "name": "Model",
            "startElementId": "v0",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                }
            ],
            "edges": [
                {
                    "name": "v_name"
                }
            ]
        }

        assert _validate_model(model) == {'Each edge must have an id.'}

    def test_invalid_generator(self):
        model = {
            "name": "Model",
            "startElementId": "v0",
            "generator": 1,
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                }
            ],
            "edges": [
            ]
        }

        assert _validate_model(model) == {'The generator must be a string.'}

    def test_start_element_no_found(self):
        model = {
            "name": "Model",
            "startElementId": "v1",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                }
            ],
            "edges": [
            ]
        }

        assert _validate_model(model) == {"Starting element 'v1' was not found."}

    def test_edge_as_start_element(self):
        model = {
            "name": "Model",
            "startElementId": "e0",
            "generator": "weighted_random(never)",
            "vertices": [
                {
                    "id": "v0",
                    "name": "v_vertex"
                }
            ],
            "edges": [
                {
                    "id": "e0",
                    "name": "e_edge",
                    "targetVertexId": "v0"
                }
            ]
        }

        assert _validate_model(model) == set()


class TestValidateModels:

    def test_no_models(self):
        issues = _validate_models(NO_MODELS)
        assert issues["global"] == {'No models found.'}

    def test_duplicate_ids(self):
        issues = _validate_models(DUPLICATE_IDS_MODELS)
        assert issues["UnknownSourceFile::ModelA"] == {"Id 'v0' is not unique."}


class TestValidateJsonModels:

    def test_valid(self):
        validate_json_models(MOCK_MODELS)

    def test_no_models(self):
        with pytest.raises(ValidationException):
            validate_json_models(NO_MODELS)

    def test_duplicate_ids(self):
        with pytest.raises(ValidationException):
            validate_json_models(DUPLICATE_IDS_MODELS)

    def test_multiple_errors(self):
        with pytest.raises(ValidationException):
            validate_json_models(MULTIPLE_ERRORS_MODELS)


@mock.patch("altwalker.model.validate_json_models")
@mock.patch("altwalker.model.get_models")
class TestValidateModels:

    def test_read_json(self, read_mock, validate_mock):
        read_mock.return_value = {}

        validate_models(["first.json", "second.json"])

        read_mock.assert_any_call(["first.json", "second.json"])

    def test_validate_model(self, read_mock, validate_mock):
        read_mock.return_value = mock.sentinel.models

        validate_models(["first.json", "second.json"])

        validate_mock.assert_any_call(mock.sentinel.models)


@mock.patch("altwalker.model.validate_models")
@mock.patch("altwalker.graphwalker.check")
class TestCheckModels:

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.models = [
            ("first.json", "stop_condition"),
            ("second.graphml", "stop_condition"),
            ("third.json", "stop_condition")
        ]

    def test_validate_models(self, check_mock, validate_mock):
        check_mock.return_value = "No issues found with the model(s)"

        check_models(self.models)

        validate_mock.assert_called_once_with(["first.json", "third.json"])

    def test_check(self, check_mock, validate_mock):
        check_mock.return_value = "No issues found with the model(s)"

        check_models(self.models)

        check_mock.assert_called_once_with(self.models, blocked=False)

    def test_check_blocked(self, check_mock, validate_mock):
        check_mock.return_value = "No issues found with the model(s)"

        check_models(self.models, blocked=True)

        check_mock.assert_called_once_with(self.models, blocked=True)

    def test_check_output(self, check_mock, validate_mock):
        check_mock.return_value = "Error message."

        with pytest.raises(ValidationException, match="Error message."):
            check_models(self.models, blocked=True)
