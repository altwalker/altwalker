import unittest
import unittest.mock as mock

from altwalker.exceptions import AltWalkerException
from altwalker._cli_offline import _normalize_stop_condition, _validate_models, cli_offline


class _TestNormalizeStopCondition(unittest.TestCase):

    def test_lowercase(self):
        stop_conditions = [
            "random(never)",
            "random(Never)",
            "Random(never)",
            "Random(Never)",
        ]

        for stop_condition in stop_conditions:
            self.assertEqual("random(never)", _normalize_stop_condition(stop_condition))

    def test_undersocore(self):
        stop_conditions = [
            "quick_random(vertex_coverage(100))",
            "quick_random(Vertex_Coverage(100))",
            "Quick_Random(vertex_coverage(100))",
            "Quick_Random(Vertex_Coverage(100))",
        ]

        for stop_condition in stop_conditions:
            self.assertEqual("quickrandom(vertexcoverage(100))", _normalize_stop_condition(stop_condition))

    def test_reached_vertex(self):
        self.assertEqual("random()", _normalize_stop_condition("random(reached_vertex(v_name))"))
        self.assertEqual("random()", _normalize_stop_condition("random(reached_vertex ( v_name ))"))

    def test_reached_edge(self):
        self.assertEqual("random()", _normalize_stop_condition("random(reached_edge(e_name))"))
        self.assertEqual("random()", _normalize_stop_condition("random(reached_edge ( e_name ))"))


class _TestValidateModels(unittest.TestCase):

    def test_valid(self):
        models = (
            ("modelA.json", "random(edge_coverage(100))"),
            ("modelB.json", "random(vertex_coverage(100))"),
            ("modelC.json", "random(reached_vertex(v_never))"),
            ("modelD.json", "random(reached_edge(e_time_duration))"),
        )

        _validate_models(models)

    def test_never(self):
        stop_conditions = ["random(never)", "quic_random(Never)"]
        model = "modelA.json"

        for stop_condition in stop_conditions:
            with self.assertRaisesRegex(AltWalkerException, r"Invalid stop condition: '.*'"):
                _validate_models([(model, stop_condition)])

    def test_time_duration(self):
        stop_conditions = ["random(time_duration(10))", "quic_random(TimeDuration(10))"]
        model = "modelA.json"

        for stop_condition in stop_conditions:
            with self.assertRaisesRegex(AltWalkerException, r"Invalid stop condition: '.*'"):
                _validate_models([(model, stop_condition)])


@mock.patch("click.echo")
@mock.patch("altwalker.graphwalker.offline")
class TestCliOffline(unittest.TestCase):

    def test_offline(self, offline_mock, echo_mock):
        offline_mock.return_value = {}

        cli_offline(
            [("model.json", "random(vertex_coverage(100))")],
            output_file=None,
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False
        )

        offline_mock.assert_called_once_with(
            models=[("model.json", "random(vertex_coverage(100))")],
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False
        )

    def test_output_file(self, offline_mock, echo_mock):
        offline_mock.return_value = {}

        cli_offline(
            [("model.json", "random(vertex_coverage(100))")],
            output_file="output.txt",
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False
        )

        echo_mock.assert_called_once_with(
            "{}",
            file="output.txt"
        )

    def test_no_output_file(self, offline_mock, echo_mock):
        offline_mock.return_value = {}

        cli_offline(
            [("model.json", "random(vertex_coverage(100))")],
            output_file=None,
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False
        )

        echo_mock.assert_called_once_with(
            "{}",
            file=None
        )
