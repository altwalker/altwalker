import unittest.mock as mock

import pytest

from altwalker.exceptions import AltWalkerError, FailedTestsError
from altwalker._cli import _echo_model_issues, _cli_validate_models, _cli_check_models, _echo_code_issues, \
    _echo_suggestions, cli_check, cli_verify, cli_init, cli_generate, cli_online, cli_offline, cli_walk


@mock.patch("click.secho")
@mock.patch("click.echo")
class TestEchoModelIssues:

    def test_global_issues(self, echo_mock, secho_mock):
        issues = {
            "global": ["No models found."]
        }

        _echo_model_issues(issues)

        secho_mock.assert_called_once_with("  No models found.", fg="red")

    def test_models_with_issues(self, echo_mock, secho_mock):
        issues = {
            "sourceFile.json::ModelName": ["Issues with the model."]
        }

        _echo_model_issues(issues)

        secho_mock.assert_any_call("  * sourceFile.json::ModelName ", nl=False)
        secho_mock.assert_any_call("[FAILED]\n", fg="red")

    def test_models_without_issues(self, echo_mock, secho_mock):
        issues = {
            "sourceFile.json::ModelName": []
        }

        _echo_model_issues(issues)

        secho_mock.assert_any_call("  * sourceFile.json::ModelName ", nl=False)
        secho_mock.assert_any_call("[PASSED]", fg="green")


@mock.patch("altwalker._cli.run.validate")
@mock.patch("altwalker._cli._echo_model_issues")
@mock.patch("click.secho")
class TestCliValidateModels:

    def test_valid_models(self, secho_mock, echo_model_issues, validate_mock):
        validate_mock.return_value = {
            "status": True,
            "issues": mock.sentinel.issues
        }

        status = _cli_validate_models(mock.sentinel.model_paths)

        validate_mock.assert_called_once_with(mock.sentinel.model_paths)
        echo_model_issues.assert_called_once_with(mock.sentinel.issues)

        assert status

    def test_invalid_models(self, secho_mock, echo_model_issues, validate_mock):
        validate_mock.return_value = {
            "status": False,
            "issues": mock.sentinel.issues
        }

        status = _cli_validate_models(mock.sentinel.model_paths)

        validate_mock.assert_called_once_with(mock.sentinel.model_paths)
        echo_model_issues.assert_called_once_with(mock.sentinel.issues)

        assert not status


@mock.patch("altwalker._cli.run.check")
@mock.patch("click.secho")
class TestCliCheckModels:

    def test_valid_models(self, secho_mock, check_mock):
        check_mock.return_value = {
            "status": True,
            "output": "No issues found with the model(s)."
        }

        status = _cli_check_models(mock.sentinel.models)

        secho_mock.assert_any_call("  No issues found with the model(s).", fg="")
        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)

        assert status

    def test_invalid_models(self, secho_mock, check_mock):
        check_mock.return_value = {
            "status": False,
            "output": "Issues found with the model(s)."
        }

        status = _cli_check_models(mock.sentinel.models)

        secho_mock.assert_any_call("  Issues found with the model(s).", fg="red")
        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)

        assert not status

    def test_blocked(self, secho_mock, check_mock):
        check_mock.return_value = {
            "status": True,
            "output": "No issues found with the model(s)."
        }

        _cli_check_models(mock.sentinel.models, blocked=True)

        check_mock.assert_called_once_with(mock.sentinel.models, blocked=True)

    def test_not_blocked(self, secho_mock, check_mock):
        check_mock.return_value = {
            "status": True,
            "output": "No issues found with the model(s)."
        }

        _cli_check_models(mock.sentinel.models, blocked=False)

        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)


@mock.patch("altwalker._cli._cli_check_models")
@mock.patch("altwalker._cli._cli_validate_models")
class TestCliCheck:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.models = [("model.json", "random(never)"), ]

    def test_valid_models(self, validate_mock, check_mock):
        validate_mock.return_value = True
        cli_check.return_value = True

        status = cli_check(self.models)

        assert validate_mock.called
        check_mock.assert_called_once_with(self.models, blocked=False)

        assert status

    @pytest.mark.parametrize(
        "return_values",
        [(True, False), (False, True), (False, False)]
    )
    def test_failed_status(self, validate_mock, check_mock, return_values):
        validate_mock.return_value = return_values[0]
        check_mock.return_value = return_values[1]

        status = cli_check(self.models)

        assert validate_mock.called
        assert check_mock.called == return_values[0]

        assert not status

    def test_blocked(self, validate_mock, check_mock):
        validate_mock.return_value = True

        cli_check(self.models, blocked=True)

        check_mock.assert_called_once_with(self.models, blocked=True)

    def test_not_blocked(self, validate_mock, check_mock):
        validate_mock.return_value = True

        cli_check(self.models, blocked=False)

        check_mock.assert_called_once_with(self.models, blocked=False)


