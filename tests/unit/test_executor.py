import os
import unittest
import unittest.mock as mock

from altwalker.exceptions import ExecutorException
from altwalker.executor import get_output, load, create_executor, \
    PythonExecutor, HttpExecutor, DotnetExecutorService


class TestGetOutput(unittest.TestCase):

    def test_output(self):
        func = mock.MagicMock()
        func.side_effect = lambda: print("message")

        result = get_output(func)

        func.assert_called_once_with()
        self.assertEqual(result["output"], "message\n")

    def test_not_error(self):
        func = mock.MagicMock()

        result = get_output(func)

        func.assert_called_once_with()
        self.assertFalse("error" in result)

    def test_error(self):
        func = mock.MagicMock()
        func.side_effect = Exception("Error message.")

        result = get_output(func)

        func.assert_called_once_with()
        self.assertTrue("error" in result)

    def test_args(self):
        func = mock.MagicMock()
        get_output(func, "argument_1", "argument_2")

        func.assert_called_once_with("argument_1", "argument_2")

    def test_kargs(self):
        func = mock.MagicMock()
        get_output(func, key="value")

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


class TestHttpExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = HttpExecutor(url="http://localhost:5000/")

    def test_base(self):
        self.assertEqual(self.executor.base, "http://localhost:5000/altwalker")

    def test_url(self):
        self.assertEqual(self.executor.url, "http://localhost:5000/")

    def test_valid_response(self):
        response = mock.MagicMock()
        response.status_code = 200

        self.executor._validate_response(response)

    def test_invalid_response(self):
        response = mock.MagicMock()
        response.status_code = 404
        response.json.return_value = {}

        error_message_reqex = "The executor from http://.*/ responded with status code: .*"

        with self.assertRaisesRegex(ExecutorException, error_message_reqex):
            self.executor._validate_response(response)

    def test_response_error(self):
        response = mock.MagicMock()
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
        response = mock.MagicMock()
        response.json.return_value = {
            "payload": {
                "data": "data"
            }
        }

        self.assertEqual(self.executor._get_payload(response), {"data": "data"})

    def test_get_payload_with_no_payload(self):
        response = mock.MagicMock()
        response.json.side_effect = ValueError("No json body.")

        self.assertEqual(self.executor._get_payload(response), {})

    def test_load(self):
        self.executor._post = mock.MagicMock(return_value={})

        path = "tests/common/example"
        self.executor.load(path)
        self.executor._post.assert_called_once_with("load", data={"path": os.path.abspath(path)})

    def test_restet(self):
        self.executor._put = mock.MagicMock(return_value={})

        self.executor.reset()
        self.executor._put.assert_called_once_with("reset")

    def test_has_model(self):
        self.executor._get = mock.MagicMock(return_value={"hasModel": True})

        self.executor.has_model("model")
        self.executor._get.assert_called_once_with("hasModel", params=({"name": "model"}))

    def test_has_model_invalid_response(self):
        self.executor._get = mock.MagicMock(return_value={})

        with self.assertRaises(ExecutorException):
            self.executor.has_model("model")

    def test_has_step(self):
        self.executor._get = mock.MagicMock(return_value={"hasStep": True})

        self.executor.has_step("model", "step")
        self.executor._get.assert_called_once_with("hasStep", params=({"modelName": "model", "name": "step"}))

    def test_has_setup_run_step(self):
        self.executor._get = mock.MagicMock({"hasStep": True})

        self.executor.has_step(None, "step")
        self.executor._get.assert_called_once_with("hasStep", params=({"modelName": None, "name": "step"}))

    def test_has_step_invalid_response(self):
        self.executor._get = mock.MagicMock(return_value={})

        with self.assertRaises(ExecutorException):
            self.executor.has_step("model", "step")

    def test_execute_step(self):
        self.executor._post = mock.MagicMock({"output": ""})

        self.executor.execute_step("model", "step", {})
        self.executor._post.assert_called_once_with("executeStep", params=(
            {"modelName": "model", "name": "step"}), data={})

    def test_execute_setup_step(self):
        self.executor._post = mock.MagicMock({"output": ""})

        self.executor.execute_step(None, "step", {})
        self.executor._post.assert_called_once_with(
            "executeStep", params=({"modelName": None, "name": "step"}), data={})

    def test_execute_invalid_response(self):
        self.executor._post = mock.MagicMock(return_value={})

        with self.assertRaises(ExecutorException):
            self.executor.execute_step("model", "step", {})


