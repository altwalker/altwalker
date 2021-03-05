import os
import json
import unittest
import unittest.mock as mock

from altwalker.model import PYTHON_KEYWORDS, CSHARP_KEYWORDS, ValidationException, _read_json, get_models, \
    _is_keyword, _validate_element_name, _validate_actions, _validate_vertex, _validate_requirements, \
    _validate_weight, _validate_edge, _validate_model, _validate_models, validate_json_models, validate_models, \
    check_models


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


class _TestReadJson(unittest.TestCase):

    def test_error(self):
        file_name = "error.json"

        with open(file_name, "w") as fp:
            fp.write("{,}")

        with self.assertRaisesRegex(ValidationException, "Invalid json file: {}: .*".format(file_name)):
            _read_json(file_name)

        os.remove(file_name)

    def test_valid(self):
        file_name = "valid.json"

        with open(file_name, "w") as fp:
            fp.write(json.dumps(NO_MODELS))

        json_models = _read_json(file_name)
        self.assertEqual(json_models, NO_MODELS)

        os.remove(file_name)


class TestGetModels(unittest.TestCase):

    def test_no_files(self):
        result = get_models([])
        models = {
            'name': 'Unnamed Model Suite',
            'models': []
        }

        self.assertEqual(result, models)

    def test_no_models(self):
        result = get_models(["tests/common/models/no-models.json"])
        models = {
            'name': 'No models',
            'models': []
        }

        self.assertEqual(result, models)

    def test_one_file(self):
        result = get_models(["tests/common/models/simple.json"])
        model = _read_json("tests/common/models/simple.json")
        model["models"][0]["sourceFile"] = "tests/common/models/simple.json"

        self.assertEqual(len(result["models"]), 1)
        self.assertEqual(result["models"], model["models"])

    def test_two_files(self):
        result = get_models(["tests/common/models/simple.json", "tests/common/models/simple.json"])
        model = _read_json("tests/common/models/simple.json")
        model["models"][0]["sourceFile"] = "tests/common/models/simple.json"

        self.assertEqual(len(result["models"]), 2)
        self.assertEqual(result["models"], model["models"] + model["models"])

    def test_no_name(self):
        result = get_models(["tests/common/models/no-name.json"])
        self.assertEqual(result["name"], "Unnamed Model Suite")


class _TestIsKeyword(unittest.TestCase):

    def test_keyword(self):
        for keyword in PYTHON_KEYWORDS | CSHARP_KEYWORDS:
            self.assertTrue(_is_keyword(keyword))

    def test_not_kewords(self):
        for not_keyword in ["not_a_keyword", "definitely_not_a_keyword"]:
            self.assertFalse(_is_keyword(not_keyword))


class _TestValidateElementName(unittest.TestCase):
    valid_names = ["method_A", "Method_A", "Method_1"]
    invalid_names = ["0_method", "1_method", "method a"]

    def test_valid_names(self):
        for name in self.valid_names:
            self.assertEqual(_validate_element_name(name), set())

    def test_invalid_identifiers(self):
        for name in self.invalid_names:
            self.assertEqual(_validate_element_name(name), {"Name '{}' is not a valid identifier.".format(name)})

    def test_extra_spaces(self):
        for name in self.valid_names:
            name = name + " "
            self.assertEqual(_validate_element_name(name), {"Name '{}' is not a valid identifier.".format(name)})

        for name in self.valid_names:
            name = " " + name
            self.assertEqual(_validate_element_name(name), {"Name '{}' is not a valid identifier.".format(name)})

        for name in self.valid_names:
            name = " " + name + " "
            self.assertEqual(_validate_element_name(name), {"Name '{}' is not a valid identifier.".format(name)})

    def test_invalid_characters(self):
        characters = "!@#$%^&*+-/=<>~`,./;:'\"][}{)(|"

        for name in self.valid_names:
            for character in characters:
                name = character + name
                self.assertEqual(_validate_element_name(name), {"Name '{}' is not a valid identifier.".format(name)})

            for character in characters:
                name = name + character
                self.assertEqual(_validate_element_name(name), {"Name '{}' is not a valid identifier.".format(name)})

    def test_keywords(self):
        for keyword in PYTHON_KEYWORDS | CSHARP_KEYWORDS:
            self.assertEqual(_validate_element_name(keyword), {"Name '{}' is a reserve keyword.".format(keyword)})


