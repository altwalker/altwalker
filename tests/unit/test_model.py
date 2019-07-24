import os
import unittest
import unittest.mock as mock

from altwalker.model import PYTHON_KEYWORDS, CSHARP_KEYWORDS, ValidationException, _read_json, _is_keyword, \
    _is_element_blocked, _graphml_methods, _json_methods, validate_code, validate_model, validate_models, \
    validate_element, get_models, get_methods, check_models, verify_code


class TestIsKeyword(unittest.TestCase):

    def test_keyword(self):
        for keyword in PYTHON_KEYWORDS | CSHARP_KEYWORDS:
            self.assertTrue(_is_keyword(keyword))

    def test_not_kewords(self):
        for not_keyword in ["not_a_keyword", "definitely_not_a_keyword"]:
            self.assertFalse(_is_keyword(not_keyword))


class TestValidateElement(unittest.TestCase):

    def test_validation(self):
        # Should return true for valid names
        self.assertTrue(validate_element("method_A"))
        self.assertTrue(validate_element("Method_A"))
        self.assertTrue(validate_element("Method_1"))

    def test_validation_for_invalid_method(self):
        # Should return false for strings with numbers as first character
        self.assertFalse(validate_element("1_method"))

    def test_validation_for_spaces(self):
        # Should return false for strings with extra spaces
        self.assertFalse(validate_element("method "))

    def test_validation_for_invalid_characters(self):
        # Should return false for unaccepted characters

        characters = "!@#$%^&*+-/=<>~`,./;:'\"][}{)(|"

        for character in characters:
            self.assertFalse(validate_element("method_" + character))

        for character in characters:
            self.assertFalse(validate_element(character + "_method"))


class TestReadJson(unittest.TestCase):

    def test_error(self):
        file_name = "error.json"

        with open(file_name, "w") as fp:
            fp.write("{,}")

        with self.assertRaisesRegex(ValidationException, "Invalid json file: {}: .*".format(file_name)):
            _read_json(file_name)

        os.remove(file_name)


class TestValidateModel(unittest.TestCase):

    def test_valid_model(self):
        models = {
            "models": [
                {
                    "name": "Model_A",
                    "vertices": [
                        {
                            "name": "vertex_A"
                        }
                    ],
                    "edges": [
                        {
                            "name": "edge_A"
                        }
                    ]
                }
            ]
        }

        validate_model(models)

    def test_invalid_model(self):
        models = {
            "models": [
                {
                    "name": "Model A",
                    "vertices": [
                        {
                            "name": "1vertex"
                        }
                    ],
                    "edges": [
                        {
                            "name": "1edge"
                        }
                    ]
                }
            ]
        }

        with self.assertRaises(ValidationException) as cm:
            validate_model(models)

        message = str(cm.exception)

        # Should return a correct message
        self.assertIn("Invalid model name: Model A.\n", message)
        self.assertIn("Invalid vertex name: 1vertex.\n", message)
        self.assertIn("Invalid edge name: 1edge.\n", message)


@mock.patch("altwalker.model.validate_model")
@mock.patch("altwalker.model._read_json")
class TestValidateModels(unittest.TestCase):

    def test_read_json(self, read_mock, validate_mock):
        read_mock.return_value = {}

        validate_models(["first.json", "second.json"])

        read_mock.assert_any_call("first.json")
        read_mock.assert_any_call("second.json")

    def test_validate_model(self, read_mock, validate_mock):
        read_mock.side_effect = ["first.json", "second.json"]

        validate_models(["first.json", "second.json"])

        validate_mock.assert_any_call("first.json")
        validate_mock.assert_any_call("second.json")


class TestValidateCode(unittest.TestCase):

    def setUp(self):
        self.methods = {
            "Model_A": ["vertex_A", "edge_A"]
        }

        self.executor = mock.MagicMock()

    def test_valid_code(self):
        self.executor.has_model.return_value = True
        self.executor.has_step.return_value = True

        validate_code(self.executor, self.methods)

    def test_invalid_code(self):
        self.executor.has_model.return_value = False
        self.executor.has_step.return_value = False

        with self.assertRaises(ValidationException) as cm:
            validate_code(self.executor, self.methods)

        message = str(cm.exception)

        expected = "Expected to find class Model_A.\n" + \
                   "Expected to find vertex_A method in class Model_A.\n" + \
                   "Expected to find edge_A method in class Model_A.\n"

        self.assertEqual(expected, message)


@mock.patch("altwalker.model.validate_code")
@mock.patch("altwalker.model.get_methods")
@mock.patch("altwalker.model.validate_models")
@mock.patch("altwalker.model.create_executor")
class TestVerifyCode(unittest.TestCase):
    def test_verify_code(self, create_executor_mock, validate_models_mock, methods_mock, validate_code_mock):
        executor = mock.MagicMock()
        create_executor_mock.return_value = executor
        verify_code("/path/to/package", "executorname", ["models.json"], None)
        create_executor_mock.assert_called_once_with("/path/to/package", "executorname", None)
        validate_models_mock.assert_called_once_with(["models.json"])
        methods_mock.assert_called_once_with(["models.json"])
        executor.kill.assert_called_once_with()

    def test_validate_code(self, create_executor_mock, validate_models_mock, methods_mock, validate_code_mock):
        executor = mock.MagicMock()
        create_executor_mock.return_value = executor

        methods = {
            "ModelA": ["vertex_A"]
        }
        methods_mock.return_value = methods

        verify_code("/path/to/package", "executorname", ["models.json"], None)
        validate_code_mock.assert_called_once_with(executor, methods)
        executor.kill.assert_called_once_with()


