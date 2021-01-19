import os
import unittest
import unittest.mock as mock

from altwalker.exceptions import FailedTestsError
from altwalker._cli_run import run_tests, cli_run


@mock.patch("altwalker._cli_run.create_walker")
@mock.patch("altwalker._cli_run.create_executor")
@mock.patch("altwalker._cli_run.create_planner")
class TestRunTests(unittest.TestCase):

    def test_create_planner(self, create_planner, create_executor, create_walker):
        run_tests("path/to/tests", "executor_type")

        create_planner.assert_called_once_with(
            models=None, host=None, port=8887, steps=None, start_element=None,
            verbose=False, unvisited=False, blocked=False)

    def test_create_planner_host(self, create_planner, create_executor, create_walker):
        run_tests("path/to/tests", "executor_type", host="127.0.0.1")

        create_planner.assert_called_once_with(
            models=None, host="127.0.0.1", port=8887, steps=None, start_element=None,
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

        create_executor.assert_called_once_with(os.path.abspath(
            'path/to/tests'), 'executor_type', url="http://localhost:4200")

    def test_kill_executor(self, create_planner, create_executor, create_walker):
        executor_mock = mock.Mock()
        create_executor.return_value = executor_mock
        create_walker.side_effect = Exception("Error message.")

        with self.assertRaisesRegex(Exception, "Error message."):
            run_tests("path/to/tests", "executor_type")

        executor_mock.kill.assert_called_once_with()

    @mock.patch("altwalker._cli_run.create_reporters")
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


@mock.patch("altwalker._cli_run.run_tests")
class TestCliRun(unittest.TestCase):

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
            cli_run("path/to/tests", "executor_type", "http://localhost:5000", models=["path/to/model"])

    def test_run(self, run_tests):
        run_tests.return_value = (True, {}, {})

        cli_run("path/to/tests", "executor_type", "http://localhost:5000",
                models=["path/to/model"], steps=[], port=9999,
                verbose=True, unvisited=True, blocked=True)

        run_tests.assert_called_once_with(
            "path/to/tests", "executor_type", url="http://localhost:5000",
            models=["path/to/model"], port=9999, steps=[], start_element=None,
            verbose=True, unvisited=True, blocked=True, report_path=False
        )
