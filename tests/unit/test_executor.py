from altwalker.exceptions import ExecutorException
import unittest
import unittest.mock as mock

from altwalker.executor import create_executor, _create_python_executor
from altwalker.executor import get_output, load, PythonExecutor, HttpExecutorClient


class TestGetOutput(unittest.TestCase):

    def test_get_output(self):
        func = mock.MagicMock()
        func.side_effect = lambda: print("message")

        message = get_output(func)

        # Should call the function and return the std output
        func.assert_called_once_with()
        self.assertEqual(message, "message\n")

    def test_get_output_args(self):
        func = mock.MagicMock()
        get_output(func, "argument_1", "argument_2")

        # Should call the function with args
        func.assert_called_once_with("argument_1", "argument_2")

    def test_get_output_kargs(self):
        func = mock.MagicMock()
        get_output(func, key="value")

        # Should call the function with kargs
        func.assert_called_once_with(key="value")


class TestLoad(unittest.TestCase):

    def test_load(self):
        # Should import a module from a package
        module = load("tests/common/", "example", "simple")
        self.assertTrue(hasattr(module, "Simple"))


class TestPythonExecutor(unittest.TestCase):

    def setUp(self):
        self.module = mock.MagicMock()
        self.executor = PythonExecutor(self.module)

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

    def test_execute_step(self):
        self.executor._setup_class = mock.MagicMock()
        self.executor._instances["class_name"] = mock.MagicMock()

        # Should execute a function
        self.executor.execute_step(None, "function")
        self.module.function.assert_called_once_with()

        # Should executre a method
        self.executor.execute_step("class_name", "method")
        self.executor._setup_class.assert_called_once_with("class_name")
        self.executor._instances["class_name"].method.assert_called_once_with()

    def test_execute_step_function_args(self):
        with mock.patch("altwalker.executor.inspect.getfullargspec") as inspect:
            spec_mock = mock.MagicMock()
            spec_mock.args = ["arg1", "arg2"]
            inspect.return_value = spec_mock

            # should call the function with the right args
            self.executor.execute_step(None, "function", "arg1", "arg2", "arg3")
            self.module.function.assert_called_once_with("arg1", "arg2")

    def test_execute_step_method_args(self):
        with mock.patch("altwalker.executor.inspect.getfullargspec") as inspect:
            self.executor._setup_class = mock.MagicMock()
            self.executor._instances["class_name"] = mock.MagicMock()

            spec_mock = mock.MagicMock()
            spec_mock.args = ["self", "arg1", "arg2"]
            inspect.return_value = spec_mock

            # should call the method with the right args
            self.executor.execute_step("class_name", "method", "arg1", "arg2", "arg3")
            self.executor._instances["class_name"].method.assert_called_once_with("arg1", "arg2")


class TestHttpExecutorClient(unittest.TestCase):
    def setUp(self):
        self.executor = HttpExecutorClient("1.2.3.4", 1234)

    def test_base(self):
        self.assertEqual(self.executor.base, "http://1.2.3.4:1234/altwalker/")

    def test_has_model(self):
        self.executor._get = mock.MagicMock()
        self.executor.has_model("model")
        self.executor._get.assert_called_once_with("hasModel", params=(("name", "model")))

    def test_has_step(self):
        self.executor._get = mock.MagicMock()
        self.executor.has_step("model", "step")
        self.executor._get.assert_called_once_with("hasStep", params=(("modelName", "model"), ("name", "step")))

    def test_has_setup_run_step(self):
        self.executor._get = mock.MagicMock()
        self.executor.has_step(None, "step")
        self.executor._get.assert_called_once_with("hasStep", params=(("modelName", None), ("name", "step")))

    def test_execute_step(self):
        self.executor._post = mock.MagicMock()
        self.executor.execute_step("model", "step")
        self.executor._post.assert_called_once_with("executeStep", params=(("modelName", "model"), ("name", "step")))

    def test_execute_setup_step(self):
        self.executor._post = mock.MagicMock()
        self.executor.execute_step(None, "step")
        self.executor._post.assert_called_once_with("executeStep", params=(("modelName", None), ("name", "step")))

    def test_restart(self):
        self.executor._get = mock.MagicMock()
        self.executor.reset()
        self.executor._get.assert_called_once_with("reset")

    def test_get_body(self):
        body = mock.MagicMock()

        # if no error should return body
        body.json.return_value = {"data": "data"}

        self.assertEqual(self.executor._get_body(body), {"data": "data"})

        # Should raise exception if the error key is present
        body.json.return_value = {"error": "error message."}

        with self.assertRaises(ExecutorException) as error:
            self.executor._get_body(body)

        self.assertEqual(str(error.exception), "error message.")


class TestCreateExecutor(unittest.TestCase):
    @mock.patch("altwalker.executor._create_python_executor")
    def test_create_executor_python(self, create_python_executor):
        create_executor("path/to/pacakge", "python")
        create_python_executor.assert_called_once_with("path/to/pacakge")

    @mock.patch("altwalker.executor._create_python_executor")
    @mock.patch("altwalker.executor.DotnetExecutorService", return_value="service")
    @mock.patch("altwalker.executor.HttpExecutor", return_value="executor")
    def test_create_executor_dotnet(self, http_executor, dotnet_executor_service, create_python_executor):
        executor = create_executor("path/to/pacakge", "dotnet", port=1111, host="1.1.1.1")
        self.assertEqual(executor, "executor")
        dotnet_executor_service.assert_called_once_with("path/to/pacakge", "1.1.1.1", 1111)
        http_executor.assert_called_once_with("service", "1.1.1.1", 1111)
        create_python_executor.assert_not_called()

    @mock.patch("altwalker.executor.load", return_value="module")
    @mock.patch("altwalker.executor.Executor")
    def test_create_python_executor(self, executor, load):
        _create_python_executor("path/to/package")
        load.assert_called_once_with("path/to", "package", "test")
        executor.assert_called_once_with("module")

    def test_create_executor_service_not_implemented(self):
        with self.assertRaises(ValueError) as error:
            create_executor("path/to/pacakge", "mylanguage", "1.1.1.1", 1111)

        self.assertEqual("mylanguage is not supported.", str(error.exception))
