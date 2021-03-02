import os
import shutil
import random
import warnings
import unittest
import unittest.mock as mock

from altwalker.exceptions import AltWalkerException
from altwalker.generate import _normalize_namespace, _copy_models, \
    _call_generate_function, _create_default_model, _git_init, generate_empty_tests, \
    generate_python_methods, generate_python_class, generate_python_code, generate_python_tests, \
    generate_dotnet_methods, generate_dotnet_class, generate_dotnet_code, generate_dotnet_tests, \
    generate_methods, generate_class, generate_code, generate_tests, init_project


PYTHON_METHOD_REGEX_TEMPLATE = r"def {}\(self\):\n\s*pass"
DOTNET_METHOD_REGEX_TEMPLATE = r"public void {}\(\)\n\s*{{\s*\n\s*}}\s*"


def scramble_case(word):
    result = ""

    for letter in word:
        result += random.choice([letter.upper(), letter.lower()])

    return result


class GenerateTestsTestCase(unittest.TestCase):

    def setUp(self):
        self.project_name = "test-project"
        self.methods = {
            "ModelName": ["vertex_A", "vertex_B", "edge_A"]
        }

    def tearDown(self):
        if os.path.exists(self.project_name):
            shutil.rmtree(self.project_name)


class _TestScrambleCase(unittest.TestCase):

    def test_scramble(self):
        for word in ["random", "worlds", "for", "tests"]:
            scrambled_word = scramble_case(word)
            self.assertEqual(word.lower(), scrambled_word.lower())


class _TestNormalizeNamespace(unittest.TestCase):

    def test_dash(self):
        self.assertEqual("A.B", _normalize_namespace("A-B"))

    def test_title_case(self):
        self.assertEqual("A.B.C", _normalize_namespace("a-b-c"))
        self.assertEqual("A.B.C", _normalize_namespace("A-B-C"))


class _TestCopyModels(unittest.TestCase):

    def setUp(self):
        self.output_dir = "output_dir"

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_with_no_model(self):
        _copy_models(self.output_dir, [])
        self.assertTrue(os.path.isdir(self.output_dir))

    def test_with_models(self):
        _copy_models(self.output_dir, ["tests/common/models/simple.json", "tests/common/models/complex.json"])

        self.assertTrue(os.path.isfile(self.output_dir + "/simple.json"))
        self.assertTrue(os.path.isfile(self.output_dir + "/complex.json"))


class _TestCreateDefaultModel(unittest.TestCase):

    def setUp(self):
        self.output_dir = "output_dir"

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_create_default(self):
        _create_default_model(self.output_dir)
        self.assertTrue(os.path.isfile(self.output_dir + "/default.json"))


class _TestGitInit(unittest.TestCase):

    @mock.patch("altwalker.generate.has_git")
    def test_warning(self, has_git):
        has_git.return_value = False

        with warnings.catch_warnings(record=True) as w:
            _git_init("path/to/project")

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))


class TestGenerateEmptyTests(GenerateTestsTestCase):

    def test_code(self):
        tests_directory = "tests"

        generate_empty_tests(self.project_name, package_name=tests_directory)

        tests_path = os.path.join(self.project_name, tests_directory)
        self.assertTrue(os.path.exists(tests_path))

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_get_methods(self, get_methods_mock):
        tests_directory = "tests"

        generate_tests(self.project_name, model_paths=mock.sentinel.models, language=None, package_name=tests_directory)

        get_methods_mock.assert_called_once_with(mock.sentinel.models)

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests(self, get_methods_mock):
        tests_directory = "tests"

        generate_tests(self.project_name, model_paths=mock.sentinel.models, language=None, package_name=tests_directory)

        tests_path = os.path.join(self.project_name, tests_directory)
        self.assertTrue(os.path.exists(tests_path))


class TestGeneratePythonMethods(unittest.TestCase):

    def setUp(self):
        self.methods = ["method_a", "method_b", "method_c"]

    def test_methods(self):
        methods_code = generate_python_methods(self.methods)

        for method in self.methods:
            expresion = PYTHON_METHOD_REGEX_TEMPLATE.format(method)
            self.assertRegex(methods_code, expresion)

    def test_generate_methods(self):
        self.assertEqual(
            generate_methods("python", self.methods),
            generate_python_methods(self.methods)
        )


class TestGeneratePythonClass(unittest.TestCase):

    def setUp(self):
        self.class_name = "ClassA"
        self.methods = ["method_a", "method_b", "method_c"]

    def test_class(self):
        class_code = generate_python_class(self.class_name, self.methods)

        self.assertIn("class {}:".format(self.class_name), class_code)

    def test_methods(self):
        class_code = generate_python_class(self.class_name, self.methods)

        for method in self.methods:
            expresion = PYTHON_METHOD_REGEX_TEMPLATE.format(method)
            self.assertRegex(class_code, expresion)

    def test_generate_class(self):
        self.assertEqual(
            generate_class("python", self.class_name, self.methods),
            generate_python_class(self.class_name, self.methods)
        )


