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
        self.runner = CliRunner()
        self.files = [
            ("simple.json", SIMPLE_MODEL)
        ]

    def verify_file_structure(self, repo_path, models=None):
        models = models if models else []

        for model in models:
            self.assertTrue(Path("{}/models/{}.json".format(repo_path, model)).exists())

        self.assertTrue(Path("{}/tests/__init__.py".format(repo_path)).exists())
        self.assertTrue(Path("{}/tests/test.py".format(repo_path)).exists())

    def verify_git_repo(self, repo_path):
        repo = Repo(repo_path)
        commits = list(repo.iter_commits('master'))

        self.assertEqual(len(commits), 1, "Tests repo should have one commit")
        self.assertEqual(commits[0].summary, "Initial commit", "Commit summary should be 'Initial commit'")

    def test_init(self):
        with run_isolation(self.runner, self.files):
            packagename = "example"
            result = self.runner.invoke(init, [packagename, "-l", "python"])

            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self.verify_file_structure(packagename)
            self.verify_git_repo(packagename)

            expected_code = "\nclass ModelName:\n\n" \
                "\tdef edge_A(self):\n" \
                "\t\tpass\n\n" \
                "\tdef vertex_A(self):\n" \
                "\t\tpass\n\n" \
                "\tdef vertex_B(self):\n" \
                "\t\tpass\n\n"

            with open(packagename + "/tests/test.py", "r") as f:
                code = f.read()

                self.assertEqual(code, expected_code)

    def test_with_model(self):
        with run_isolation(self.runner, self.files):
            packagename = "example"
            result = self.runner.invoke(init, ["-m", "simple.json", packagename, "-l", "python"])
            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self.verify_file_structure(packagename)
            self.assertTrue(filecmp.cmp(packagename + "/models/simple.json", "simple.json"))
            self.verify_git_repo(packagename)


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
                verify, ["tests", "-m", "models/simple.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("No issues found with the code.", result.output)

    def test_for_invalid_code(self):
        files = [
            ("models/simple.json", SIMPLE_MODEL),
            ("tests/__init__.py", None),
            ("tests/test.py", None)
        ]

        with run_isolation(self.runner, files):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models/simple.json"])

            self.assertEqual(result.exit_code, 4, msg=result.output)

            self.assertIn("Expected to find edge_a method in class Simple.", result.output)
            self.assertIn("Expected to find edge_b method in class Simple.", result.output)
            self.assertIn("Expected to find vertex_a method in class Simple.", result.output)
            self.assertIn("Expected to find vertex_b method in class Simple.", result.output)


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
