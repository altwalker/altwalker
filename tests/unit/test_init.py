import os
import shutil
import warnings
import unittest
import unittest.mock as mock

from altwalker.init import _normalize_namespace, _copy_models, _create_default_model, _git_init, \
    generate_empty_tests, generate_python_tests, generate_csharp_tests, generate_tests, \
    init_project


class TestNormalizeNamespace(unittest.TestCase):

    def test_dash(self):
        self.assertEqual("A.B", _normalize_namespace("A-B"))

    def test_title_case(self):
        self.assertEqual("A.B.C", _normalize_namespace("a-b-c"))


class TestCopyModels(unittest.TestCase):

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


class TestCreateDefaultModel(unittest.TestCase):

    def setUp(self):
        self.output_dir = "output_dir"

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_create_default(self):
        _create_default_model(self.output_dir)
        self.assertTrue(os.path.isfile(self.output_dir + "/default.json"))


class TestGitInit(unittest.TestCase):

    @mock.patch("altwalker.init.has_git")
    def test_warning(self, has_git):
        has_git.return_value = False

        with warnings.catch_warnings(record=True) as w:
            _git_init("path/to/project")

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, UserWarning))


class GenerateTestsSetup(unittest.TestCase):

    def setUp(self):
        self.project_name = "test-project"
        self.methods = {
            "ModelName": ["vertex_A", "vertex_B", "edge_A"]
        }

    def tearDown(self):
        if os.path.exists(self.project_name):
            shutil.rmtree(self.project_name)


class TestGenerateEmptyTests(GenerateTestsSetup):

    def test_generate(self):
        tests_directory = "tests"

        generate_empty_tests(self.project_name, package_name=tests_directory)

        tests_path = os.path.join(self.project_name, tests_directory)
        self.assertTrue(os.path.exists(tests_path))


class TestGeneratePythonTests(GenerateTestsSetup):

    def test_code(self):
        generate_python_tests(self.project_name, self.methods)

        expected_code = "\nclass ModelName:\n\n" \
            "\tdef vertex_A(self):\n" \
            "\t\tpass\n\n" \
            "\tdef vertex_B(self):\n" \
            "\t\tpass\n\n" \
            "\tdef edge_A(self):\n" \
            "\t\tpass\n\n"

        with open(self.project_name + "/tests/test.py", "r") as f:
            code = f.read()
            self.assertEqual(code, expected_code)

    def test_init(self):
        generate_python_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists(self.project_name + "/tests/__init__.py"))


class TestGenerateCSharpTests(GenerateTestsSetup):

    def test_generate(self):
        generate_csharp_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists("{}/tests".format(self.project_name)))

    def test_csproj(self):
        generate_csharp_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists("{}/tests/tests.csproj".format(self.project_name)))

    def test_model_files(self):
        generate_csharp_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists("{}/tests/ModelName.cs".format(self.project_name)))

    def test_program(self):
        generate_csharp_tests(self.project_name, self.methods)
        self.assertTrue(os.path.exists("{}/tests/Program.cs".format(self.project_name)))


@mock.patch("altwalker.init.get_methods", return_value=[])
class TestGenerateTests(GenerateTestsSetup):

    def test_dir_already_exists(self, get_methods):
        test_package_path = "{}/{}".format(self.project_name, "tests")
        os.makedirs(test_package_path)

        with self.assertRaisesRegex(FileExistsError, "The .* directory already exists."):
            generate_tests(self.project_name, ["model.json"], language="python")

        self.assertTrue(os.path.exists(test_package_path))

    def test_unsupported_language(self, get_methods):
        with self.assertRaisesRegex(ValueError, "'unsupported-language' is not a supported language."):
            generate_tests(self.project_name, ["model.json"], language="unsupported-language")

    @mock.patch("altwalker.init.generate_empty_tests")
    def test_cleanup(self, generate_empty, get_methods):
        message = "Error message"
        generate_empty.side_effect = Exception(message)

        os.makedirs(self.project_name)

        with self.assertRaisesRegex(Exception, message):
            generate_tests(self.project_name, ["model.json"], language=None)

        self.assertFalse(os.path.isdir(os.path.join(self.project_name, "tests")))

    @mock.patch("altwalker.init.generate_empty_tests")
    def test_error(self, generate_empty, get_methods):
        message = "Error message"
        generate_empty.side_effect = Exception(message)

        with self.assertRaisesRegex(Exception, message):
            generate_tests(self.project_name, ["model.json"], language=None)

        self.assertFalse(os.path.isdir(self.project_name))

    @mock.patch("altwalker.init.generate_empty_tests")
    def test_no_language(self, generate_empty, get_methods):
        generate_tests(self.project_name, ["model.json"], language=None)
        generate_empty.assert_called_once_with(self.project_name, [], package_name="tests")

    @mock.patch("altwalker.init.generate_python_tests")
    def test_python(self, generate_python, get_methods):
        generate_tests(self.project_name, ["model.json"], language="python")
        generate_python.assert_called_once_with(self.project_name, [], package_name="tests")

    @mock.patch("altwalker.init.generate_csharp_tests")
    def test_csharp(self, generate_csharp, get_methods):
        generate_tests(self.project_name, ["model.json"], language="c#")
        generate_csharp.assert_called_once_with(self.project_name, [], package_name="tests")

    @mock.patch("altwalker.init.generate_csharp_tests")
    def test_dotnet(self, generate_csharp, get_methods):
        generate_tests(self.project_name, ["model.json"], language="dotnet")
        generate_csharp.assert_called_once_with(self.project_name, [], package_name="tests")


@mock.patch("altwalker.init._git_init")
@mock.patch("altwalker.init.generate_tests")
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

    def test_dir_already_exisits(self, generate_tests_mock, git_init_mock):
        os.makedirs(self.output_dir)

        with self.assertRaisesRegex(FileExistsError, "The {} directory already exists.".format(self.output_dir)):
            init_project(self.output_dir)

    def test_create_dir(self, generate_tests_mock, git_init_mock):
        init_project(self.output_dir)
        self.assertEqual(True, os.path.isdir(self.output_dir))

    @mock.patch("altwalker.init._copy_models")
    @mock.patch("altwalker.init.check_models")
    def test_check_models(self, check_mock, copy_mock, generate_tests_mock, git_init_mock):
        init_project(self.output_dir, model_paths=["first.json", "second.json"], language="python")
        check_mock.assert_called_once_with([("first.json", "random(never)"), ("second.json", "random(never)")])

    @mock.patch("altwalker.init._copy_models")
    @mock.patch("altwalker.init.check_models")
    def test_copy_models(self, check_mock, copy_mock, generate_tests_mock, git_init_mock):
        init_project(self.output_dir, model_paths=["first.json", "second.json"], language="python")
        copy_mock.assert_called_once_with(self.output_dir + "/models", ["first.json", "second.json"])

    def test_git_init(self, generate_tests_mock, git_init_mock):
        init_project(self.output_dir)
        git_init_mock.assert_called_once_with(self.output_dir)

    def test_no_git_init(self, generate_tests_mock, git_init_mock):
        init_project(self.output_dir, git=False)
        git_init_mock.assert_not_called()
