import os
import sys
import unittest
import unittest.mock as mock

from altwalker.exceptions import ExecutorException, AltWalkerException
from altwalker.executor import _pop_previously_loaded_modules, _is_parent_path, \
    get_step_result, load, create_executor, create_python_executor, \
    PythonExecutor, HttpExecutor, DotnetExecutorService


class TestGetStepResult(unittest.TestCase):

    def test_output(self):
        func = mock.Mock()
        func.side_effect = lambda: print("message")

        result = get_step_result(func)

        func.assert_called_once_with()
        self.assertEqual(result["output"], "message\n")

    def test_result(self):
        func = mock.Mock()
        func.side_effect = lambda: {"prop": "val"}

        result = get_step_result(func)

        self.assertEqual(result["result"], {"prop": "val"})

    def test_not_error(self):
        func = mock.Mock()

        result = get_step_result(func)

        func.assert_called_once_with()
        self.assertFalse("error" in result)

    def test_error(self):
        func = mock.Mock()
        func.side_effect = Exception("Error message.")

        result = get_step_result(func)

        func.assert_called_once_with()
        self.assertTrue("error" in result)

    def test_args(self):
        func = mock.Mock()
        get_step_result(func, "argument_1", "argument_2")

        func.assert_called_once_with("argument_1", "argument_2")

    def test_kwargs(self):
        func = mock.Mock()
        get_step_result(func, key="value")

        func.assert_called_once_with(key="value")


class TestLoad(unittest.TestCase):

    def test_load(self):
        module = load("tests/common/", "python", "simple")
        self.assertTrue(hasattr(module, "Simple"))

    def test_load_submodule(self):
        module = load("tests/common/", "python", "complex")
        self.assertTrue(hasattr(module, "ComplexA"))
        self.assertTrue(hasattr(module, "ComplexB"))
        self.assertTrue(hasattr(module, "Base"))

    def test_pop_previously_loaded_modules(self):
        load("tests/common/", "python", "simple")
        self.assertTrue("python.simple" in sys.modules)
        _pop_previously_loaded_modules("tests/common/", "python")
        self.assertFalse("python.simple" in sys.modules)

    def test_is_parent_path(self):
        self.assertTrue(_is_parent_path("/a/b/c", "/a/b/c/d"))
        self.assertTrue(_is_parent_path("./tests", "./tests/unit/test_cli.py"))

        self.assertFalse(_is_parent_path("/a/b/test", "/a/b/test.py"))
        self.assertFalse(_is_parent_path("./tests/integration", "./tests/unit"))


class TestHttpExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = HttpExecutor(url="http://localhost:5000/")

    def test_base(self):
        self.assertEqual(self.executor.base, "http://localhost:5000/altwalker")

    def test_url(self):
        self.assertEqual(self.executor.url, "http://localhost:5000/")

    def test_valid_response(self):
        response = mock.Mock()
        response.status_code = 200

        self.executor._validate_response(response)

    def test_invalid_response(self):
        response = mock.Mock()
        response.status_code = 404
        response.json.return_value = {}

        error_message_reqex = "The executor from http://.*/ responded with status code: .*"

        with self.assertRaisesRegex(ExecutorException, error_message_reqex):
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

        with self.assertRaisesRegex(ExecutorException, ".*\nMessage: Error message.\nTrace: Trace."):
            self.executor._validate_response(response)

    def test_get_payload(self):
        response = mock.Mock()
        response.json.return_value = {
            "payload": {
                "data": "data"
            }
        }

        self.assertEqual(self.executor._get_payload(response), {"data": "data"})

    def test_get_payload_with_no_payload(self):
        response = mock.Mock()
        response.json.side_effect = ValueError("No json body.")

        self.assertEqual(self.executor._get_payload(response), {})

    def test_load(self):
        self.executor._post = mock.Mock(return_value={})

        path = "tests/common/example"
        self.executor.load(path)
        self.executor._post.assert_called_once_with("load", json={"path": path})

    def test_restet(self):
        self.executor._put = mock.Mock(return_value={})

        self.executor.reset()
        self.executor._put.assert_called_once_with("reset")

    def test_has_model(self):
        self.executor._get = mock.Mock(return_value={"hasModel": True})

        self.executor.has_model("model")
        self.executor._get.assert_called_once_with("hasModel", params=({"name": "model"}))

    def test_has_model_invalid_response(self):
        self.executor._get = mock.Mock(return_value={})

        with self.assertRaises(ExecutorException):
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

        with self.assertRaises(ExecutorException):
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

        with self.assertRaises(ExecutorException):
            self.executor.execute_step("model", "step", {})


