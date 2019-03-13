import unittest
import unittest.mock as mock

from altwalker.executor import get_output, load, Executor


class TestGetOutput(unittest.TestCase):

    def test_get_output(self):
        func = mock.MagicMock()
        func.side_effect = lambda: print("message")

        result = get_output(func)

        # Should call the function and return the std output
        func.assert_called_once_with()
        self.assertEqual(result["output"], "message\n")
        self.assertFalse("error" in result)

    def test_get_output_error(self):
        func = mock.MagicMock()
        func.side_effect = Exception("Error message.")

        result = get_output(func)

        # Should call the function and return the std output
        func.assert_called_once_with()
        self.assertEqual(result["output"], "")
        self.assertTrue("error" in result)

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


class TestExecutor(unittest.TestCase):

    def setUp(self):
        self.module = mock.MagicMock()
        self.executor = Executor(self.module)

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
        self.assertTrue(self.executor.has_function("name"))

        # Should return false for a non callable
        self.module.name = "Not a function"
        self.assertFalse(self.executor.has_function("name"))

    def test_has_class(self):
        # Should return true for a class
        self.module.name = object
        self.assertTrue(self.executor.has_class("name"))

        # Should return false otherwise
        self.module.name = "Not a class"
        self.assertFalse(self.executor.has_class("name"))

    def test_has_method(self):
        # Should return true for a class with a method
        self.module.class_name = object
        self.assertTrue(self.executor.has_method("class_name", "__str__"))

        # Should return false for a class without the method
        self.module.class_name = object
        self.assertFalse(self.executor.has_method("class_name", "method"))

        # Should return false for a non class
        self.module.class_name = "Not a class"
        self.assertFalse(self.executor.has_method("class_name", "method"))

    def test_has_step(self):
        self.executor.has_function = mock.MagicMock()
        self.executor.has_method = mock.MagicMock()

        # Should call has_function
        self.executor.has_step(None, "method")
        self.executor.has_function.assert_called_once_with("method")

        # Should call has_method
        self.executor.has_step("class_name", "method")
        self.executor.has_method.assert_called_once_with("class_name", "method")

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
