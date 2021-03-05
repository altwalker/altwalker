import os.path
import unittest.mock as mock

import pytest

from altwalker.exceptions import AltWalkerException
from altwalker.run import _normalize_stop_condition, _validate_stop_conditions, _run_tests, validate, check, verify, \
    init, generate, offline, online, walk


@mock.patch("altwalker.run._validate_models")
@mock.patch("altwalker.run.get_models")
class TestValidate:

    def test_validate(self, get_models_mock, validate_mock):
        get_models_mock.return_value = mock.sentinel.models
        validate_mock.return_value = {}

        response = validate(["models.json", "models.graphml"])

        get_models_mock.assert_called_once_with(["models.json"])
        validate_mock.assert_called_once_with(mock.sentinel.models)
        assert response["status"]

    def test_status(self, get_models_mock, validate_mock):
        get_models_mock.return_value = mock.sentinel.models
        validate_mock.return_value = {"models.json": {"No models found."}}

        response = validate(["models.json", "models.graphml"])

        get_models_mock.assert_called_once_with(["models.json"])
        validate_mock.assert_called_once_with(mock.sentinel.models)
        assert not response["status"]


@mock.patch("altwalker.run.graphwalker.check")
class TestCheck:

    def test_valid_models(self, check_mock):
        output = "No issues found with the model(s)"
        check_mock.return_value = output
        response = check([("model.json", "random(never)")])

        assert response["status"]
        assert response["output"] == output
        check_mock.assert_called_once_with([('model.json', 'random(never)')], blocked=False)

    def test_invalid_models(self, check_mock):
        output = ""
        check_mock.return_value = output
        response = check([("model.json", "random(never)")])

        assert not response["status"]
        assert response["output"] == output
        check_mock.assert_called_once_with([('model.json', 'random(never)')], blocked=False)

    def test_blocked(self, check_mock):
        output = "No issues found with the model(s)"
        check_mock.return_value = output
        response = check([("model.json", "random(never)")], blocked=True)

        assert response["status"]
        assert response["output"] == output
        check_mock.assert_called_once_with([('model.json', 'random(never)')], blocked=True)


@mock.patch("altwalker.run.create_executor")
@mock.patch("altwalker.run._validate_code")
@mock.patch("altwalker.run.get_missing_methods")
@mock.patch("altwalker.run.get_methods")
@mock.patch("altwalker.run.validate_models")
class TestVerify:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_package = "tests"
        self.models = ["models.json", "models.graphml"]

    def test_validate(self, *args):
        verify(self.test_package, self.models)

    def test_invalid_models(self, validate_models_mock, *args):
        validate_models_mock.side_effect = AltWalkerException("Error.")

        with pytest.raises(AltWalkerException):
            verify(self.test_package, self.models)

        validate_models_mock.assert_called_once_with(self.models)


@mock.patch("altwalker.run.init_project")
class TestInit:

    def test_init(self, init_project_mock):
        init("project-name")

        init_project_mock.assert_called_once_with("project-name", model_paths=None, language=None, git=True)

    def test_model_paths(self, init_project_mock):
        model_paths = ["models.json", "models.graphml"]
        init("project-name", model_paths=model_paths)

        init_project_mock.assert_called_once_with("project-name", model_paths=model_paths, language=None, git=True)

    def test_language(self, init_project_mock):
        language = "dotnet"
        init("project-name", language=language)

        init_project_mock.assert_called_once_with("project-name", model_paths=None, language="dotnet", git=True)

    def test_git(self, init_project_mock):
        init("project-name", git=False)

        init_project_mock.assert_called_once_with("project-name", model_paths=None, language=None, git=False)


@mock.patch("altwalker.run.generate_tests")
class TestGenerate:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.model_paths = ["models.json", "models.gramphml"]

    def test_generate(self, generate_tests_mock):
        generate(".", self.model_paths)

        generate_tests_mock.assert_called_once_with(".", self.model_paths, language=None)


@pytest.mark.parametrize(
    "stop_condition, expected",
    [
        ("random(never)", "random(never)"),
        ("Random(Never)", "random(never)"),
        ("weighted_random(never)", "weightedrandom(never)"),
        ("Weighted_Random(Never)", "weightedrandom(never)"),
        ("WeightedRandom(Never)", "weightedrandom(never)"),
        ("random(reached_vertex(v_never))", "random()"),
        ("Random(Reached_Vertex(v_never))", "random()"),
        ("Random(ReachedVertex(v_never))", "random()"),
        ("random(reached_edge(v_timeduration))", "random()"),
        ("Random(Reached_Edge(v_timeduration))", "random()"),
        ("Random(ReachedEdge(v_timeduration))", "random()")
    ]
)
def test_normalize_stop_condition(stop_condition, expected):
    assert _normalize_stop_condition(stop_condition) == expected


