import unittest
import filecmp
from os import path

from git import Repo
from click.testing import CliRunner

from tests.common.utils import run_isolation
from altwalker.cli import init, check


with open("tests/common/models/simple.json", "r") as f:
    simple_model = f.read()


with open("tests/common/models/invalid.json", "r") as f:
    invalid_model = f.read()


class TestCliInit(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("simple.json", simple_model)
        ]

    def verify_file_structure(self, repo_path, models=[]):
        for model in models:
            self.assertTrue(path.exists(repo_path + "/models/" + model + ".json"))

        self.assertTrue(path.exists(repo_path+"/tests/__init__.py"))
        self.assertTrue(path.exists(repo_path+"/tests/test.py"))

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

    def test_init_model(self):
        with run_isolation(self.runner, self.files):
            packagename = "example"
            result = self.runner.invoke(init, ["-m", "simple.json", packagename, "-l", "python"])
            self.assertIsNone(result.exception, msg=result.exception)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            self.verify_file_structure(packagename)
            self.assertTrue(filecmp.cmp(packagename + "/models/simple.json", "simple.json"))
            self.verify_git_repo(packagename)


class TestCliCheck(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("simple.json", simple_model),
            ("invalid.json", invalid_model)
        ]

    def test_check_valid_model(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "simple.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_check_invalid_model(self):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "invalid.json", "random(vertex_coverage(100))"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
