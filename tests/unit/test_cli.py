import unittest
import unittest.mock as mock

from click.testing import CliRunner

from tests.common.utils import run_isolation
from altwalker.cli import check, init, generate, online, offline, walk


@mock.patch("altwalker.cli.check_models")
class TestCheck(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_models(self, check_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                check, ["-m", "invalid.json", "stop_condition"])

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn('Invalid value for "--model" / "-m": File "invalid.json" does not exist.', result.output)

    def test_blocked(self, check_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition", "-b"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition", "--blocked"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_check(self, check_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            check_mock.assert_called_once_with((("models.json", "stop_condition"), ), blocked=False)
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_erorr(self, check_mock):
        message = "Error message"
        check_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)


@mock.patch("altwalker.cli.generate_tests")
class TestGenerate(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_generate(self, generate_test_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json"])

            generate_test_mock.assert_called_once_with("output_dir", ("models.json", ))
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_erorr(self, generate_tests_mock):
        message = "Error message"
        generate_tests_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)


@mock.patch("altwalker.cli.init_repo")
class TestInit(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_init(self, init_repo_mock):
        with run_isolation(self.runner, self.files):
            self.runner.invoke(init, ["."])
            init_repo_mock.assert_called_once_with(".", (), False)

    def test_model(self, init_repo_mock):
        with run_isolation(self.runner, self.files):
            self.runner.invoke(init, ["-m", "models.json", "."])
            init_repo_mock.assert_called_once_with(".", ("models.json", ), False)

    def test_error(self, init_repo_mock):
        message = "Erorr messaage"
        init_repo_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                init, ["-m", "models.json", "."])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)


@mock.patch("altwalker.cli.run_tests")
class TestOnline(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_online(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))"])

            run_mock.assert_called_once_with(
                '', 'package',
                blocked=False,
                models=(('models.json', 'random(vertex_coverage(100))'),),
                port=8887,
                steps=None,
                unvisited=False,
                verbose=False)

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_multiple_models(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))",
                         "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_start_element(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--start-element", "start",
                         "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-e", "start",
                         "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_verbose(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--verbose", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-o", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_unvisited(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--unvisited", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-u", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_blocked(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--blocked", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-b", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, run_mock):
        message = "Erorr messaage"
        run_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)


@mock.patch("altwalker.graphwalker.offline")
class TestOffline(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_offline(self, offline_mock):
        offline_mock.return_value = {}

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_start_element(self, offline_mock):
        offline_mock.return_value = {}

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["--start-element", "Start", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                offline, ["-e", "start", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                offline, ["-e", "start", "-m", "models.json", "random(never)"])
            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn(
                "Invalid stop condition: random(never), never and time_duration are not allowed with offline.",
                result.output)

    def test_verbose(self, offline_mock):
        offline_mock.return_value = {}

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["--verbose", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                offline, ["-o", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_unvisited(self, offline_mock):
        offline_mock.return_value = {}

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["--unvisited", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                offline, ["-u", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_blocked(self, offline_mock):
        offline_mock.return_value = {}

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["--blocked", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                offline, ["-b", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_output_file(self, offline_mock):
        offline_mock.return_value = {}

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["--output-file", "output.txt", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                offline, ["-f", "output.txt", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, offline_mock):
        message = "Erorr messaage"
        offline_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(offline, ["-m", "models.json", "random(vertex_coverage(100))"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)


@mock.patch("altwalker.cli.run_tests")
class TestWalk(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("steps.json", "[]")
        ]

    def test_walk(self, run_mock):
        run_mock.return_value = (True, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            run_mock.assert_called_once_with(
                '', 'package',
                blocked=False,
                models=None,
                port=None,
                steps=[],
                unvisited=False,
                verbose=False)

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, run_mock):
        message = "Erorr messaage"
        run_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)
