import platform
import unittest
import unittest.mock as mock

from altwalker._utils import get_command, url_join, has_git, _percentege_color, \
    _style_percentage, _style_fail, _echo_stat, echo_statistics, echo_status


class TestGetCommand(unittest.TestCase):

    def test_get_command(self):
        if platform.system() == "Windows":
            self.assertListEqual(get_command("gw"), ["cmd.exe", "/C", "gw"])
        else:
            self.assertListEqual(get_command("gw"), ["gw"])


class TestUrlJoin(unittest.TestCase):

    def test_url_join(self):
        expected = "http://localhost:5000/altwalker"

        self.assertEqual(url_join("http://localhost:5000", "altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000", "/altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000", "/altwalker/"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "/altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "/altwalker/"), expected)


@mock.patch("subprocess.Popen")
class TestHasGit(unittest.TestCase):

    def test_has_git(self, popen):
        process = mock.Mock()
        process.communicate.return_value = (b"git version 2.20.1", b"")
        popen.return_value = process

        self.assertTrue(has_git())

    def test_stderr(self, popen):
        process = mock.Mock()
        process.communicate.return_value = (b"", b"git not installed")
        popen.return_value = process

        self.assertFalse(has_git())

    def test_for_file_not_found(self, popen):
        popen.side_effect = FileNotFoundError("Message")
        self.assertFalse(has_git())


class TestPercentageColor(unittest.TestCase):

    def test_red(self):
        for percentage in range(0, 50):
            self.assertEqual(_percentege_color(percentage), "red")

    def test_yellow(self):
        for percentage in range(50, 80):
            self.assertEqual(_percentege_color(percentage), "yellow")

    def test_green(self):
        for percentage in range(80, 100):
            self.assertEqual(_percentege_color(percentage), "green")


class TestStylePercentage(unittest.TestCase):

    def test_message(self):
        for percentage in range(0, 100):
            self.assertIn("{}%".format(percentage), _style_percentage(percentage))


class TestStyleFail(unittest.TestCase):

    def test_message(self):
        for number in range(0, 100):
            self.assertIn(str(number), _style_fail(number))


@mock.patch("click.echo")
class TestEchoStat(unittest.TestCase):

    def test_message(self, echo):
        title = "Title"
        value = 100

        _echo_stat(title, value)

        echo.assert_called_once_with(mock.ANY)


@mock.patch("altwalker._utils._echo_stat")
@mock.patch("click.echo")
class TestEchoStatistics(unittest.TestCase):

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

        echo_statistics(statistics)

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
class TestEchoStatus(unittest.TestCase):

    def test_pass(self, echo, secho):
        echo_status(True)

        self.assertGreater(echo.call_count, 0)
        self.assertGreater(secho.call_count, 0)

        self.assertEqual([mock.call(" PASS ", bg="green")], secho.mock_calls)

    def test_fail(self, echo, secho):
        echo_status(False)

        self.assertGreater(echo.call_count, 0)
        self.assertGreater(secho.call_count, 0)

        self.assertEqual([mock.call(" FAIL ", bg="red")], secho.mock_calls)