@mock.patch("click.secho")
class TestEchoCodeIssues:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.issues = {
            "ModelA": {"issues_A", "issues_B"},
            "ModelB": {"issues_C", "issues_D"},
            "ModelC": set(),
        }

    def test_no_issues(self, secho_mock):
        _echo_code_issues({})
        secho_mock.assert_called_once_with("No issues found with the code.\n")

    def test_issues(self, secho_mock):
        _echo_code_issues(self.issues)

        for error_messages in self.issues.values():
            for error_message in error_messages:
                secho_mock.assert_any_call("    {}".format(error_message), fg="red")

        secho_mock.assert_any_call("[PASSED]", fg="green")


@mock.patch("altwalker._cli.generate_class")
@mock.patch("altwalker._cli.generate_methods")
@mock.patch("click.secho")
class TestEchoSugesstions:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.language = mock.sentinel.language

        self.methods = {
            "ModelA": {"vertex_A", "edge_A", "vertex_B", "edge_B"},
            "ModelB": {"vertex_C", "edge_C", "vertex_D", "edge_D"},
            "ModelC": {"vertex_E", "edge_E"},
        }

        self.missing_methods = {
            "ModelA": {"vertex_A", "edge_A", "vertex_B", "edge_B"},
            "ModelB": {"vertex_C", "edge_C"},
            "ModelC": set(),
        }

    def test_missing_class(self, secho_mock, generate_methods_mock, generate_class_mock):
        generate_methods_mock.return_value = ""
        generate_class_mock.return_value = ""

        methods = {
            "ModelA": {"vertex_A", "edge_A", "vertex_B", "edge_B"}
        }

        missing_methods = {
            "ModelA": {"vertex_A", "edge_A", "vertex_B", "edge_B"}
        }

        _echo_suggestions(self.language, methods, missing_methods)
        generate_class_mock.assert_called_once_with(
            self.language,
            "ModelA", {"vertex_A", "edge_A", "vertex_B", "edge_B"}
        )

    def test_missing_methods(self, secho_mock, generate_methods_mock, generate_class_mock):
        generate_methods_mock.return_value = ""
        generate_class_mock.return_value = ""

        methods = {
            "ModelA": {"vertex_A", "edge_A", "vertex_B", "edge_B"}
        }

        missing_methods = {
            "ModelA": {"vertex_A", "edge_A"}
        }

        _echo_suggestions(self.language, methods, missing_methods)
        generate_methods_mock.assert_called_once_with(self.language, {"vertex_A", "edge_A"})

    def test_no_missing_methods(self, secho_mock, generate_methods_mock, generate_class_mock):
        generate_methods_mock.return_value = ""
        generate_class_mock.return_value = ""

        methods = {
            "ModelA": {"vertex_A", "edge_A", "vertex_B", "edge_B"}
        }

        missing_methods = {
            "ModelA": set()
        }

        _echo_suggestions(self.language, methods, missing_methods)

        assert not generate_methods_mock.called
        assert not generate_class_mock.called


@mock.patch("altwalker._cli._echo_suggestions")
@mock.patch("altwalker._cli._echo_code_issues")
@mock.patch("altwalker._cli.run.verify")
@mock.patch("click.secho")
class TestCliVerify:

    def test_valid_code(self, secho_mock, verify_mock, issues_mock, suggestions_mock):
        verify_mock.return_value = {
            "status": True,
            "issues": mock.sentinel.issues
        }

        status = cli_verify("test", ["models.json"], executor_type="python", executor_url="https://localhost:8080/")

        verify_mock.assert_called_once_with(
            "test", ["models.json"], executor_type="python", executor_url="https://localhost:8080/")
        issues_mock.assert_called_once_with(mock.sentinel.issues)
        assert not suggestions_mock.called
        assert status

    def test_invalid_code(self, secho_mock, verify_mock, issues_mock, suggestions_mock):
        verify_mock.return_value = {
            "status": False,
            "issues": mock.sentinel.issues
        }

        status = cli_verify("test", ["models.json"], executor_type="python", executor_url="https://localhost:8080/")

        verify_mock.assert_called_once_with(
            "test", ["models.json"], executor_type="python", executor_url="https://localhost:8080/")
        issues_mock.assert_called_once_with(mock.sentinel.issues)
        assert not suggestions_mock.called
        assert not status

    def test_suggestions(self, secho_mock, verify_mock, issues_mock, suggestions_mock):
        verify_mock.return_value = {
            "status": False,
            "issues": mock.sentinel.issues,
            "methods": mock.sentinel.methods,
            "missing": mock.sentinel.missing
        }

        status = cli_verify(
            "test", ["models.json"], executor_type="python",
            executor_url="https://localhost:8080/", suggestions=True)

        verify_mock.assert_called_once_with(
            "test", ["models.json"], executor_type="python", executor_url="https://localhost:8080/")
        issues_mock.assert_called_once_with(mock.sentinel.issues)
        suggestions_mock.assert_called_once_with("python", mock.sentinel.methods, mock.sentinel.missing)
        assert not status