class _TestValidateActions(unittest.TestCase):

    def test_actions(self):
        actions = [
            "a = 1",
            "b = 2"
        ]
        self.assertEqual(_validate_actions("v0", actions), set())

    def test_invalid_actions(self):
        actions = {}
        self.assertEqual(
            _validate_actions("v0", actions),
            {"Edge 'v0' has invalid actions. Actions must be a list of strings."})

    def test_empty_action(self):
        actions = [
            "a = 1",
            ""
        ]
        self.assertEqual(
            _validate_actions("v0", actions),
            {"Edge 'v0' has an invalid action. Action cannot be an empty string."})

    def test_invalid_action(self):
        actions = [
            1,
            {},
            []
        ]

        for action in actions:
            self.assertEqual(
                _validate_actions("v0", [action]),
                {"Edge 'v0' has an invalid action. Each action must be a string."})


class _TestValidateRequirements(unittest.TestCase):

    def test_valid_requirements(self):
        requirements = [
            "requirement1",
            "requirement2"
        ]
        self.assertEqual(_validate_requirements("v0", requirements), set())

    def test_invalid_requirements(self):
        requirements = {}
        self.assertEqual(
            _validate_requirements("v0", requirements),
            {"Vertex 'v0' has invalid requirements. Requirements must be a list of strings."})

    def test_empty_requirement(self):
        requirements = [
            "requirement1",
            ""
        ]
        self.assertEqual(
            _validate_requirements("v0", requirements),
            {"Vertex 'v0' has an invalid requirement. Requirement cannot be an empty string."})

    def test_invalid_requirement(self):
        requirements = [
            1,
            {},
            []
        ]

        for requirement in requirements:
            self.assertEqual(
                _validate_requirements("v0", [requirement]),
                {"Vertex 'v0' has an invalid requirement. Each requirements must be a string."})


class _TestValidateWeight(unittest.TestCase):

    def test_valid_weight(self):
        weights = [x / 10.0 for x in range(0, 11, 1)]

        for weight in weights:
            self.assertEqual(_validate_weight("e0", weight), set())

    def test_invalid_weight(self):
        weights = [x / 10.0 for x in range(-10, 0, 1)]
        weights.extend(x / 10.0 for x in range(11, 20, 1))

        for weight in weights:
            self.assertEqual(
                _validate_weight("e0", weight),
                {"Edge 'e0' has an ivalid weight of: {}. The weight must be a value between 0 and 1.".format(weight)}
            )


class _TestValidateVertex(unittest.TestCase):

    def test_valid(self):
        vertex = {
            "id": "v1",
            "name": "v_name"
        }

        self.assertEqual(_validate_vertex(vertex), set())

    def test_no_id(self):
        vertex = {
            "name": "v_name"
        }

        self.assertEqual(_validate_vertex(vertex), {"Each vertex must have an id."})

        vertex = {
            "id": "",
            "name": "v_name"
        }

        self.assertEqual(_validate_vertex(vertex), {"Each vertex must have an id."})

    def test_no_name(self):
        vertex = {
            "id": "v0"
        }

        self.assertEqual(_validate_vertex(vertex), {"Vertex 'v0' doesn't have a name."})

    def test_invalid_names(self):
        vertex = {
            "id": "v0",
            "name": "v name"
        }

        self.assertEqual(_validate_vertex(vertex), {"Name 'v name' is not a valid identifier."})

    def test_keyword_name(self):
        vertex = {
            "id": "v0",
            "name": "return"
        }

        self.assertEqual(_validate_vertex(vertex), {"Name 'return' is a reserve keyword."})

    def test_invalid_shared_state(self):
        vertex = {
            "id": "v1",
            "name": "v_name",
            "sharedState": {}
        }
        error_message = "Vertex 'v1' has an invalid sharedState. Shared states must be strings."

        self.assertEqual(_validate_vertex(vertex), {error_message})


