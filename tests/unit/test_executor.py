import unittest.mock as mock

import pytest

from altwalker.exceptions import ExecutorException
from altwalker.executor import (DotnetExecutorService, HttpExecutor,
                                PythonExecutor, get_step_result)


class TestGetStepResult:

    def test_output(self):
        func = mock.Mock()
        func.side_effect = lambda: print("message")

        result = get_step_result(func)

        func.assert_called_once_with()
        result["output"] == "message\n"

    def test_result(self):
        func = mock.Mock()
        func.side_effect = lambda: {"prop": "val"}

        result = get_step_result(func)

        assert result["result"] == {"prop": "val"}

    def test_not_error(self):
        func = mock.Mock()

        result = get_step_result(func)

        func.assert_called_once_with()
        assert "error" not in result

    def test_error(self):
        func = mock.Mock()
        func.side_effect = Exception("Error message.")

        result = get_step_result(func)

        func.assert_called_once_with()
        assert "error" in result

    def test_args(self):
        func = mock.Mock()
        get_step_result(func, "argument_1", "argument_2")

        func.assert_called_once_with("argument_1", "argument_2")

    def test_kwargs(self):
        func = mock.Mock()
        get_step_result(func, key="value")

        func.assert_called_once_with(key="value")


class TestHttpExecutor:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.executor = HttpExecutor(url="http://localhost:5000/")

    def test_base(self):
        assert self.executor.base == "http://localhost:5000/altwalker"

    def test_url(self):
        assert self.executor.url == "http://localhost:5000/"

    def test_valid_response(self):
        response = mock.Mock()
        response.status_code = 200

        self.executor._validate_response(response)

    def test_invalid_response(self):
        response = mock.Mock()
        response.status_code = 404
        response.json.return_value = {}

        error_message_regex = "The executor from http://.*/ responded with status code: .*"

        with pytest.raises(ExecutorException, match=error_message_regex):
            self.executor._validate_response(response)

    def test_response_error(self):
        response = mock.Mock()
        response.status_code = 404
        response.json.return_value = {
            "error": {
                "message": "Error message.",
                "trace": "Trace."
            }
        }

        error_message_regex = ".*\nMessage: Error message.\nTrace: Trace."

        with pytest.raises(ExecutorException, match=error_message_regex):
            self.executor._validate_response(response)

    def test_get_payload(self):
        response = mock.Mock()
        response.json.return_value = {
            "payload": {
                "data": "data"
            }
        }

        assert self.executor._get_payload(response) == {"data": "data"}

    def test_get_payload_with_no_payload(self):
        response = mock.Mock()
        response.json.side_effect = ValueError("No json body.")

        assert self.executor._get_payload(response) == {}

    def test_load(self):
        self.executor._post = mock.Mock(return_value={})

        path = "tests/common/example"
        self.executor.load(path)
        self.executor._post.assert_called_once_with("load", json={"path": path})

    def test_reset(self):
        self.executor._put = mock.Mock(return_value={})

        self.executor.reset()
        self.executor._put.assert_called_once_with("reset")

    def test_has_model(self):
        self.executor._get = mock.Mock(return_value={"hasModel": True})

        self.executor.has_model("model")
        self.executor._get.assert_called_once_with("hasModel", params=({"name": "model"}))

    def test_has_model_invalid_response(self):
        self.executor._get = mock.Mock(return_value={})

        with pytest.raises(ExecutorException):
            self.executor.has_model("model")

    def test_has_step(self):
        self.executor._get = mock.Mock(return_value={"hasStep": True})

        self.executor.has_step("model", "step")
        self.executor._get.assert_called_once_with("hasStep", params=({"modelName": "model", "name": "step"}))

    def test_has_setup_run_step(self):
        self.executor._get = mock.Mock({"hasStep": True})

        self.executor.has_step(None, "step")
        self.executor._get.assert_called_once_with("hasStep", params=({"modelName": None, "name": "step"}))

    def test_has_step_invalid_response(self):
        self.executor._get = mock.Mock(return_value={})

        with pytest.raises(ExecutorException):
            self.executor.has_step("model", "step")

    def test_execute_step(self):
        self.executor._post = mock.Mock({"output": ""})

        self.executor.execute_step("model", "step", {"key": "value"})
        self.executor._post.assert_called_once_with("executeStep", params=(
            {"modelName": "model", "name": "step"}), json={"data": {"key": "value"}})

    def test_execute_setup_step(self):
        self.executor._post = mock.Mock({"output": ""})

        self.executor.execute_step(None, "step", {})
        self.executor._post.assert_called_once_with(
            "executeStep", params=({"modelName": None, "name": "step"}), json={"data": {}})

    def test_execute_invalid_response(self):
        self.executor._post = mock.Mock(return_value={})

        with pytest.raises(ExecutorException):
            self.executor.execute_step("model", "step", {})