class TestPythonExecutor(unittest.TestCase):

    def setUp(self):
        self.module = mock.Mock()
        self.executor = PythonExecutor(self.module)

    def test_load(self):
        path = "tests/common/python"

        self.executor._module = None
        self.executor.load(path)

        self.assertIsNotNone(self.executor._module)
        self.assertTrue(hasattr(self.executor._module, "Simple"))

    def test_get_instance(self):
        self.module.object.return_value = True
        result = self.executor._get_instance("object")

        # Should call the object callable and return the output
        self.module.object.assert_called_once_with()
        self.assertTrue(result)

    def test_setup_class(self):
        self.executor._get_instance = mock.Mock()
        self.executor._get_instance.return_value = True

        # Should call _get_instance and add the class_name in _instances
        self.executor._setup_class("class_name")
        self.executor._get_instance.assert_called_once_with("class_name")
        self.assertDictEqual(self.executor._instances, {"class_name": True})

        # Should not call _get_instance again
        self.executor._setup_class("class_name")
        self.assertEqual(self.executor._get_instance.call_count, 1)

    def test_setup_class_twice(self):
        self.executor._get_instance = mock.Mock()
        self.executor._get_instance.return_value = True

        self.executor._instances["class_name"] = True

        # Should not call _get_instance if class_name is in _instances
        self.executor._setup_class("class_name")
        self.executor._get_instance.assert_not_called()

    def test_has_function(self):
        # Should return true for a function
        self.assertTrue(self.executor._has_function("name"))

        # Should return false for a non callable
        self.module.name = "Not a function"
        self.assertFalse(self.executor._has_function("name"))

    def test_has_model(self):
        # Should return true for a class
        self.module.name = object
        self.assertTrue(self.executor.has_model("name"))

        # Should return false otherwise
        self.module.name = "Not a class"
        self.assertFalse(self.executor.has_model("name"))

    def test_has_method(self):
        # Should return true for a class with a method
        self.module.class_name = object
        self.assertTrue(self.executor._has_method("class_name", "__str__"))

        # Should return false for a class without the method
        self.module.class_name = object
        self.assertFalse(self.executor._has_method("class_name", "method"))

        # Should return false for a non class
        self.module.class_name = "Not a class"
        self.assertFalse(self.executor._has_method("class_name", "method"))

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

        self.assertTrue("Simple.vertex_a" in output, "Actual output: {}".format(output))
        self.assertTrue(str(data) in output, "Actual output: {}".format(output))

        response = self.executor.execute_step("Simple", "vertex_b", data=data)
        output = response["output"]

        self.assertTrue("Simple.vertex_b" in output, "Actual output: {}".format(output))
        self.assertTrue(str(data) in output, "Actual output: {}".format(output))

        response = self.executor.execute_step("Simple", "edge_a", data=data)
        output = response["output"]

        self.assertTrue("Simple.edge_a" in output, "Actual output: {}".format(output))
        self.assertTrue("Decorated method" in output, "Actual output: {}".format(output))

        response = self.executor.execute_step("Simple", "edge_b", data=data)
        output = response["output"]

        self.assertTrue("Simple.edge_b" in output, "Actual output: {}".format(output))
        self.assertTrue("Decorated method" in output, "Actual output: {}".format(output))
        self.assertTrue(str(data) in output, "Actual output: {}".format(output))

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

        with self.assertRaisesRegex(ExecutorException, error_message):
            self.executor.execute_step(None, "function", data={"key": "value"})

        self.module.function.assert_not_called()

    @mock.patch("altwalker.executor.signature")
    def test_execute_step_method(self, signature):
        self.executor._setup_class = mock.Mock()
        self.executor._instances["ClassName"] = mock.Mock()

        signature.return_value.parameters = []

        # Should executre a method
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

        with self.assertRaisesRegex(ExecutorException, error_message):
            self.executor.execute_step("ClassName", "method")

        self.executor._setup_class.assert_called_once_with("ClassName")
        self.executor._instances["ClassName"].method.assert_not_called()

    def test_reset(self):
        self.executor._instances = {"ClassName": None}
        self.executor.reset()

        self.assertDictEqual(self.executor._instances, {})


