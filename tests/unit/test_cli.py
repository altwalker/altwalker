import unittest
import unittest.mock as mock

from click.testing import CliRunner

from tests.common.utils import run_isolation
from altwalker.cli import run_tests, run_command, check, verify, init, generate, online, offline, walk
from altwalker.exceptions import FailedTestsError


@mock.patch("altwalker.cli.create_walker")
@mock.patch("altwalker.cli.create_executor")
@mock.patch("altwalker.cli.create_planner")
class TestRunTests(unittest.TestCase):

    def test_create_planner(self, create_planner, create_executor, create_walker):
        run_tests("path/to/tests", "executor_type")

        create_planner.assert_called_once_with(
            models=None, port=None, steps=None, start_element=None,
            verbose=False, unvisited=False, blocked=False)

    def test_kill_planner(self, create_planner, create_executor, create_walker):
        planner_mock = mock.Mock()
        create_planner.return_value = planner_mock
        create_executor.side_effect = Exception("Error message.")

        with self.assertRaisesRegex(Exception, "Error message."):
            run_tests("path/to/tests", "executor_type")

        planner_mock.kill.assert_called_once_with()

    def test_create_executor(self, create_planner, create_executor, create_walker):
        run_tests("path/to/tests", "executor_type", url="http://localhost:4200")

        create_executor.assert_called_once_with('path/to/tests', 'executor_type', url="http://localhost:4200")

    def test_kill_executor(self, create_planner, create_executor, create_walker):
        executor_mock = mock.Mock()
        create_executor.return_value = executor_mock
        create_walker.side_effect = Exception("Error message.")

        with self.assertRaisesRegex(Exception, "Error message."):
            run_tests("path/to/tests", "executor_type")

        executor_mock.kill.assert_called_once_with()

    @mock.patch("altwalker.cli.create_reporters")
    def test_create_walker(self, create_reporters, create_planner, create_executor, create_walker):
        planner = mock.Mock()
        create_planner.return_value = planner

        executor = mock.Mock()
        create_executor.return_value = executor

        reporter = mock.Mock()
        create_reporters.return_value = reporter

        run_tests("path/to/tests", "executor_type", url="http://localhost:4200")

        create_walker.assert_called_once_with(planner, executor, reporter=reporter)

    def test_status(self, create_planner, create_executor, create_walker):
        walker = mock.Mock()
        walker.status = "status"
        create_walker.return_value = walker

        status, _, _ = run_tests("path/to/tests", "executor_type", url="http://localhost:4200")

        self.assertEqual(status, "status")

    def test_statistics(self, create_planner, create_executor, create_walker):
        planner = mock.Mock()
        planner.get_statistics.return_value = {"statistics": None}
        create_planner.return_value = planner

        _, statistics, _ = run_tests("path/to/tests", "executor_type", url="http://localhost:4200")

        self.assertDictEqual(statistics, {"statistics": None})


@mock.patch("altwalker.cli.run_tests")
class TestRunCommand(unittest.TestCase):

    def setUp(self):
        self.echo_patcher = mock.patch("click.echo")
        self.secho_patcher = mock.patch("click.secho")

        self.echo_patcher.start()
        self.secho_patcher.start()

    def tearDown(self):
        self.echo_patcher.stop()
        self.secho_patcher.stop()

    def test_fail(self, run_tests):
        run_tests.return_value = (False, {}, {})

        with self.assertRaises(FailedTestsError):
            run_command("path/to/tests", "executor_type", "http://localhost:5000", models=["path/to/model"])

    def test_run(self, run_tests):
        run_tests.return_value = (True, {}, {})

        run_command("path/to/tests", "executor_type", "http://localhost:5000",
                    models=["path/to/model"], steps=[], port=9999,
                    verbose=True, unvisited=True, blocked=True)

        run_tests.assert_called_once_with(
            "path/to/tests", "executor_type", "http://localhost:5000",
            models=["path/to/model"], port=9999, steps=[], start_element=None,
            verbose=True, unvisited=True, blocked=True)


@mock.patch("altwalker.cli.check_models")
class TestCheck(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_check(self, check_models):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            check_models.assert_called_once_with((("models.json", "stop_condition"), ), blocked=False)
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, check_models):
        error_message = "Error message"
        check_models.side_effect = Exception(error_message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(error_message, result.output)

    def test_models(self, check_models):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                check, ["--model", "models.json", "stop_condition"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_invalid_models(self, check_models):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "invalid.json", "stop_condition"])

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn('Invalid value for "--model" / "-m": File "invalid.json" does not exist.', result.output)

            result = self.runner.invoke(
                check, ["--model", "invalid.json", "stop_condition"])

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn('Invalid value for "--model" / "-m": File "invalid.json" does not exist.', result.output)

    def test_blocked(self, check_models):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition", "-b"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            check_models.assert_called_once_with((("models.json", "stop_condition"), ), blocked=True)


