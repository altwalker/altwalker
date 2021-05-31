import itertools
import unittest.mock as mock

import pytest
from click.testing import CliRunner

from tests.common.utils import run_isolation
from altwalker.generate import SUPPORTED_LANGUAGES
from altwalker.executor import SUPPORTED_EXECUTORS
from altwalker.cli import check, verify, init, generate, online, offline, walk


MODELS_OPTIONS = ["--model", "-m"]
EXECUTOR_TYPE_OPTIONS = ["--executor", "-x", "--language", "-l"]
LANGUAGE_OPTIONS = ["--language", "-l"]
NO_GIT_OPTIONS = ["--no-git", "-n"]
PORT_OPTIONS = ["--port", "-p"]
START_ELEMENT_OPTIONS = ["--start-element", "-e"]
VERBOSE_OPTIONS = ["--verbose", "-o"]
UNVISITED_OPTIONS = ["--unvisited", "-u"]
BLOCKED_OPTIONS = ["--blocked", "-b"]
OUTPUT_FILE_OPTIONS = ["--output-file", "-f"]


@mock.patch("altwalker.cli.cli_check")
class TestCheck:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_check(self, cli_check_mock, model_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, [model_option, "models.json", "stop_condition"])

            assert result.exit_code == 0, result.output
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=False
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_fail(self, cli_check_mock, model_option):
        cli_check_mock.return_value = False

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, [model_option, "models.json", "stop_condition"])

            assert result.exit_code == 4, result.output
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=False
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_multiple_models(self, cli_check_mock, model_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, [model_option, "modelA.json", "stop_condition", model_option, "modelB.json", "stop_condition"])

            assert result.exit_code == 0, result.output
            cli_check_mock.assert_called_once_with(
                (("modelA.json", "stop_condition"), ("modelB.json", "stop_condition"), ),
                blocked=False
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_invalid_models(self, cli_check_mock, model_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, [model_option, "invalid.json", "stop_condition"])

            assert result.exit_code == 2, result.output
            assert "Invalid value for '--model' / '-m': File 'invalid.json' does not exist." in result.output

    @pytest.mark.parametrize("blocked_option", BLOCKED_OPTIONS)
    def test_blocked(self, cli_check_mock, blocked_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition", blocked_option])

            assert result.exit_code == 0, result.output
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=True
            )


@mock.patch("altwalker.cli.cli_verify")
class TestVerify:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

        self.folders = ["tests"]

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_verify(self, cli_verify_mock, model_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", model_option, "models.json"])

            assert result.exit_code == 0, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("models.json", ),
                executor_type="python",
                executor_url=None,
                suggestions=True,
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_fail(self, cli_verify_mock, model_option):
        cli_verify_mock.return_value = False

        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", model_option, "models.json"])

            assert result.exit_code == 4, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("models.json", ),
                executor_type="python",
                executor_url=None,
                suggestions=True,
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_multiple_models(self, cli_verify_mock, model_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", model_option, "modelA.json", model_option, "modelB.json"])

            assert result.exit_code == 0, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("modelA.json", "modelB.json", ),
                executor_type="python",
                executor_url=None,
                suggestions=True,
            )

    @pytest.mark.parametrize(
        "executor_type_option, executor_type",
        itertools.product(EXECUTOR_TYPE_OPTIONS, SUPPORTED_EXECUTORS)
    )
    def test_executor_type(self, cli_verify_mock, executor_type_option, executor_type):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, [executor_type_option, executor_type, "tests", "-m", "models.json"])

            assert result.exit_code == 0, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("models.json", ),
                executor_type=executor_type,
                executor_url=None,
                suggestions=True,
            )

    def test_url(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            with pytest.warns(DeprecationWarning):
                result = self.runner.invoke(
                    verify, ["--url", "http://127.0.0.1:5000/", "tests", "-m", "models.json"])

                assert result.exit_code == 0, result.output
                cli_verify_mock.assert_called_once_with(
                    "tests", ("models.json", ),
                    executor_type="python",
                    executor_url="http://127.0.0.1:5000/",
                    suggestions=True,
                )

    def test_execuort_url(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["--executor-url", "http://127.0.0.1:5000/", "tests", "-m", "models.json"])

            assert result.exit_code == 0, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("models.json", ),
                executor_type="python",
                executor_url="http://127.0.0.1:5000/",
                suggestions=True,
            )

    def test_no_suggestions(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["--no-suggestions", "tests", "-m", "models.json"])

            assert result.exit_code == 0, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("models.json", ),
                executor_type="python",
                executor_url=None,
                suggestions=False,
            )

    def test_suggestions(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["--suggestions", "tests", "-m", "models.json"])

            assert result.exit_code == 0, result.output
            cli_verify_mock.assert_called_once_with(
                "tests", ("models.json", ),
                executor_type="python",
                executor_url=None,
                suggestions=True,
            )


