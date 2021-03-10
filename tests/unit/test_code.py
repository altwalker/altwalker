import unittest
import unittest.mock as mock

from altwalker.code import ValidationException, _is_element_blocked, _graphml_methods, _json_methods, \
    validate_code, get_methods, get_missing_methods, verify_code


MOCK_MODELS = {
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
                    "name": "edge_blocked",
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
                },
                {
                    "name": "edge_name"
                }

            ]
        }
    ]
}


class TestIsElementBlocked(unittest.TestCase):

    def test_element_blocked_and_blocked_enabled(self):
        element = {"properties": {"blocked": True}}
        self.assertTrue(_is_element_blocked(element, blocked=True))

    def test_element_blocked_and_blocked_disabled(self):
        element = {"properties": {"blocked": True}}
        self.assertFalse(_is_element_blocked(element, blocked=False))

    def test_element_not_blocked_and_blocked_enabled(self):
        element = {"properties": {"blocked": False}}
        self.assertFalse(_is_element_blocked(element, blocked=True))

    def test_element_not_blocked_and_blocked_disabled(self):
        element = {"properties": {"blocked": False}}
        self.assertFalse(_is_element_blocked(element, blocked=False))


@mock.patch("altwalker.code._read_json")
class TestJsonMethods(unittest.TestCase):

    def setUp(self):
        self.models = MOCK_MODELS

        self.expected_methods = {
            "ModelA": ["vertex_blocked", "vertex_not_blocked", "edge_blocked", "edge_not_blocked"],
            "ModelB": ["vertex_name", "edge_name"]
        }

        self.filtered_expected_methods = {
            "ModelA": ["vertex_not_blocked", "edge_not_blocked"],
            "ModelB": ["vertex_name", "edge_name"]
        }

    def test_models(self, read_mock):
        read_mock.return_value = self.models

        output = _json_methods("path/to/model")
        self.assertSequenceEqual({"ModelA", "ModelB"}, output.keys())

    def test_blocked_disable(self, read_mock):
        read_mock.return_value = self.models

        methods = _json_methods("path/to/model", blocked=False)
        self.assertEqual(methods, self.expected_methods)

    def test_blocked_enable(self, read_mock):
        read_mock.return_value = self.models

        methods = _json_methods("path/to/model", blocked=True)
        self.assertEqual(methods, self.filtered_expected_methods)


@mock.patch("altwalker.graphwalker.methods")
class TestGraphmlMethods(unittest.TestCase):

    def test_methods(self, methods_mock):
        _graphml_methods("ModelName.graphml")
        methods_mock.assert_called_once_with("ModelName.graphml", blocked=False)

    def test_blocked(self, methods_mock):
        _graphml_methods("ModelName.graphml", blocked=True)
        methods_mock.assert_called_once_with("ModelName.graphml", blocked=True)

    def test_name(self, methods_mock):
        result = _graphml_methods("ModelName.graphml")
        self.assertIn("ModelName", result)

    def test_result(self, methods_mock):
        expected_methods = {"ModelName": {"method_A", "method_B"}}
        methods_mock.return_value = expected_methods["ModelName"]
        methods = _graphml_methods("ModelName.graphml")

        self.assertEqual(methods, expected_methods)


@mock.patch("altwalker.code._json_methods")
@mock.patch("altwalker.code._graphml_methods")
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
        expected_methods = {
            "ModelA": {"method_A", "method_B"},
            "ModelB": {"method_C", "method_D"}
        }

        json_mock.return_value = {"ModelA": expected_methods["ModelA"]}
        graphml_mock.return_value = {"ModelB": expected_methods["ModelB"]}

        methods = get_methods(["model.json", "ModelB.graphml"])

        self.assertEqual(
            methods,
            expected_methods
        )


class TestGetMissingMethods(unittest.TestCase):

    def setUp(self):
        self.methods = {
            "Model_A": ["vertex_A", "edge_A"]
        }

        self.executor = mock.Mock()

    def test_missing_methods(self):
        self.executor.has_step.side_effect = [True, False]

        self.assertEqual(get_missing_methods(self.executor, self.methods), {"Model_A": {"edge_A"}})

    def test_no_missing_methods(self):
        self.executor.has_step.return_value = True

        self.assertEqual(get_missing_methods(self.executor, self.methods), {})


class TestValidateCode(unittest.TestCase):

    def setUp(self):
        self.methods = {
            "Model_A": ["vertex_A", "edge_A"]
        }

        self.executor = mock.Mock()

    def test_valid_code(self):
        self.executor.has_model.return_value = True
        self.executor.has_step.return_value = True

        validate_code(self.executor, self.methods)

    def test_invalid_code(self):
        expected = (
            "Expected to find class 'Model_A'.",
            "Expected to find method 'vertex_A' in class 'Model_A'.",
            "Expected to find method 'edge_A' in class 'Model_A'.",
        )

        self.executor.has_model.return_value = False
        self.executor.has_step.return_value = False

        with self.assertRaises(ValidationException) as cm:
            validate_code(self.executor, self.methods)

        error_message = str(cm.exception)
        for message in expected:
            self.assertIn(message, error_message)


@mock.patch("altwalker.code.validate_code")
@mock.patch("altwalker.code.get_methods")
@mock.patch("altwalker.code.validate_models")
@mock.patch("altwalker.code.create_executor")
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