@mock.patch("altwalker.cli.verify_code")
class TestVerify(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

        self.folders = ["tests"]

    def test_package(self, verify_code):
        pass

    def test_models(self, verify_code):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                verify, ["tests", "-m", "invalid.json"])

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn('Invalid value for "--model" / "-m": File "invalid.json" does not exist.', result.output)

    def test_executor_type(self, verify_code):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json", "-x", "python"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json", "-x", "unsupported-executor"])

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn(
                'Invalid value for "--executor" / "-x" / "--language" / "-l": invalid choice: unsupported-executor.',
                result.output)

    def test_url(self, verify_code):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json", "--url", "http://localhost:4200"])

            self.assertEqual(result.exit_code, 0, msg=result.output)


@mock.patch("altwalker.cli.generate_tests")
class TestGenerate(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_generate(self, generate_test):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json"])

            generate_test.assert_called_once_with("output_dir", ("models.json", ), language="python")
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, generate_tests):
        error_message = "Error message"
        generate_tests.side_effect = Exception(error_message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(error_message, result.output)

    def test_language(self, generate_test):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json", "-l", "c#"])

            generate_test.assert_called_once_with("output_dir", ("models.json", ), language="c#")
            self.assertEqual(result.exit_code, 0, msg=result.output)


@mock.patch("altwalker.cli.init_project")
class TestInit(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}")
        ]

    def test_init(self, init_project):
        with run_isolation(self.runner, self.files):
            self.runner.invoke(init, ["."])
            init_project.assert_called_once_with(".", model_paths=(), language=None, git=True)

    def test_model(self, init_project):
        with run_isolation(self.runner, self.files):
            self.runner.invoke(init, ["-m", "models.json", "."])
            init_project.assert_called_once_with(".", model_paths=("models.json", ), language=None, git=True)

    def test_error(self, init_project):
        message = "Error messaage"
        init_project.side_effect = Exception(message)

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
        run_mock.return_value = (True, {}, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))"])

            run_mock.assert_called_once_with(
                'package', 'python', 'http://localhost:5000/',
                models=(('models.json', 'random(vertex_coverage(100))'),),
                port=8887,
                steps=None,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False)

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_multiple_models(self, run_mock):
        run_mock.return_value = (True, {}, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))",
                         "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_start_element(self, run_mock):
        run_mock.return_value = (True, {}, {})

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
        run_mock.return_value = (True, {}, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--verbose", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-o", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_unvisited(self, run_mock):
        run_mock.return_value = (True, {}, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--unvisited", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-u", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_blocked(self, run_mock):
        run_mock.return_value = (True, {}, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "--blocked", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            result = self.runner.invoke(
                online, ["package", "-b", "-m", "models.json", "random(vertex_coverage(100))"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, run_mock):
        message = "Error message"
        run_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)

    def test_executor(self, run_mock):
        with run_isolation(self.runner, self.files, folders=["package"]):
            self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))", "-x", "http"])
        run_mock.assert_called_once_with(
            'package', 'http', 'http://localhost:5000/',
            blocked=False,
            models=(('models.json', 'random(vertex_coverage(100))'),),
            port=8887,
            start_element=None,
            steps=None,
            unvisited=False,
            verbose=False,
            report_file=None,
            report_path=False)

    def test_language(self, run_mock):
        with run_isolation(self.runner, self.files, folders=["package"]):
            self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))", "-l", "c#"])
        run_mock.assert_called_once_with(
            'package', 'c#', 'http://localhost:5000/',
            blocked=False,
            models=(('models.json', 'random(vertex_coverage(100))'),),
            port=8887,
            steps=None,
            start_element=None,
            unvisited=False,
            verbose=False,
            report_file=None,
            report_path=False)


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

            offline_mock.assert_called_once_with(
                models=(('models.json', 'random(vertex_coverage(100))'),),
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=False)
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

    def test_walk(self, run_tests):
        run_tests.return_value = (True, {}, {})

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            run_tests.assert_called_once_with(
                'package', 'python', 'http://localhost:5000/',
                models=None,
                port=None,
                steps=[],
                start_element=None,
                verbose=False,
                unvisited=False,
                blocked=False,
                report_file=None,
                report_path=False)

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_error(self, run_tests):
        error_message = "Erorr messaage"
        run_tests.side_effect = Exception(error_message)

        with run_isolation(self.runner, self.files, folders=["package"]):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(error_message, result.output)