@mock.patch("altwalker._cli.run.init")
@mock.patch("click.secho")
class TestCliInit:

    def test_init(self, secho_mock, init_project_mock):
        cli_init(
            "example",
            model_paths=mock.sentinel.models,
            language="python",
            git=False,
        )

        init_project_mock.assert_called_once_with(
            "example",
            model_paths=mock.sentinel.models,
            language="python",
            git=False,
        )

    def test_error(self, secho_mock, init_project_mock):
        error_message = "Error message."
        init_project_mock.side_effect = FileExistsError(error_message)

        with pytest.raises(AltWalkerError):
            cli_init(
                "example",
                model_paths=mock.sentinel.models,
                language="python",
                git=False,
            )


@mock.patch("altwalker._cli.run.generate")
@mock.patch("click.secho")
class TestCliGenerate:

    def test_generate(self, secho_mock, generate_mock):
        cli_generate(".", ["models.json"])

        generate_mock.assert_called_with(".", ["models.json"], language="python")

    def test_error(self, secho_mock, generate_mock):
        generate_mock.side_effect = FileExistsError("File alredy exists.")

        with pytest.raises(AltWalkerError):
            cli_generate(".", ["models.json"])

        generate_mock.assert_called_with(".", ["models.json"], language="python")

    def test_language(self, secho_mock, generate_mock):
        cli_generate(".", ["models.json"], language="dotnet")

        generate_mock.assert_called_with(".", ["models.json"], language="dotnet")


@mock.patch("altwalker._cli.run.online")
@mock.patch("altwalker._cli.create_reporters")
class TestCliOnline:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.models = [("models.json", "random(never)"), ]

    def test_online(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": True
        }

        cli_online(".", self.models)

        create_reporters_mock.assert_called_once_with()
        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_error(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models)

        create_reporters_mock.assert_called_once_with()
        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_executor_type(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, executor_type="dotnet")

        online_mock.assert_called_once_with(
            '.', self.models, executor_type="dotnet", executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_executor_url(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, executor_url="http://localhost:8080/")

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url="http://localhost:8080/",
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_gw_host(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, gw_host="localhost")

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host="localhost", gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_gw_port(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, gw_port=8080)

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8080, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_start_element(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, start_element="v_start")

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element="v_start",
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_verbose(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, verbose=True)

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=True, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_unvisited(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, unvisited=True)

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=True, blocked=False,
            reporter=mock.sentinel.reporter)

    def test_blocked(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(".", self.models, blocked=True)

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=True,
            reporter=mock.sentinel.reporter)

    def test_reporter(self, create_reporters_mock, online_mock):
        create_reporters_mock.return_value = mock.sentinel.reporter
        online_mock.return_value = {
            "status": False
        }

        with pytest.raises(FailedTestsError):
            cli_online(
                ".", self.models,
                report_file="altwalker-report.log",
                report_path=True, report_path_file="steps.json",
                report_xml=True, report_xml_file="altwalker.xml")

        create_reporters_mock.assert_called_once_with(
            report_file="altwalker-report.log",
            report_path=True, report_path_file="steps.json",
            report_xml=True, report_xml_file="altwalker.xml")

        online_mock.assert_called_once_with(
            '.', self.models, executor_type=None, executor_url=None,
            gw_host=None, gw_port=8887, start_element=None,
            verbose=False, unvisited=False, blocked=False,
            reporter=mock.sentinel.reporter)