class TestPythonExecutor(unittest.TestCase):

    def setUp(self):
        self.module = mock.MagicMock()
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
        self.executor._get_instance = mock.MagicMock()
        self.executor._get_instance.return_value = True

        # Should call _get_instance and add the class_name in _instances
        self.executor._setup_class("class_name")
        self.executor._get_instance.assert_called_once_with("class_name")
        self.assertDictEqual(self.executor._instances, {"class_name": True})

        # Should not call _get_instance again
        self.executor._setup_class("class_name")
        self.assertEqual(self.executor._get_instance.call_count, 1)

    def test_setup_class_twice(self):
        self.executor._get_instance = mock.MagicMock()
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
        self.executor._has_function = mock.MagicMock()
        self.executor._has_method = mock.MagicMock()

        # Should call _has_function
        self.executor.has_step(None, "method")
        self.executor._has_function.assert_called_once_with("method")

        # Should call _has_method
        self.executor.has_step("class_name", "method")
        self.executor._has_method.assert_called_once_with("class_name", "method")

    @mock.patch("altwalker.executor.inspect.getfullargspec")
    def test_execute_step_function(self, getfullargspec):
        spec_mock = mock.MagicMock()
        spec_mock.args = []
        getfullargspec.return_value = spec_mock

        # Should execute a function
        self.executor.execute_step(None, "function")
        self.module.function.assert_called_once_with()

    @mock.patch("altwalker.executor.inspect.getfullargspec")
    def test_execute_step_function_with_data(self, getfullargspec):
        spec_mock = mock.MagicMock()
        spec_mock.args = ["data"]
        getfullargspec.return_value = spec_mock

        # should call the function with the right args
        self.executor.execute_step(None, "function", data={"key": "value"})
        self.module.function.assert_called_once_with({"key": "value"})

    @mock.patch("altwalker.executor.inspect.getfullargspec")
    def test_execute_step_function_invalid_args(self, getfullargspec):
        spec_mock = mock.MagicMock()
        spec_mock.args = ["data", "extra"]
        getfullargspec.return_value = spec_mock

        # should call the function with the right args
        error_message = "The .* function must take 0 or 1 parameters but it expects .* parameters."

        with self.assertRaisesRegex(ExecutorException, error_message):
            self.executor.execute_step(None, "function", data={"key": "value"})

        self.module.function.assert_not_called()

    @mock.patch("altwalker.executor.inspect.getfullargspec")
    def test_execute_step_method(self, getfullargspec):
        self.executor._setup_class = mock.MagicMock()
        self.executor._instances["ClassName"] = mock.MagicMock()

        spec_mock = mock.MagicMock()
        spec_mock.args = ["self"]
        getfullargspec.return_value = spec_mock

        # Should executre a method
        self.executor.execute_step("ClassName", "method")
        self.executor._setup_class.assert_called_once_with("ClassName")
        self.executor._instances["ClassName"].method.assert_called_once_with()

    @mock.patch("altwalker.executor.inspect.getfullargspec")
    def test_execute_step_method_with_data(self, getfullargspec):
        self.executor._setup_class = mock.MagicMock()
        self.executor._instances["class_name"] = mock.MagicMock()

        spec_mock = mock.MagicMock()
        spec_mock.args = ["self", "data"]
        getfullargspec.return_value = spec_mock

        # should call the method with the right args
        self.executor.execute_step("class_name", "method", data={"key": "value"})
        self.executor._instances["class_name"].method.assert_called_once_with({"key": "value"})

    @mock.patch("altwalker.executor.inspect.getfullargspec")
    def test_execute_step_method_with_invalid_args(self, getfullargspec):
        self.executor._setup_class = mock.MagicMock()
        self.executor._instances["ClassName"] = mock.MagicMock()

        spec_mock = mock.MagicMock()
        spec_mock.args = ["self", "data", "extra"]
        getfullargspec.return_value = spec_mock

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

    def test_create_command(self):
        command = DotnetExecutorService._create_command("path", "http://localhost:4200")
        self.assertEqual(command, ['dotnet', 'path', '--server.urls=http://localhost:4200'])

        command = DotnetExecutorService._create_command("tests/", "http://localhost:5000")
        self.assertEqual(command, ['dotnet', 'run', '-p', 'tests/', '--server.urls=http://localhost:5000'])


class TestCreateExecutor(unittest.TestCase):

    @mock.patch("altwalker.executor.create_python_executor")
    def test_create_executor_python(self, create_python_executor):
        create_executor("path/to/pacakge", "python", None)
        create_python_executor.assert_called_once_with("path/to/pacakge")

    @mock.patch("altwalker.executor.create_dotnet_executor", return_value="service")
    def test_create_dotnet(self, dotnet_executor):
        executor = create_executor("path/to/pacakge", "dotnet", "http://1.2.3.4:5678")
        self.assertEqual(executor, "service")

        dotnet_executor.assert_called_once_with("path/to/pacakge", "http://1.2.3.4:5678")

    @mock.patch("altwalker.executor.create_dotnet_executor", return_value="service")
    def test_create_csharp(self, dotnet_executor):
        executor = create_executor("path/to/pacakge", "c#", "http://1.2.3.4:5678")
        self.assertEqual(executor, "service")

        dotnet_executor.assert_called_once_with("path/to/pacakge", "http://1.2.3.4:5678")

    @mock.patch("altwalker.executor.create_python_executor")
    def test_create_python(self, python_executor):
        path = "path/to/package"
        create_executor(path, "python", None)

        python_executor.assert_called_once_with(path)

    @mock.patch("altwalker.executor.create_http_executor")
    def test_create_http(self, http_executor):
        path = "path/to/code"
        url = "http://localhost:4200"

        create_executor(path, "http", url)

        http_executor.assert_called_once_with(path, url)

    def test_create_invalid_language(self):
        with self.assertRaisesRegex(ValueError, "myexecutortype is not a supported executor type."):
            create_executor("path/to/package", "myexecutortype", "http://1.1.1.1:1111")
