import os
import unittest
import unittest.mock as mock

from altwalker.exceptions import FailedTestsError
from altwalker._cli_run import _percentege_color, _style_percentage, _style_fail, _echo_stat, \
    _echo_status, _echo_statistics, run_tests, cli_run


class _TestPercentageColor(unittest.TestCase):

    def test_red(self):
        for percentage in range(0, 50):
            self.assertEqual(_percentege_color(percentage), "red")

    def test_yellow(self):
        for percentage in range(50, 80):
            self.assertEqual(_percentege_color(percentage), "yellow")

    def test_green(self):
        for percentage in range(80, 100):
            self.assertEqual(_percentege_color(percentage), "green")


class _TestStylePercentage(unittest.TestCase):

    def test_message(self):
        for percentage in range(0, 100):
            self.assertIn("{}%".format(percentage), _style_percentage(percentage))


class _TestStyleFail(unittest.TestCase):

    def test_message(self):
        for number in range(0, 100):
            self.assertIn(str(number), _style_fail(number))


@mock.patch("click.echo")
class _TestEchoStat(unittest.TestCase):

    def test_message(self, echo):
        title = "Title"
        value = 100

        _echo_stat(title, value)

        echo.assert_called_once_with(mock.ANY)


@mock.patch("altwalker._cli_run._echo_stat")
@mock.patch("click.echo")
class _TestEchoStatistics(unittest.TestCase):

    def test_statistics(self, echo, echo_stat):
        statistics = {
            "edgeCoverage": 100,
            "edgesNotVisited": [],
            "totalCompletedNumberOfModels": 1,
            "totalFailedNumberOfModels": 0,
            "totalIncompleteNumberOfModels": 0,
            "totalNotExecutedNumberOfModels": 0,
            "totalNumberOfEdges": 1,
            "totalNumberOfModels": 1,
            "totalNumberOfUnvisitedEdges": 0,
            "totalNumberOfUnvisitedVertices": 0,
            "totalNumberOfVertices": 2,
            "totalNumberOfVisitedEdges": 1,
            "totalNumberOfVisitedVertices": 2,
            "vertexCoverage": 100,
            "verticesNotVisited": []
        }

        _echo_statistics(statistics)

        self.assertGreater(echo.call_count, 0)
        echo_stat.assert_any_call("Model Coverage", mock.ANY)
        echo_stat.assert_any_call("Number of Models", mock.ANY)
        echo_stat.assert_any_call("Completed Models", mock.ANY)
        echo_stat.assert_any_call("Failed Models", mock.ANY)
        echo_stat.assert_any_call("Incomplete Models", mock.ANY)
        echo_stat.assert_any_call("Not Executed Models", mock.ANY)

        echo_stat.assert_any_call("Edge Coverage", mock.ANY)
        echo_stat.assert_any_call("Number of Edges", mock.ANY)
        echo_stat.assert_any_call("Visited Edges", mock.ANY)
        echo_stat.assert_any_call("Unvisited Edges", mock.ANY)

        echo_stat.assert_any_call("Vertex Coverage", mock.ANY)
        echo_stat.assert_any_call("Number of Vertices", mock.ANY)
        echo_stat.assert_any_call("Visited Vertices", mock.ANY)
        echo_stat.assert_any_call("Unvisited Vertices", mock.ANY)


@mock.patch("click.secho")
@mock.patch("click.echo")
class _TestEchoStatus(unittest.TestCase):

    def test_pass(self, echo, secho):
        _echo_status(True)

        self.assertGreater(echo.call_count, 0)
        self.assertGreater(secho.call_count, 0)

        self.assertEqual([mock.call(" PASSED ", bg="green")], secho.mock_calls)

    def test_fail(self, echo, secho):
        _echo_status(False)

        self.assertGreater(echo.call_count, 0)
        self.assertGreater(secho.call_count, 0)

        self.assertEqual([mock.call(" FAILED ", bg="red")], secho.mock_calls)


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