class _TestValidateEdge(unittest.TestCase):

    def test_valid_edge(self):
        edge = {
            "id": "e0",
            "name": "v_name",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        self.assertEqual(_validate_edge(edge), set())

    def test_no_id(self):
        edge = {
            "name": "v_name",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        self.assertEqual(_validate_edge(edge), {'Each edge must have an id.'})

    def test_no_name(self):
        edge = {
            "id": "e0",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        self.assertEqual(_validate_edge(edge), set())

    def test_invalid_name(self):
        edge = {
            "id": "e0",
            "name": "e name",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        self.assertEqual(_validate_edge(edge), {"Name 'e name' is not a valid identifier."})

    def test_keyword_name(self):
        edge = {
            "id": "e0",
            "name": "return",
            "sourceVertexId": "v0",
            "targetVertexId": "v1"
        }

        self.assertEqual(_validate_edge(edge), {"Name 'return' is a reserve keyword."})

    def test_no_target_vertex_id(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v0"
        }

        self.assertEqual(_validate_edge(edge), {"Edge 'e0' doesn't have a targetVertexId."})

    def test_no_source_vertex_id(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "targetVertexId": "v0"
        }

        self.assertEqual(_validate_edge(edge, is_start_element=True), set())

    def test_weight(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }
        weights = [x / 10.0 for x in range(0, 11, 1)]

        for weight in weights:
            edge["weight"] = weight
            self.assertEqual(_validate_edge(edge), set())

    def test_invalid_weight(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }
        weights = [-2, -1, 2, 3]
        error_message = "Edge 'e0' has an ivalid weight of: {}. The weight must be a value between 0 and 1."

        for weight in weights:
            edge["weight"] = weight
            self.assertEqual(_validate_edge(edge), {error_message.format(weight)})

    def test_not_start_element(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "targetVertexId": "v0"
        }
        error_message = "Edge 'e0' is not a start element and it doesn't have a sourceVertexId."

        self.assertEqual(_validate_edge(edge, is_start_element=False), {error_message})

    def test_invalid_dependency(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }
        dependencies = [
            "a", "b", "c",
            "1a", "2b", "3c",
            "a1", "b2", "c3",
            "1.1", "2.2", "3.3",
            1.0, 2.0, 3.0,
            1.1, 2.2, 3.3
        ]
        error_message = "Edge 'e0' has an ivalid dependency of: {}. The dependency must be a valid integer number."

        for dependency in dependencies:
            edge["dependency"] = dependency
            self.assertEqual(_validate_edge(edge), {error_message.format(dependency)})

    def test_dependency(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }
        dependencies = ["1", "2", "3", 1, 2, 3]

        for dependency in dependencies:
            edge["dependency"] = dependency
            self.assertEqual(_validate_edge(edge), set())

    def test_guard(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "guard": "isTrue == true",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }

        self.assertEqual(_validate_edge(edge), set())

    def test_invalid_guard(self):
        edge = {
            "id": "e0",
            "name": "e_name",
            "sourceVertexId": "v1",
            "targetVertexId": "v0"
        }
        guards = [1, 2, 3, {}, []]

        for guard in guards:
            edge["guard"] = guard
            self.assertEqual(_validate_edge(edge), {"Edge 'e0' has an ivalid guard. The guard must be a string."})


class _TestValidateModel(unittest.TestCase):

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

        self.assertEqual(_validate_model(model), set())

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

        self.assertEqual(_validate_model(model), {"Each model must have a name."})

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

        self.assertEqual(_validate_model(model), {"Each model must have a name."})

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

        self.assertEqual(_validate_model(model), {"Name 'Model A' is not a valid identifier."})

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

        self.assertEqual(_validate_model(model), {"Name 'return' is a reserve keyword."})

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

        self.assertEqual(_validate_model(model), {'Each model must have a list of vertices.'})

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

        self.assertEqual(_validate_model(model), {'Each model must have a list of edges.'})

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

        self.assertEqual(_validate_model(model), {'Each vertex must have an id.'})

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

        self.assertEqual(_validate_model(model), {'Each edge must have an id.'})

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

        self.assertEqual(_validate_model(model), {'The generator must be a string.'})

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

        self.assertEqual(_validate_model(model), {"Starting element 'v1' was not found."})

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

        self.assertEqual(_validate_model(model), set())


class _TestValidateModels(unittest.TestCase):

    def test_no_models(self):
        issues = _validate_models(NO_MODELS)

        self.assertEqual(issues["global"], {'No models found.'})

    def test_duplicate_ids(self):
        issues = _validate_models(DUPLICATE_IDS_MODELS)

        self.assertEqual(issues["UnknownSourceFile::ModelA"], {"Id 'v0' is not unique."})


class TestValidateJsonModels(unittest.TestCase):

    def test_valid(self):
        validate_json_models(MOCK_MODELS)

    def test_no_models(self):
        with self.assertRaises(ValidationException):
            validate_json_models(NO_MODELS)

    def test_duplicate_ids(self):
        with self.assertRaises(ValidationException):
            validate_json_models(DUPLICATE_IDS_MODELS)

    def test_multiple_erros(self):
        with self.assertRaises(ValidationException):
            validate_json_models(MULTIPLE_ERRORS_MODELS)


@mock.patch("altwalker.model.validate_json_models")
@mock.patch("altwalker.model.get_models")
class TestValidateModels(unittest.TestCase):

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
class TestCheckModels(unittest.TestCase):

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

        with self.assertRaisesRegex(ValidationException, "Error message."):
            check_models(self.models, blocked=True)