class TestDotnetExecutorService(unittest.TestCase):

    @mock.patch("platform.system", return_value="Linux")
    def test_create_command(self, platform):
        command = DotnetExecutorService._create_command("path", "http://localhost:4200")
        self.assertEqual(command, ['dotnet', 'path', '--server.urls=http://localhost:4200'])

        command = DotnetExecutorService._create_command("tests/", "http://localhost:5000")
        self.assertEqual(command, ['dotnet', 'run', '-p', 'tests/', '--server.urls=http://localhost:5000'])


class TestCreatePythonExecutor(unittest.TestCase):

    @mock.patch("altwalker.executor.load")
    def test_load(self, load_mock):
        create_python_executor(os.sep.join(["base", "path", "tests"]))
        load_mock.assert_called_once_with(os.sep.join(["base", "path"]), "tests", "test")


class TestCreateExecutor(unittest.TestCase):

    @mock.patch("altwalker.executor._call_create_executor_function", return_value=mock.sentinel.executor)
    def test_create_dotnet(self, dotnet_executor):
        executor = executor = create_executor("path/to/pacakge", "dotnet", url="http://1.2.3.4:5678")

        dotnet_executor.assert_called_once_with("dotnet", "path/to/pacakge", url="http://1.2.3.4:5678")
        self.assertEqual(executor, mock.sentinel.executor)

    @mock.patch("altwalker.executor._call_create_executor_function", return_value=mock.sentinel.executor)
    def test_create_csharp(self, dotnet_executor):
        executor = create_executor("path/to/pacakge", "c#", url="http://1.2.3.4:5678")

        dotnet_executor.assert_called_once_with("c#", "path/to/pacakge", url="http://1.2.3.4:5678")
        self.assertEqual(executor, mock.sentinel.executor)

    @mock.patch("altwalker.executor._call_create_executor_function", return_value=mock.sentinel.executor)
    def test_create_python(self, _call_function_mock):
        executor = create_executor("path/to/package", "python")

        _call_function_mock.assert_called_once_with("python", "path/to/package", url="http://localhost:5000/")
        self.assertTrue(executor, mock.sentinel.executor)

    @mock.patch("altwalker.executor._call_create_executor_function", return_value=mock.sentinel.executor)
    def test_create_http(self, _call_function_mock):
        executor = create_executor("path/to/code", "http", url="http://localhost:4200")

        _call_function_mock.assert_called_once_with("http", "path/to/code", url="http://localhost:4200")
        self.assertEqual(executor, mock.sentinel.executor)

    def test_create_invalid_language(self):
        error_message_regex = r"Executor type 'my_executor_type' is not supported. Supported executor types are: *."
        with self.assertRaisesRegex(AltWalkerException, error_message_regex):
            create_executor("path/to/package", "my_executor_type", "http://1.1.1.1:1111")