class TestGeneratePythonCode(unittest.TestCase):

    def setUp(self):
        self.methods = {
            "ClassA": ["method_a", "method_b", "method_c"],
            "ClassB": ["method_d", "method_e", "method_f"],
        }

    def test_clases(self):
        code = generate_python_code(self.methods)

        for class_name, methods_list in self.methods.items():
            class_code = generate_python_class(class_name, methods_list)
            self.assertIn(class_code, code)

    def test_generate_code(self):
        self.assertEqual(
            generate_code("python", self.methods),
            generate_python_code(self.methods)
        )


class TestGeneratePythonTests(GenerateTestsTestCase):

    def test_code(self):
        generate_python_tests(self.project_name, self.methods)

        expected_code = (
            "\n"
            "class ModelName:\n\n"
            "    def vertex_A(self):\n"
            "        pass\n\n"
            "    def vertex_B(self):\n"
            "        pass\n\n"
            "    def edge_A(self):\n"
            "        pass\n\n"
        )

        with open(self.project_name + "/tests/test.py", "r") as fp:
            code = fp.read()
            self.assertEqual(code, expected_code)

    def test_init(self):
        generate_python_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists(self.project_name + "/tests/__init__.py"))

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_get_methods(self, get_methods_mock):
        get_methods_mock.return_value = self.methods

        generate_tests(self.project_name, mock.sentinel.models, language="python")

        get_methods_mock.assert_called_once_with(mock.sentinel.models)

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_code(self, get_methods_mock):
        get_methods_mock.return_value = self.methods

        generate_tests(self.project_name, mock.sentinel.models, language="python")

        expected_code = (
            "\n"
            "class ModelName:\n\n"
            "    def vertex_A(self):\n"
            "        pass\n\n"
            "    def vertex_B(self):\n"
            "        pass\n\n"
            "    def edge_A(self):\n"
            "        pass\n\n"
        )

        with open(self.project_name + "/tests/test.py", "r") as fp:
            code = fp.read()
            self.assertEqual(code, expected_code)

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_init(self, get_methods_mock):
        get_methods_mock.return_value = self.methods

        generate_tests(self.project_name, mock.sentinel.models, language="python")

        self.assertTrue(os.path.exists(self.project_name + "/tests/__init__.py"))


class TestGenerateDotnetMethods(unittest.TestCase):

    def setUp(self):
        self.methods = ["method_a", "method_b", "method_c"]

    def test_methods(self):
        methods_code = generate_dotnet_methods(self.methods)

        for method in self.methods:
            expresion = DOTNET_METHOD_REGEX_TEMPLATE.format(method)
            self.assertRegex(methods_code, expresion)

    def test_generate_methods(self):
        self.assertEqual(
            generate_methods("dotnet", self.methods),
            generate_dotnet_methods(self.methods)
        )

        self.assertEqual(
            generate_methods("c#", self.methods),
            generate_dotnet_methods(self.methods)
        )


class TestGenerateDotnetClass(unittest.TestCase):

    def setUp(self):
        self.class_name = "ClassA"
        self.methods = ["method_a", "method_b", "method_c"]

    def test_class(self):
        class_code = generate_dotnet_class(self.class_name, self.methods)

        self.assertIn("public class {}".format(self.class_name), class_code)

    def test_methods(self):
        class_code = generate_dotnet_class(self.class_name, self.methods)

        for method in self.methods:
            expresion = DOTNET_METHOD_REGEX_TEMPLATE.format(method)
            self.assertRegex(class_code, expresion)

    def test_generate_class(self):
        self.assertEqual(
            generate_class("dotnet", self.class_name, self.methods),
            generate_dotnet_class(self.class_name, self.methods)
        )

        self.assertEqual(
            generate_class("c#", self.class_name, self.methods),
            generate_dotnet_class(self.class_name, self.methods)
        )


class TestGenerateDotnetCode(unittest.TestCase):

    def setUp(self):
        self.methods = {
            "ClassA": ["method_a", "method_b", "method_c"],
            "ClassB": ["method_d", "method_e", "method_f"],
        }

    def test_clases(self):
        code = generate_dotnet_code(self.methods)

        for class_name, methods_list in self.methods.items():
            class_code = generate_dotnet_class(class_name, methods_list)
            self.assertIn(class_code, code)

    def test_program_class(self):
        code = generate_dotnet_code(self.methods)
        self.assertIn("public class Program", code)

    def test_main(self):
        code = generate_dotnet_code(self.methods)

        self.assertIn("public static void Main(string[] args)", code)

        for class_name in self.methods.keys():
            self.assertIn("service.RegisterModel<{}>();".format(class_name), code)

    def test_generate_code(self):
        self.assertEqual(
            generate_code("dotnet", self.methods),
            generate_dotnet_code(self.methods)
        )

        self.assertEqual(
            generate_code("c#", self.methods),
            generate_dotnet_code(self.methods)
        )