class TestPythonExecutor:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.module = mock.Mock()
        self.executor = PythonExecutor(self.module)

    def test_load(self):
        path = "tests/common/python"

        self.executor._module = None
        self.executor.load(path)

        assert self.executor._module is not None
        assert hasattr(self.executor._module, "Simple")

    def test_get_instance(self):
        self.module.object.return_value = True
        result = self.executor._get_instance("object")

        # Should call the object callable and return the output
        self.module.object.assert_called_once_with()
        assert result

    def test_setup_class(self):
        self.executor._get_instance = mock.Mock()
        self.executor._get_instance.return_value = True

        # Should call _get_instance and add the class_name in _instances
        self.executor._setup_class("class_name")
        self.executor._get_instance.assert_called_once_with("class_name")
        assert self.executor._instances == {"class_name": True}

        # Should not call _get_instance again
        self.executor._setup_class("class_name")
        assert self.executor._get_instance.call_count == 1

    def test_setup_class_twice(self):
        self.executor._get_instance = mock.Mock()
        self.executor._get_instance.return_value = True

        self.executor._instances["class_name"] = True

        # Should not call _get_instance if class_name is in _instances
        self.executor._setup_class("class_name")
        self.executor._get_instance.assert_not_called()

    def test_has_function(self):
        # Should return true for a function
        assert self.executor._has_function("name")

        # Should return false for a non callable
        self.module.name = "Not a function"
        assert not self.executor._has_function("name")

    def test_has_model(self):
        # Should return true for a class
        self.module.name = object
        assert self.executor.has_model("name")

        # Should return false otherwise
        self.module.name = "Not a class"
        assert not self.executor.has_model("name")

    def test_has_method(self):
        # Should return true for a class with a method
        self.module.class_name = object
        assert self.executor._has_method("class_name", "__str__")

        # Should return false for a class without the method
        self.module.class_name = object
        assert not self.executor._has_method("class_name", "method")

        # Should return false for a non class
        self.module.class_name = "Not a class"
        assert not self.executor._has_method("class_name", "method")

    def test_has_step(self):
        self.executor._has_function = mock.Mock()
        self.executor._has_method = mock.Mock()

        # Should call _has_function
        self.executor.has_step(None, "method")
        self.executor._has_function.assert_called_once_with("method")

        # Should call _has_method
        self.executor.has_step("class_name", "method")
        self.executor._has_method.assert_called_once_with("class_name", "method")

    def test_execute_step(self):
        path = "tests/common/python"

        self.executor._module = None
        self.executor.load(path)

        data = {"key": "value"}

        response = self.executor.execute_step("Simple", "vertex_a", data=data)
        output = response["output"]

        assert "Simple.vertex_a" in output, f"Actual output: {output}"
        assert str(data) in output, f"Actual output: {output}"

        response = self.executor.execute_step("Simple", "vertex_b", data=data)
        output = response["output"]

        assert "Simple.vertex_b" in output, f"Actual output: {output}"
        assert str(data) in output, f"Actual output: {output}"

        response = self.executor.execute_step("Simple", "edge_a", data=data)
        output = response["output"]

        assert "Simple.edge_a" in output, f"Actual output: {output}"
        assert "Decorated method" in output, f"Actual output: {output}"

        response = self.executor.execute_step("Simple", "edge_b", data=data)
        output = response["output"]

        assert "Simple.edge_b" in output, f"Actual output: {output}"
        assert "Decorated method" in output, f"Actual output: {output}"
        assert str(data) in output, f"Actual output: {output}"

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_function(self, signature):
        signature.return_value.parameters = []

        # Should execute a function
        self.executor.execute_step(None, "function")
        self.module.function.assert_called_once_with()

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_function_with_data(self, signature):
        signature.return_value.parameters = ["data"]

        # should call the function with the right args
        self.executor.execute_step(None, "function", data={"key": "value"})
        self.module.function.assert_called_once_with({"key": "value"})

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_function_invalid_args(self, signature):
        signature.return_value.parameters = ["data", "extra"]

        # should call the function with the right args
        error_message = "The .* function must take 0 or 1 parameters but it expects .* parameters."

        with pytest.raises(ExecutorException, match=error_message):
            self.executor.execute_step(None, "function", data={"key": "value"})

        self.module.function.assert_not_called()

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_method(self, signature):
        self.executor._setup_class = mock.Mock()
        self.executor._instances["ClassName"] = mock.Mock()

        signature.return_value.parameters = []

        # Should execute a method
        self.executor.execute_step("ClassName", "method")
        self.executor._setup_class.assert_called_once_with("ClassName")
        self.executor._instances["ClassName"].method.assert_called_once_with()

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_method_with_data(self, signature):
        self.executor._setup_class = mock.Mock()
        self.executor._instances["class_name"] = mock.Mock()

        signature.return_value.parameters = ["data"]

        # should call the method with the right args
        self.executor.execute_step("class_name", "method", data={"key": "value"})
        self.executor._instances["class_name"].method.assert_called_once_with({"key": "value"})

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_method_with_invalid_args(self, signature):
        self.executor._setup_class = mock.Mock()
        self.executor._instances["ClassName"] = mock.Mock()

        signature.return_value.parameters = ["data", "extra"]

        error_message = "The .* method must take 0 or 1 parameters but it expects .* parameters."

        with pytest.raises(ExecutorException, match=error_message):
            self.executor.execute_step("ClassName", "method")

        self.executor._setup_class.assert_called_once_with("ClassName")
        self.executor._instances["ClassName"].method.assert_not_called()

    def test_reset(self):
        self.executor._instances = {"ClassName": None}
        self.executor.reset()

        assert self.executor._instances == {}


class TestDotnetExecutorService:

    @mock.patch("platform.system", return_value="Linux")
    def test_create_command(self, _):
        command = DotnetExecutorService._create_command("path", "http://localhost:4200")
        assert command == ['dotnet', 'path', '--server.urls=http://localhost:4200']

        command = DotnetExecutorService._create_command("tests/", "http://localhost:5000")
        assert command == ['dotnet', 'run', '-p', 'tests/', '--server.urls=http://localhost:5000']