@mock.patch("altwalker._cli.run.offline")
@mock.patch("click.echo")
class TestCliOffline:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.models = [("models.json", "random(never)"), ]

    def test_offline(self, echo_mock, offline_mock):
        offline_mock.return_value = {}

        cli_offline(self.models)

        offline_mock.assert_called_once_with(
            self.models,
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False)
        echo_mock.assert_called_once_with('{}', file=None)

    def test_output_file(self, echo_mock, offline_mock):
        offline_mock.return_value = {}

        cli_offline(self.models, output_file="steps.json")

        offline_mock.assert_called_once_with(
            self.models,
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=False)
        echo_mock.assert_called_once_with('{}', file="steps.json")

    def test_start_element(self, echo_mock, offline_mock):
        offline_mock.return_value = {}

        cli_offline(self.models, start_element="v_start")

        offline_mock.assert_called_once_with(
            self.models,
            start_element="v_start",
            verbose=False,
            unvisited=False,
            blocked=False)
        echo_mock.assert_called_once_with('{}', file=None)

    def test_verbose(self, echo_mock, offline_mock):
        offline_mock.return_value = {}

        cli_offline(self.models, verbose=True)

        offline_mock.assert_called_once_with(
            self.models,
            start_element=None,
            verbose=True,
            unvisited=False,
            blocked=False)
        echo_mock.assert_called_once_with('{}', file=None)

    def test_unvisited(self, echo_mock, offline_mock):
        offline_mock.return_value = {}

        cli_offline(self.models, unvisited=True)

        offline_mock.assert_called_once_with(
            self.models,
            start_element=None,
            verbose=False,
            unvisited=True,
            blocked=False)
        echo_mock.assert_called_once_with('{}', file=None)

    def test_blocked(self, echo_mock, offline_mock):
        offline_mock.return_value = {}

        cli_offline(self.models, blocked=True)

        offline_mock.assert_called_once_with(
            self.models,
            start_element=None,
            verbose=False,
            unvisited=False,
            blocked=True)
        echo_mock.assert_called_once_with('{}', file=None)


@mock.patch("altwalker._cli.run.walk")
@mock.patch("altwalker._cli.create_reporters")
class TestCliWalk:

    def test_walk(self, create_reporters_mock, walk_mock, tmpdir):
        create_reporters_mock.return_value = mock.sentinel.reporter
        walk_mock.return_value = {
            "status": True
        }

        steps_file = "{}/steps.json".format(tmpdir)

        with open(steps_file, "w+") as fp:
            fp.write("{}")

        cli_walk("tests", steps_file)

        create_reporters_mock.assert_called_once_with()
        walk_mock.assert_called_once_with(
            "tests", {}, executor_type=None, executor_url=None, reporter=mock.sentinel.reporter)

    def test_error(self, create_reporters_mock, walk_mock, tmpdir):
        create_reporters_mock.return_value = mock.sentinel.reporter
        walk_mock.return_value = {
            "status": False
        }

        steps_file = "{}/steps.json".format(tmpdir)

        with open(steps_file, "w+") as fp:
            fp.write("{}")

        with pytest.raises(FailedTestsError):
            cli_walk("tests", steps_file)

        create_reporters_mock.assert_called_once_with()
        walk_mock.assert_called_once_with(
            "tests", {}, executor_type=None, executor_url=None, reporter=mock.sentinel.reporter)

    def test_executor_type(self, create_reporters_mock, walk_mock, tmpdir):
        create_reporters_mock.return_value = mock.sentinel.reporter
        walk_mock.return_value = {
            "status": True
        }

        steps_file = "{}/steps.json".format(tmpdir)

        with open(steps_file, "w+") as fp:
            fp.write("{}")

        cli_walk("tests", steps_file, executor_type="dotnet")

        walk_mock.assert_called_once_with(
            "tests", {}, executor_type="dotnet", executor_url=None, reporter=mock.sentinel.reporter)

    def test_executor_url(self, create_reporters_mock, walk_mock, tmpdir):
        create_reporters_mock.return_value = mock.sentinel.reporter
        walk_mock.return_value = {
            "status": True
        }

        steps_file = "{}/steps.json".format(tmpdir)

        with open(steps_file, "w+") as fp:
            fp.write("{}")

        cli_walk("tests", steps_file, executor_url="http://localhost:8080/")

        walk_mock.assert_called_once_with(
            "tests", {}, executor_type=None, executor_url="http://localhost:8080/", reporter=mock.sentinel.reporter)

    def test_reporter(self, create_reporters_mock, walk_mock, tmpdir):
        create_reporters_mock.return_value = mock.sentinel.reporter
        walk_mock.return_value = {
            "status": True
        }

        steps_file = "{}/steps.json".format(tmpdir)

        with open(steps_file, "w+") as fp:
            fp.write("{}")

        cli_walk(
            "tests", steps_file,
            report_file="altwalker-report.log",
            report_path=True, report_path_file="steps.json",
            report_xml=True, report_xml_file="altwalker.xml")

        create_reporters_mock.assert_called_once_with(
            report_file="altwalker-report.log",
            report_path=True, report_path_file="steps.json",
            report_xml=True, report_xml_file="altwalker.xml")

        walk_mock.assert_called_once_with(
            "tests", {}, executor_type=None, executor_url=None, reporter=mock.sentinel.reporter)