@mock.patch("altwalker.cli.cli_init")
class TestInit:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}")
        ]

    def test_init(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, ["."])

            assert result.exit_code == 0, result.output
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=(),
                language=None,
                git=True
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_multiple_models(self, cli_init_mock, model_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, [model_option, "modelA.json", model_option, "modelB.json", "."])

            assert result.exit_code == 0, result.output
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=("modelA.json", "modelB.json"),
                language=None,
                git=True
            )

    @pytest.mark.parametrize(
        "language_option, language",
        itertools.product(LANGUAGE_OPTIONS, SUPPORTED_LANGUAGES)
    )
    def test_language(self, cli_init_mock, language_option, language):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                init, [language_option, language, "."]
            )

            assert result.exit_code == 0, result.output
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=(),
                language=language,
                git=True
            )

    def test_git(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, ["--git", "."])

            assert result.exit_code == 0, result.output
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=(),
                language=None,
                git=True
            )

    @pytest.mark.parametrize("no_git_option", NO_GIT_OPTIONS)
    def test_no_git(self, cli_init_mock, no_git_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, [no_git_option, "."])

            assert result.exit_code == 0, result.output
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=(),
                language=None,
                git=False
            )


@mock.patch("altwalker.cli.cli_generate")
class TestGenerate:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

    def test_generate(self, cli_generate_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json"])

            assert result.exit_code == 0, result.output
            cli_generate_mock.assert_called_once_with(
                "output_dir",
                ("models.json", ),
                language=None,
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_multiple_models(self, cli_generate_mock, model_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", model_option, "modelA.json", model_option, "modelB.json"])

            assert result.exit_code == 0, result.output
            cli_generate_mock.assert_called_once_with(
                "output_dir",
                ("modelA.json", "modelB.json", ),
                language=None,
            )

    @pytest.mark.parametrize(
        "language_option, language",
        itertools.product(LANGUAGE_OPTIONS, SUPPORTED_LANGUAGES)
    )
    def test_language(self, cli_generate_mock, language_option, language):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, [language_option, language, "output_dir", "-m", "models.json"])

            assert result.exit_code == 0, result.output
            cli_generate_mock.assert_called_once_with(
                "output_dir",
                ("models.json", ),
                language=language
            )


@mock.patch("altwalker.cli.cli_online")
class TestOnline:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.folders = ["package"]
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

    def test_online(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_multiple_models(self, cli_online_mock, model_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["package", model_option, "modelA.json", "random(never)", model_option, "modelB.json", "random(never)"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("modelA.json", "random(never)"), ("modelB.json", "random(never)")),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize(
        "executor_type_option, executor_type",
        itertools.product(EXECUTOR_TYPE_OPTIONS, SUPPORTED_EXECUTORS)
    )
    def test_executor_type(self, cli_online_mock, executor_type_option, executor_type):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                [executor_type_option, executor_type, "package", "-m", "models.json", "random(never)"]
            )

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(never)"), ),
                executor_type=executor_type,
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize("start_element_option", START_ELEMENT_OPTIONS)
    def test_start_element(self, cli_online_mock, start_element_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                [start_element_option, "start", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element="start",
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize("verbose_option", VERBOSE_OPTIONS)
    def test_verbose(self, cli_online_mock, verbose_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, [verbose_option, "package", "-m", "models.json", "random(vertex_coverage(100))"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=True,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize("unvisited_option", UNVISITED_OPTIONS)
    def test_unvisited(self, cli_online_mock, unvisited_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, [unvisited_option, "package", "-m", "models.json", "random(vertex_coverage(100))"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=True,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize("blocked_option", BLOCKED_OPTIONS)
    def test_blocked(self, cli_online_mock, blocked_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, [blocked_option, "package", "-m", "models.json", "random(vertex_coverage(100))"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=True,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize("port_option", PORT_OPTIONS)
    def test_port(self, cli_online_mock, port_option):
        with run_isolation(self.runner, self.files, folders=self.folders):
            with pytest.warns(DeprecationWarning):
                result = self.runner.invoke(
                    online, ["package", "-m", "models.json", "random(vertex_coverage(100))", port_option, 8080])

                assert result.exit_code == 0, result.output
                cli_online_mock.assert_called_once_with(
                    "package", (("models.json", "random(vertex_coverage(100))"), ),
                    executor_type="python",
                    executor_url=None,
                    gw_host=None,
                    gw_port=8080,
                    start_element=None,
                    blocked=False,
                    unvisited=False,
                    verbose=False,
                    report_file=None,
                    report_path=False,
                    report_path_file=None,
                    report_xml=False,
                    report_xml_file=None
                )

    def test_gw_port(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))", "--gw-port", 8080])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8080,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_url(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            with pytest.warns(DeprecationWarning):
                result = self.runner.invoke(
                    online,
                    ["package", "-m", "models.json", "random(vertex_coverage(100))", "--url", "http://localhost:8080"])

                assert result.exit_code == 0, result.output
                cli_online_mock.assert_called_once_with(
                    "package", (("models.json", "random(vertex_coverage(100))"), ),
                    executor_type="python",
                    executor_url="http://localhost:8080",
                    gw_host=None,
                    gw_port=8887,
                    start_element=None,
                    blocked=False,
                    unvisited=False,
                    verbose=False,
                    report_file=None,
                    report_path=False,
                    report_path_file=None,
                    report_xml=False,
                    report_xml_file=None
                )

    def test_executor_url(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["package", "-m", "models.json", "random(never)", "--executor-url", "http://localhost:8080"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(never)"), ),
                executor_type="python",
                executor_url="http://localhost:8080",
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_report_file(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, ["--report-file", "output.txt", "package", "-m", "models.json", "random(vertex_coverage(100))"])

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file="output.txt",
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_report_path(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["--report-path", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=True,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_report_path_file(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["--report-path-file", "steps.json", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file="steps.json",
                report_xml=False,
                report_xml_file=None
            )

    def test_report_xml(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["--report-xml", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=True,
                report_xml_file=None
            )

    def test_report_xml_file(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["--report-xml-file", "junit.xml", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_online_mock.assert_called_once_with(
                "package", (("models.json", "random(vertex_coverage(100))"), ),
                executor_type="python",
                executor_url=None,
                gw_host=None,
                gw_port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file="junit.xml"
            )


@mock.patch("altwalker.cli.cli_offline")
class TestOffline:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

    def test_offline(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, ["-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=None,
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=False,
            )

    @pytest.mark.parametrize("model_option", MODELS_OPTIONS)
    def test_multiple_models(self, cli_offline_mock, model_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline,
                [model_option, "modelA.json", "random(never)", model_option, "modelB.json", "random(never)"]
            )

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('modelA.json', 'random(never)'), ('modelB.json', 'random(never)')),
                output_file=None,
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=False,
            )

    @pytest.mark.parametrize("start_element_option", START_ELEMENT_OPTIONS)
    def test_start_element(self, cli_offline_mock, start_element_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, [start_element_option, "start", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=None,
                start_element="start",
                unvisited=False,
                verbose=False,
                blocked=False,
            )

    @pytest.mark.parametrize("verbose_option", VERBOSE_OPTIONS)
    def test_verbose(self, cli_offline_mock, verbose_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, [verbose_option, "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=None,
                start_element=None,
                unvisited=False,
                verbose=True,
                blocked=False,
            )

    @pytest.mark.parametrize("unvisited_option", UNVISITED_OPTIONS)
    def test_unvisited(self, cli_offline_mock, unvisited_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, [unvisited_option, "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=None,
                start_element=None,
                unvisited=True,
                verbose=False,
                blocked=False,
            )

    @pytest.mark.parametrize("blocked_option", BLOCKED_OPTIONS)
    def test_blocked(self, cli_offline_mock, blocked_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, [blocked_option, "-m", "models.json", "random(vertex_coverage(100))"]
            )

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=None,
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=True,
            )

    @pytest.mark.parametrize("output_file_option", OUTPUT_FILE_OPTIONS)
    def test_output_file(self, cli_offline_mock, output_file_option):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline, [output_file_option, "output.txt", "-m", "models.json", "random(vertex_coverage(100))"])

            assert result.exit_code == 0, result.output
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=mock.ANY,
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=False,
            )


@mock.patch("altwalker.cli.cli_walk")
class TestWalk:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()
        self.folders = ["package"]
        self.files = [
            ("steps.json", "[]")
        ]

    def test_walk(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url=None,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    @pytest.mark.parametrize(
        "executor_type_option, executor_type",
        itertools.product(EXECUTOR_TYPE_OPTIONS, SUPPORTED_EXECUTORS)
    )
    def test_executor_type(self, cli_walk_mock, executor_type_option, executor_type):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, [executor_type_option, executor_type, "package", "steps.json"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type=executor_type,
                executor_url=None,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_url(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            with pytest.warns(DeprecationWarning):
                result = self.runner.invoke(walk, ["package", "steps.json", "--url", "http://localhost:8080/"])

                assert result.exit_code == 0, result.output
                cli_walk_mock.assert_called_once_with(
                    "package",
                    "steps.json",
                    executor_type="python",
                    executor_url="http://localhost:8080/",
                    report_file=None,
                    report_path=False,
                    report_path_file=None,
                    report_xml=False,
                    report_xml_file=None
                )

    def test_executor_url(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--executor-url", "http://localhost:8080/"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url="http://localhost:8080/",
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_report_file(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-file", "output.txt"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url=None,
                report_file="output.txt",
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None,
            )

    def test_report_path(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-path"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url=None,
                report_file=None,
                report_path=True,
                report_path_file=None,
                report_xml=False,
                report_xml_file=None
            )

    def test_report_path_file(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-path-file", "new-steps.json"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url=None,
                report_file=None,
                report_path=False,
                report_path_file="new-steps.json",
                report_xml=False,
                report_xml_file=None
            )

    def test_report_xml(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-xml"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url=None,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=True,
                report_xml_file=None
            )

    def test_report_xml_file(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-xml-file", "junit.xml"])

            assert result.exit_code == 0, result.output
            cli_walk_mock.assert_called_once_with(
                "package",
                "steps.json",
                executor_type="python",
                executor_url=None,
                report_file=None,
                report_path=False,
                report_path_file=None,
                report_xml=False,
                report_xml_file="junit.xml"
            )