class TestGenerateDotnetTests(GenerateTestsTestCase):

    def test_csproj(self):
        generate_dotnet_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists("{}/tests/tests.csproj".format(self.project_name)))

    def test_program(self):
        generate_dotnet_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists("{}/tests/Program.cs".format(self.project_name)))

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_get_methods(self, get_methods_mock):
        get_methods_mock.return_value = self.methods

        generate_tests(self.project_name, mock.sentinel.models, language="dotnet")
        get_methods_mock.assert_called_once_with(mock.sentinel.models)

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_csproj(self, get_methods_mock):
        get_methods_mock.return_value = self.methods

        generate_tests(self.project_name, mock.sentinel.models, language="dotnet")
        self.assertTrue(os.path.exists("{}/tests/tests.csproj".format(self.project_name)))

    @mock.patch("altwalker.generate.get_methods")
    def test_generate_tests_program(self, get_methods_mock):
        get_methods_mock.return_value = self.methods

        generate_tests(self.project_name, mock.sentinel.models, language="dotnet")
        self.assertTrue(os.path.exists("{}/tests/Program.cs".format(self.project_name)))


class TestsCallGenerateFunction(unittest.TestCase):

    def setUp(self):
        self.call_args = None

        self.functions = {
            "python": mock.Mock(),
            "dotnet": mock.Mock(),
        }

    def test_call(self):
        for language in self.functions.keys():
            _call_generate_function(language, self.functions)

            self.functions[language].assert_called_once_with()

    def test_args_and_kwargs(self):
        for language in self.functions.keys():
            _call_generate_function(language, self.functions, language, x=language)

            self.functions[language].assert_called_once_with(language, x=language)

    def test_case_sensitivity(self):
        for language in self.functions.keys():
            scrambled_language = scramble_case(language)
            _call_generate_function(scrambled_language, self.functions)

            self.functions[language].assert_called_once_with()

    def test_invalid_language(self):
        expected_error_message = "Language 'not-found' is not supported. Supported languages are: *."
        with self.assertRaisesRegex(AltWalkerException, expected_error_message):
            _call_generate_function("not-found", self.functions)


@mock.patch("altwalker.generate.get_methods", return_value={})
class TestGenerateTests(GenerateTestsTestCase):

    def test_directory_already_exists(self, get_methods):
        test_package_path = "{}/{}".format(self.project_name, "tests")
        os.makedirs(test_package_path)

        with self.assertRaisesRegex(FileExistsError, "The .* directory already exists."):
            generate_tests(self.project_name, ["model.json"], language="python")

        self.assertTrue(os.path.exists(test_package_path))

    def test_unsupported_language(self, get_methods):
        with self.assertRaisesRegex(AltWalkerException, "Language 'unsupported-language' is not supported. *."):
            generate_tests(self.project_name, ["model.json"], language="unsupported-language")

    @mock.patch("altwalker.generate._call_generate_function")
    def test_error(self, call_generate_function_mock, get_methods):
        error_message = "Unknown error"

        def side_effect(*args, **kwargs):
            os.makedirs("{}/tests/".format(self.project_name))
            raise AltWalkerException(error_message)

        call_generate_function_mock.side_effect = side_effect

        with self.assertRaisesRegex(AltWalkerException, error_message):
            generate_tests(self.project_name, ["model.json"], language="python")

        self.assertFalse(os.path.exists("{}/tests/".format(self.project_name)))


@mock.patch("altwalker.generate._git_init")
@mock.patch("altwalker.generate.generate_tests")
class TestInitProject(unittest.TestCase):

    def setUp(self):
        self.output_dir = "output_dir"

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_cleanup(self, generate_tests_mock, git_init_mock):
        message = "Mocked exception message"
        generate_tests_mock.side_effect = Exception(message)

        with self.assertRaisesRegex(Exception, message):
            init_project("output_dir", None)

        self.assertEqual(False, os.path.isdir(self.output_dir))

    def test_directory_already_exisits(self, generate_tests_mock, git_init_mock):
        os.makedirs(self.output_dir)

        with self.assertRaisesRegex(FileExistsError, "The .* directory already exists."):
            init_project(self.output_dir)

    def test_create_dir(self, generate_tests_mock, git_init_mock):
        init_project(self.output_dir)
        self.assertEqual(True, os.path.isdir(self.output_dir))

    @mock.patch("altwalker.generate._copy_models")
    def test_copy_models(self, copy_mock, generate_tests_mock, git_init_mock):
        init_project(self.output_dir, model_paths=["first.json", "second.json"], language="python")
        copy_mock.assert_called_once_with(self.output_dir + os.path.sep + "models", ["first.json", "second.json"])

    def test_git_init(self, generate_tests_mock, git_init_mock):
        init_project(self.output_dir)
        git_init_mock.assert_called_once_with(self.output_dir)

    def test_no_git_init(self, generate_tests_mock, git_init_mock):
        init_project(self.output_dir, git=False)
        git_init_mock.assert_not_called()