class TestIsElementBlocked(unittest.TestCase):

    def test_element_blocked_and_blocked_enabled(self):
        element = {"properties": {"blocked": False}}
        self.assertTrue(_is_element_blocked(element, blocked=True))

    def test_element_blocked_and_blocked_disabled(self):
        element = {"properties": {"blocked": True}}
        self.assertTrue(_is_element_blocked(element, blocked=False))

    def test_element_not_blocked_and_blocked_enabled(self):
        element = {"properties": {"blocked": False}}
        self.assertTrue(_is_element_blocked(element, blocked=False))

    def test_element_not_blocked_and_blocked_disabled(self):
        element = {"properties": {"blocked": True}}
        self.assertFalse(_is_element_blocked(element, blocked=True))


@mock.patch("altwalker.model._read_json")
class TestJsonMethods(unittest.TestCase):

    def setUp(self):
        self.models = {
            "models": [
                {
                    "name": "ModelA",
                    "vertices": [
                        {
                            "name": "vertex_blocked",
                            "properties": {
                                "blocked": True
                            }
                        },
                        {
                            "name": "vertex_not_blocked",
                        }
                    ],
                    "edges": [
                        {
                            "name": "edge_bloked",
                            "properties": {
                                "blocked": True
                            }
                        },
                        {
                            "name": "edge_not_blocked",
                        }
                    ]
                },
                {
                    "name": "ModelB",
                    "vertices": [
                        {
                            "name": "vertex_name",
                            "properties": {
                                "blocked": False
                            }
                        }
                    ],
                    "edges": [
                        {
                            "name": "edge_name",
                            "properties": {
                                "blocked": False
                            }
                        }
                    ]
                }
            ]
        }

    def test_models(self, read_mock):
        read_mock.return_value = self.models

        output = _json_methods("model_path")
        self.assertSequenceEqual({"ModelA", "ModelB"}, output.keys())

    def test_blocked_disable(self, read_mock):
        read_mock.return_value = self.models

        output = _json_methods("model_path")
        self.assertListEqual(
            output["ModelA"],
            sorted(set(["vertex_blocked", "vertex_not_blocked", "edge_bloked", "edge_not_blocked"])))
        self.assertListEqual(output["ModelB"], sorted(set(["vertex_name", "edge_name"])))

    def test_blocked_enable(self, read_mock):
        read_mock.return_value = self.models

        output = _json_methods("model_path", blocked=True)
        self.assertListEqual(output["ModelA"], sorted(set(["vertex_not_blocked", "edge_not_blocked"])))
        self.assertListEqual(output["ModelB"], sorted(set(["vertex_name", "edge_name"])))


@mock.patch("altwalker.graphwalker.methods")
class TestGraphmlMethods(unittest.TestCase):

    def test_methods(self, methods_mock):
        _graphml_methods("model.graphml")
        methods_mock.assert_called_once_with("model.graphml", blocked=False)

    def test_blocked(self, methods_mock):
        _graphml_methods("model.graphml", blocked=True)
        methods_mock.assert_called_once_with("model.graphml", blocked=True)

    def test_name(self, methods_mock):
        result = _graphml_methods("model.graphml")

        self.assertIn("model", result)

    def test_result(self, methods_mock):
        methods_mock.return_value = ["method_A", "method_B"]

        result = _graphml_methods("model.graphml")

        self.assertListEqual(result["model"], ["method_A", "method_B"])


@mock.patch("altwalker.model._json_methods")
@mock.patch("altwalker.model._graphml_methods")
class TestGetMetohds(unittest.TestCase):

    def test_json(self, graphml_mock, json_mock):
        get_methods(["model.json"])

        json_mock.assert_called_once_with("model.json", blocked=False)
        graphml_mock.assert_not_called()

    def test_graphml(self, graphml_mock, json_mock):
        get_methods(["model.graphml"])

        graphml_mock.assert_called_once_with("model.graphml", blocked=False)
        json_mock.assert_not_called()

    def test_invalid_format(self, graphml_mock, json_mock):
        get_methods(["model.txt"])

        json_mock.assert_not_called()
        graphml_mock.assert_not_called()

    def test_both(self, graphml_mock, json_mock):
        get_methods(["model.json", "model.graphml"])

        json_mock.assert_called_once_with("model.json", blocked=False)
        graphml_mock.assert_called_once_with("model.graphml", blocked=False)

    def test_blocked(self, graphml_mock, json_mock):
        get_methods(["model.json", "model.graphml"], blocked=True)

        json_mock.assert_called_once_with("model.json", blocked=True)
        graphml_mock.assert_called_once_with("model.graphml", blocked=True)

    def test_result(self, graphml_mock, json_mock):
        json_mock.return_value = {"modelA": ["method_A", "method_B"]}
        graphml_mock.return_value = {"modelB": ["method_C", "method_D"]}

        result = get_methods(["model.json", "model.graphml"])

        self.assertSequenceEqual({"modelA", "modelB"}, result.keys())
        self.assertListEqual(result["modelA"], ["method_A", "method_B"])
        self.assertListEqual(result["modelB"], ["method_C", "method_D"])


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


class TestGetModels(unittest.TestCase):

    def test_get_models(self):
        result = get_models(["tests/common/models/simple.json", "tests/common/models/simple.json"])
        model = _read_json("tests/common/models/simple.json")

        self.assertEqual(len(result["models"]), 2)
        self.assertListEqual(result["models"], model["models"] + model["models"])
