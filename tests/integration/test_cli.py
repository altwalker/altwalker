import unittest
import filecmp
from pathlib import Path

from git import Repo
from click.testing import CliRunner

from tests.common.utils import run_isolation
from altwalker.cli import init, check, verify, online, offline, walk


with open("tests/common/models/simple.json") as f:
    SIMPLE_MODEL = f.read()


with open("tests/common/python/simple.py") as f:
    SIMPLE_TESTS = f.read()


with open("tests/common/models/invalid.json") as f:
    INVALID_MODEL = f.read()


OFFLINE_OUTPUT = """\
[
    {
        "id": "v0",
        "modelName": "Simple",
        "name": "vertex_a"
    },
    {
        "id": "e0",
        "modelName": "Simple",
        "name": "edge_a"
    },
    {
        "id": "v1",
        "modelName": "Simple",
        "name": "vertex_b"
    }
]
"""


class TestInit(unittest.TestCase):

    def setUp(self):
        self.packagename = "example"

        self.runner = CliRunner()
        self.files = [
            ("simple.json", SIMPLE_MODEL)
        ]

    def _assert_models_files(self, repo_path, models=None):
        models = models if models else []

        for model in models:
            self.assertTrue(Path("{}/models/{}".format(repo_path, model)).exists())

    def _assert_empty_file_structure(self, repo_path):
        self.assertTrue(Path("{}/tests/".format(repo_path)).exists())

    def _assert_python_file_structure(self, repo_path):
        self.assertTrue(Path("{}/tests/__init__.py".format(repo_path)).exists())
        self.assertTrue(Path("{}/tests/test.py".format(repo_path)).exists())

    def _assert_dotnet_file_structure(self, repo_path):
        self.assertTrue(Path("{}/tests/tests.csproj".format(repo_path)).exists())
        self.assertTrue(Path("{}/tests/Program.cs".format(repo_path)).exists())

    def _assert_git_repo(self, repo_path):
        repo = Repo(repo_path)
        commits = list(repo.iter_commits('master'))

        self.assertEqual(len(commits), 1, "Tests repo should have one commit")
        self.assertEqual(commits[0].summary, "Initial commit", "Commit summary should be 'Initial commit'")

    def test_git(self):
        with run_isolation(self.runner, self.files):
            packagename = "example"
            result = self.runner.invoke(init, [packagename, "--git"])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self._assert_git_repo(packagename)

    def test_no_git(self):
        with run_isolation(self.runner, self.files):
            packagename = "example"
            result = self.runner.invoke(init, [packagename, "--no-git"])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            with self.assertRaises(Exception):
                self._assert_git_repo(packagename)

    def test_python(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, [self.packagename, "-l", "python"])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self._assert_python_file_structure(self.packagename)

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

            with open("{}/tests/test.py".format(self.packagename), "r") as fp:
                self.assertEqual(fp.read(), expected_code)

    def test_dotnet(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, [self.packagename, "-l", "dotnet"])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self._assert_dotnet_file_structure(self.packagename)

            expected_code = (
                "using Altom.AltWalker;\n"
                "\n"
                "namespace Example.Tests\n"
                "{\n\n"
                "    public class ModelName\n"
                "    {\n\n"
                "        public void vertex_A()\n"
                "        {\n"
                "        }\n\n"
                "        public void vertex_B()\n"
                "        {\n"
                "        }\n\n"
                "        public void edge_A()\n"
                "        {\n"
                "        }\n\n"
                "    }\n\n"
                "    public class Program\n"
                "    {\n\n"
                "        public static void Main(string[] args)\n"
                "        {\n"
                "            ExecutorService service = new ExecutorService();\n"
                "            service.RegisterModel<ModelName>();\n"
                "            service.Run(args);\n"
                "        }\n"
                "    }\n\n"
                "}\n"
            )

            with open("{}/tests/Program.cs".format(self.packagename), "r") as fp:
                self.assertEqual(fp.read(), expected_code)

    def test_no_language(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, [self.packagename])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self._assert_empty_file_structure(self.packagename)

    def test_model(self):
        with run_isolation(self.runner, self.files):
            packagename = "example"
            result = self.runner.invoke(init, ["-m", "simple.json", packagename])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self._assert_models_files(packagename, ["simple.json"])
            self.assertTrue(filecmp.cmp("{}/models/simple.json".format(packagename), "simple.json"))


class TestCheck(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("simple.json", SIMPLE_MODEL),
            ("invalid.json", INVALID_MODEL)
        ]

    def test_check(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "simple.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_invalid_model(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "invalid.json", "random(vertex_coverage(100))"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)


class TestVerify(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_verify(self):
        files = [
            ("models/simple.json", SIMPLE_MODEL),
            ("tests/__init__.py", ""),
            ("tests/test.py", SIMPLE_TESTS)
        ]

        with run_isolation(self.runner, files):
            result = self.runner.invoke(
                verify, ["tests/", "-m", "models/simple.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("No issues found with the code.", result.output)

    def test_for_invalid_code(self):
        expected_error_messges = [
            "Expected to find method 'edge_a' in class 'Simple'.",
            "Expected to find method 'edge_b' in class 'Simple'.",
            "Expected to find method 'vertex_a' in class 'Simple'.",
            "Expected to find method 'vertex_b' in class 'Simple'."
        ]

        files = [
            ("models/simple.json", SIMPLE_MODEL),
            ("tests/__init__.py", None),
            ("tests/test.py", None)
        ]

        with run_isolation(self.runner, files):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models/simple.json"])

            self.assertEqual(result.exit_code, 4, msg=result.output)

            for error_message in expected_error_messges:
                self.assertIn(error_message, result.output)


class TestOnline(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models/simple.json", SIMPLE_MODEL),
            ("tests/__init__.py", ""),
            ("tests/test.py", SIMPLE_TESTS)
        ]

    def test_online(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                online, ["tests", "-m", "models/simple.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)


class TestOffline(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models/simple.json", SIMPLE_MODEL),
            ("tests/__init__.py", ""),
            ("tests/test.py", SIMPLE_TESTS)
        ]

    def test_offline(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["-m", "models/simple.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(OFFLINE_OUTPUT, result.output)

    def test_file_output(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["-m", "models/simple.json", "random(vertex_coverage(100))", "-f", "steps.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(Path("steps.json").exists())

            with open("steps.json") as f:
                self.assertEqual(OFFLINE_OUTPUT, f.read())


class TestWalk(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("tests/__init__.py", ""),
            ("tests/test.py", SIMPLE_TESTS),
            ("steps.json", OFFLINE_OUTPUT)
        ]

    def test_walk(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                walk, ["tests", "steps.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