class TestValidateStopConditions:

    @pytest.mark.parametrize(
        "stop_condition",
        [
            "random(vertex_coverage(100))",
            "Random(VertexCoverage(100))",
            "weighted_random(reached_edge(v_never))"
        ]
    )
    def test_valid_stop_conditions(self, stop_condition):
        _validate_stop_conditions([stop_condition])

    @pytest.mark.parametrize(
        "stop_condition",
        [
            "random(never)",
            "Random(Never)",
            "random(time_duration(100)))",
            "Random(TimeDuration(100)))",
            "weighted_random(never)",
            "WeightedRandom(Never)",
            "weighted_random(time_duration(100))",
            "WeightedRandom(TimeDuration(100))"
        ]
    )
    def test_invalid_stop_conditions(self, stop_condition):
        with pytest.raises(AltWalkerException):
            _validate_stop_conditions([stop_condition])


@mock.patch("altwalker.run.graphwalker.offline")
class TestOffline:

    def test_offline(self, offline_mock):
        models = [("models.json", "random(vertex_coverage(100))")]
        offline_mock.return_value = mock.sentinel.steps

        steps = offline(models)

        offline_mock.assert_called_once_with(
            models,
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False
        )
        assert steps == mock.sentinel.steps


@mock.patch("altwalker.run.create_walker")
@mock.patch("altwalker.run.create_reporters")
@mock.patch("altwalker.run.create_executor")
@mock.patch("altwalker.run.create_planner")
class TestRunTests:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.test_package = "path/to/tests"

    def test_run_tests(self, create_planner_mock, create_executor_mock, create_reporters_mock, create_walker_mock):
        _run_tests(self.test_package)

        create_planner_mock.assert_called_once_with(
            models=None, host=None, port=8887, steps=None, start_element=None,
            verbose=False, unvisited=False, blocked=False)
        create_executor_mock.assert_called_once_with(os.path.abspath(self.test_package), None, url=None)
        create_reporters_mock.assert_called_once_with()
        create_walker_mock.assert_called_once_with(
            create_planner_mock.return_value, create_executor_mock.return_value,
            reporter=create_reporters_mock.return_value
        )

    def test_error(self, create_planner_mock, create_executor_mock, create_reporters_mock, create_walker_mock):
        planner_mock = mock.Mock()
        create_planner_mock.return_value = planner_mock
        create_planner_mock.side_effect = AltWalkerException("Error.")

        with pytest.raises(AltWalkerException):
            _run_tests(self.test_package)

    def test_kill_planner(self, create_planner_mock, create_executor_mock, create_reporters_mock, create_walker_mock):
        planner_mock = mock.Mock()
        create_planner_mock.return_value = planner_mock
        create_executor_mock.side_effect = AltWalkerException("Error.")

        with pytest.raises(AltWalkerException):
            _run_tests(self.test_package)

        planner_mock.kill.assert_called_once_with()

    def test_kill_executor(self, create_planner_mock, create_executor_mock, create_reporters_mock, create_walker_mock):
        executor_mock = mock.Mock()
        create_executor_mock.return_value = executor_mock
        create_walker_mock.side_effect = AltWalkerException("Error.")

        with pytest.raises(AltWalkerException):
            _run_tests(self.test_package)

        executor_mock.kill.assert_called_once_with()


@mock.patch("altwalker.run._run_tests")
class TestOnline:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.models = ["models.json", "models.graphml"]

    def test_online(self, run_test_mock):
        online("tests", self.models)

        run_test_mock.assert_called_once_with(
            "tests", models=self.models, executor_type=None, executor_url=None,
            gw_port=8887, gw_host=None, start_element=None, verbose=False, unvisited=False, blocked=False,
            reporter=None)


@mock.patch("altwalker.run._run_tests")
class TestWalk:

    def test_walk(self, run_test_mock):
        walk("tests", steps=mock.sentinel.steps)

        run_test_mock.assert_called_once_with(
            "tests", steps=mock.sentinel.steps,
            executor_type=None, executor_url=None, reporter=None)
