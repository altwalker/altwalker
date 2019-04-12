import os
import shutil
import unittest
import unittest.mock as mock

from altwalker.init import _copy_models, _create_default_model, init_repo
from altwalker.init import generate_tests,  generate_tests_python, generate_tests_csharp, _proj_name_to_namespace


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


class TestGenerateTests(unittest.TestCase):

    def setUp(self):
        self.output_dir = "output_dir"

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_generate_python(self):
        generate_tests_python(self.output_dir, {"ModelName": ["vertex_A", "vertex_B", "edge_A"]})

        expected_code = "\nclass ModelName:\n\n" \
            "\tdef vertex_A(self):\n" \
            "\t\tpass\n\n" \
            "\tdef vertex_B(self):\n" \
            "\t\tpass\n\n" \
            "\tdef edge_A(self):\n" \
            "\t\tpass\n\n"

        with open(self.output_dir + "/tests/test.py", "r") as f:
            code = f.read()
            self.assertEqual(code, expected_code)

    def test_generate_csharp(self):
        generate_tests_csharp(self.output_dir, {"ModelName": ["vertex_A", "vertex_B", "edge_A"]})

        self.assertTrue(os.path.exists("output_dir/output_dir.Tests"))

        files = [
            "output_dir.Tests/output_dir.Tests.csproj",
            "output_dir.Tests/Program.cs",
            "output_dir.Tests/ModelName.cs"
        ]

        for file in files:
            with open("tests/common/dotnet/" + file, "r") as expected:
                expected = expected.read()
                with open(self.output_dir + "/" + file, "r") as generated:
                    generated = generated.read()
                    self.assertEqual(expected, generated, file)

    @mock.patch("altwalker.init.get_methods")
    def test_generate_unsupported_language(self, get_methods):
        get_methods.return_value = []
        with self.assertRaisesRegex(Exception, "unsupportedlanguage is not supported."):
            generate_tests("output_dir", ["model.json"], "unsupportedlanguage")

    @mock.patch("altwalker.init.get_methods")
    @mock.patch("altwalker.init.generate_tests_python")
    def test_cleanup(self, generate_tests_python_mock, get_methods):
        get_methods.return_value = []
        message = "Error message"
        generate_tests_python_mock.side_effect = Exception(message)

        os.makedirs("output_dir")
        with self.assertRaisesRegex(Exception, message):
            generate_tests("output_dir", ["model.json"], "python")

        self.assertEqual(False, os.path.isdir(self.output_dir))

    def test_proj_name_to_namespace(self):
        self.assertEqual("a.b_c.d.e_f", _proj_name_to_namespace("a-b_c d--e_f"))


@mock.patch("altwalker.init._git_init")
@mock.patch("altwalker.init.generate_tests")
class TestInit(unittest.TestCase):

    def setUp(self):
        self.output_dir = "output_dir"

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_cleanup(self, generate_tests_mock, git_init_mock):
        message = "Mocked exception message"
        generate_tests_mock.side_effect = Exception(message)

        with self.assertRaisesRegex(Exception, message):
            init_repo("output_dir", None)

        self.assertEqual(False, os.path.isdir(self.output_dir))

    def test_dir_already_exisits(self, generate_tests_mock, git_init_mock):
        os.makedirs(self.output_dir)

        with self.assertRaisesRegex(FileExistsError, "The {} directory already exists.".format(self.output_dir)):
            init_repo(self.output_dir, None)

    def test_create_dir(self, generate_tests_mock, git_init_mock):
        init_repo(self.output_dir, None)
        self.assertEqual(True, os.path.isdir(self.output_dir))

    @mock.patch("altwalker.init._copy_models")
    @mock.patch("altwalker.init.check_models")
    def test_check_models(self, check_mock, copy_mock, generate_tests_mock, git_init_mock):
        init_repo(self.output_dir, "python", ["first.json", "second.json"])
        check_mock.assert_called_once_with([("first.json", "random(never)"), ("second.json", "random(never)")])

    @mock.patch("altwalker.init._copy_models")
    @mock.patch("altwalker.init.check_models")
    def test_copy_models(self, check_mock, copy_mock, generate_tests_mock, git_init_mock):
        init_repo(self.output_dir, "python", ["first.json", "second.json"])
        copy_mock.assert_called_once_with(self.output_dir + "/models", ["first.json", "second.json"])

    def test_git_init(self, generate_tests_mock, git_init_mock):
        init_repo(self.output_dir, None)
        git_init_mock.assert_called_once_with(self.output_dir)

    def test_no_git_init(self, generate_tests_mock, git_init_mock):
        init_repo(self.output_dir, "python", None, True)
        git_init_mock.assert_not_called()
