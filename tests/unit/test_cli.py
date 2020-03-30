import itertools
import unittest
import unittest.mock as mock

from click.testing import CliRunner

from tests.common.utils import run_isolation
from altwalker.cli import check, verify, init, generate, online, offline, walk
from altwalker.exceptions import FailedTestsError
from altwalker.generate import SUPPORTED_LANGUAGES
from altwalker.executor import SUPPORTED_EXECUTORS


EXECUTOR_TYPE_OPTIONS = ["--executor", "-x", "--language", "-l"]


@mock.patch("altwalker.cli.cli_check")
class TestCheck(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

    def test_check(self, cli_check_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=False
            )

    def test_error(self, cli_check_mock):
        error_message = "Error message"
        cli_check_mock.side_effect = Exception(error_message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn(error_message, result.output)
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=False
            )

    def test_fail(self, cli_check_mock):
        cli_check_mock.return_value = False

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition"])

            self.assertEqual(result.exit_code, 4, msg=result.output)
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=False
            )

    def test_multiple_models(self, cli_check_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "modelA.json", "stop_condition", "-m", "modelB.json", "stop_condition"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_check_mock.assert_called_once_with(
                (("modelA.json", "stop_condition"), ("modelB.json", "stop_condition"), ),
                blocked=False
            )

    def test_invalid_models(self, cli_check_mock):
        with run_isolation(self.runner, self.files):
            for models_option in ["--model", "-m"]:
                result = self.runner.invoke(
                    check, [models_option, "invalid.json", "stop_condition"])

                self.assertEqual(result.exit_code, 2, msg=result.output)
                self.assertIn(
                    'Invalid value for "--model" / "-m": File "invalid.json" does not exist.',
                    result.output.replace("\'", "\"")
                )

    def test_blocked(self, cli_check_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                check, ["-m", "models.json", "stop_condition", "-b"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_check_mock.assert_called_once_with(
                (("models.json", "stop_condition"), ),
                blocked=True
            )


@mock.patch("altwalker.cli.cli_verify")
class TestVerify(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}"),
        ]

        self.folders = ["tests"]

    def test_verify(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_verify_mock.assert_called_once_with(
                'tests', 'python',
                ('models.json',),
                url='http://localhost:5000/',
                suggestions=True,
            )

    def test_error(self, cli_verify_mock):
        error_message = "Error message."
        cli_verify_mock.side_effect = Exception(error_message)

        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn(error_message, result.output)
            cli_verify_mock.assert_called_once_with(
                'tests', 'python',
                ('models.json',),
                url='http://localhost:5000/',
                suggestions=True,
            )

    def test_fail(self, cli_verify_mock):
        cli_verify_mock.return_value = False

        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 4, msg=result.output)
            cli_verify_mock.assert_called_once_with(
                'tests', 'python',
                ('models.json',),
                url='http://localhost:5000/',
                suggestions=True,
            )

    def test_multiple_models(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["tests", "-m", "modelA.json", "-m", "modelB.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_verify_mock.assert_called_once_with(
                "tests", "python",
                ("modelA.json", "modelB.json", ),
                url="http://localhost:5000/",
                suggestions=True,
            )

    def test_executor_type(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for executor_type_option, exectuor_type in itertools.product(EXECUTOR_TYPE_OPTIONS, SUPPORTED_EXECUTORS):
                result = self.runner.invoke(
                    verify, [executor_type_option, exectuor_type, "tests", "-m", "models.json"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_verify_mock.assert_called_once_with(
                    'tests', exectuor_type,
                    ('models.json',),
                    url='http://localhost:5000/',
                    suggestions=True,
                )
                cli_verify_mock.reset_mock()

    def test_url(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["--url", "http://127.0.0.1:5000/", "tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_verify_mock.assert_called_once_with(
                'tests', 'python',
                ('models.json',),
                url="http://127.0.0.1:5000/",
                suggestions=True,
            )

    def test_no_suggestions(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["--no-suggestions", "tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_verify_mock.assert_called_once_with(
                'tests', 'python',
                ('models.json',),
                url='http://localhost:5000/',
                suggestions=False,
            )

    def test_suggestions(self, cli_verify_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                verify, ["--suggestions", "tests", "-m", "models.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_verify_mock.assert_called_once_with(
                'tests', 'python',
                ('models.json',),
                url='http://localhost:5000/',
                suggestions=True,
            )


@mock.patch("altwalker.cli.cli_generate")
class TestGenerate(unittest.TestCase):

    def setUp(self):
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

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_generate_mock.assert_called_once_with(
                "output_dir",
                ("models.json", ),
                language=None,
            )

    def test_error(self, cli_generate_mock):
        error_message = "Error message"
        cli_generate_mock.side_effect = Exception(error_message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "models.json"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(error_message, result.output)
            cli_generate_mock.assert_called_once_with(
                "output_dir",
                ("models.json", ),
                language=None,
            )

    def test_multiple_models(self, cli_generate_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                generate, ["output_dir", "-m", "modelA.json", "-m", "modelB.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_generate_mock.assert_called_once_with(
                "output_dir",
                ("modelA.json", "modelB.json", ),
                language=None,
            )

    def test_language(self, cli_generate_mock):
        with run_isolation(self.runner, self.files):
            for language_option, language in itertools.product(["--language", "-l"], SUPPORTED_LANGUAGES):
                result = self.runner.invoke(
                    generate, [language_option, language, "output_dir", "-m", "models.json"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_generate_mock.assert_called_once_with(
                    "output_dir",
                    ("models.json", ),
                    language=language
                )
                cli_generate_mock.reset_mock()


@mock.patch("altwalker.cli.cli_init")
class TestInit(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.files = [
            ("models.json", "{}"),
            ("modelA.json", "{}"),
            ("modelB.json", "{}")
        ]

    def test_init(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, ["."])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=(),
                language=None,
                git=True
            )

    def test_error(self, init_project):
        message = "Error messaage"
        init_project.side_effect = Exception(message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                init, ["-m", "models.json", "."])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)

    def test_multiple_models(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, ["-m", "modelA.json", "-m", "modelB.json", "."])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=("modelA.json", "modelB.json"),
                language=None,
                git=True
            )

    def test_language(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            for language_option, language in itertools.product(["--language", "-l"], SUPPORTED_LANGUAGES):
                result = self.runner.invoke(
                    init,
                    [language_option, language, "."]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_init_mock.assert_called_once_with(
                    ".",
                    model_paths=(),
                    language=language,
                    git=True
                )
                cli_init_mock.reset_mock()

    def test_git(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(init, ["--git", "."])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_init_mock.assert_called_once_with(
                ".",
                model_paths=(),
                language=None,
                git=True
            )

    def test_no_git(self, cli_init_mock):
        with run_isolation(self.runner, self.files):
            for no_git_option in ["--no-git", "-n"]:
                result = self.runner.invoke(init, [no_git_option, "."])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_init_mock.assert_called_once_with(
                    ".",
                    model_paths=(),
                    language=None,
                    git=False
                )
                cli_init_mock.reset_mock()


@mock.patch("altwalker.cli.cli_online")
class TestOnline(unittest.TestCase):

    def setUp(self):
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

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_online_mock.assert_called_once_with(
                "package", "python",
                models=(("models.json", "random(vertex_coverage(100))"),),
                url="http://localhost:5000/",
                port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None
            )

    def test_error(self, cli_online_mock):
        cli_online_mock.side_effect = FailedTestsError()

        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, ["package", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 1, msg=result.output)
            cli_online_mock.assert_called_once_with(
                "package", "python",
                models=(("models.json", "random(vertex_coverage(100))"),),
                url="http://localhost:5000/",
                port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None
            )

    def test_multiple_models(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["package", "-m", "modelA.json", "random(never)", "-m", "modelB.json", "random(never)"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_online_mock.assert_called_once_with(
                "package", "python",
                models=(("modelA.json", "random(never)"), ("modelB.json", "random(never)")),
                url="http://localhost:5000/",
                port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file=None
            )

    def test_executor_type(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for executor_type_option, exectuor_type in itertools.product(EXECUTOR_TYPE_OPTIONS, SUPPORTED_EXECUTORS):
                result = self.runner.invoke(
                    online,
                    [executor_type_option, exectuor_type, "package", "-m", "models.json", "random(never)"]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_online_mock.assert_called_once_with(
                    "package", exectuor_type,
                    models=(("models.json", "random(never)"),),
                    url="http://localhost:5000/",
                    port=8887,
                    start_element=None,
                    blocked=False,
                    unvisited=False,
                    verbose=False,
                    report_file=None,
                    report_path=False,
                    report_path_file=None
                )
                cli_online_mock.reset_mock()

    def test_start_element(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for start_element_option in ["--start-element", "-e"]:
                result = self.runner.invoke(
                    online,
                    [start_element_option, "start", "package", "-m", "models.json", "random(vertex_coverage(100))"]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_online_mock.assert_called_once_with(
                    "package", "python",
                    models=(("models.json", "random(vertex_coverage(100))"),),
                    url="http://localhost:5000/",
                    port=8887,
                    start_element="start",
                    blocked=False,
                    unvisited=False,
                    verbose=False,
                    report_file=None,
                    report_path=False,
                    report_path_file=None
                )
                cli_online_mock.reset_mock()

    def test_verbose(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for verbose_option in ["--verbose", "-o"]:
                result = self.runner.invoke(
                    online, [verbose_option, "package", "-m", "models.json", "random(vertex_coverage(100))"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_online_mock.assert_called_once_with(
                    "package", "python",
                    models=(("models.json", "random(vertex_coverage(100))"),),
                    url="http://localhost:5000/",
                    port=8887,
                    start_element=None,
                    blocked=False,
                    unvisited=False,
                    verbose=True,
                    report_file=None,
                    report_path=False,
                    report_path_file=None
                )
                cli_online_mock.reset_mock()

    def test_unvisited(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for unvisited_option in ["--unvisited", "-u"]:
                result = self.runner.invoke(
                    online, [unvisited_option, "package", "-m", "models.json", "random(vertex_coverage(100))"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_online_mock.assert_called_once_with(
                    "package", "python",
                    models=(("models.json", "random(vertex_coverage(100))"),),
                    url="http://localhost:5000/",
                    port=8887,
                    start_element=None,
                    blocked=False,
                    unvisited=True,
                    verbose=False,
                    report_file=None,
                    report_path=False,
                    report_path_file=None
                )
                cli_online_mock.reset_mock()

    def test_blocked(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for blocked_option in ["-b", "--blocked"]:
                result = self.runner.invoke(
                    online, [blocked_option, "package", "-m", "models.json", "random(vertex_coverage(100))"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_online_mock.assert_called_once_with(
                    "package", "python",
                    models=(("models.json", "random(vertex_coverage(100))"),),
                    url="http://localhost:5000/",
                    port=8887,
                    start_element=None,
                    blocked=True,
                    unvisited=False,
                    verbose=False,
                    report_file=None,
                    report_path=False,
                    report_path_file=None
                )
                cli_online_mock.reset_mock()

    def test_report_file(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online, ["--report-file", "output.txt", "package", "-m", "models.json", "random(vertex_coverage(100))"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_online_mock.assert_called_once_with(
                "package", "python",
                models=(("models.json", "random(vertex_coverage(100))"),),
                url="http://localhost:5000/",
                port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file="output.txt",
                report_path=False,
                report_path_file=None
            )

    def test_report_path(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["--report-path", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_online_mock.assert_called_once_with(
                "package", "python",
                models=(("models.json", "random(vertex_coverage(100))"),),
                url="http://localhost:5000/",
                port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=True,
                report_path_file=None
            )

    def test_report_path_file(self, cli_online_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(
                online,
                ["--report-path-file", "steps.json", "package", "-m", "models.json", "random(vertex_coverage(100))"]
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_online_mock.assert_called_once_with(
                "package", "python",
                models=(("models.json", "random(vertex_coverage(100))"),),
                url="http://localhost:5000/",
                port=8887,
                start_element=None,
                blocked=False,
                unvisited=False,
                verbose=False,
                report_file=None,
                report_path=False,
                report_path_file="steps.json"
            )


@mock.patch("altwalker.cli.cli_offline")
class TestOffline(unittest.TestCase):

    def setUp(self):
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

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_offline_mock.assert_called_once_with(
                (('models.json', 'random(vertex_coverage(100))'),),
                output_file=None,
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=False,
            )

    def test_error(self, cli_offline_mock):
        message = "Erorr messaage"
        cli_offline_mock.side_effect = Exception(message)

        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(offline, ["-m", "models.json", "random(vertex_coverage(100))"])

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(message, result.output)

    def test_multiple_models(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            result = self.runner.invoke(
                offline,
                ["-m", "modelA.json", "random(never)", "-m", "modelB.json", "random(never)"]
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_offline_mock.assert_called_once_with(
                (('modelA.json', 'random(never)'), ('modelB.json', 'random(never)')),
                output_file=None,
                start_element=None,
                unvisited=False,
                verbose=False,
                blocked=False,
            )

    def test_start_element(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            for start_element_option in ["--start-element", "-e"]:
                result = self.runner.invoke(
                    offline, [start_element_option, "start", "-m", "models.json", "random(vertex_coverage(100))"]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_offline_mock.assert_called_once_with(
                    (('models.json', 'random(vertex_coverage(100))'),),
                    output_file=None,
                    start_element="start",
                    unvisited=False,
                    verbose=False,
                    blocked=False,
                )
                cli_offline_mock.reset_mock()

    def test_verbose(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            for verbose_option in ["--verbose", "-o"]:
                result = self.runner.invoke(
                    offline, [verbose_option, "-m", "models.json", "random(vertex_coverage(100))"]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_offline_mock.assert_called_once_with(
                    (('models.json', 'random(vertex_coverage(100))'),),
                    output_file=None,
                    start_element=None,
                    unvisited=False,
                    verbose=True,
                    blocked=False,
                )
                cli_offline_mock.reset_mock()

    def test_unvisited(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            for unvisited_option in ["--unvisited", "-u"]:
                result = self.runner.invoke(
                    offline, [unvisited_option, "-m", "models.json", "random(vertex_coverage(100))"]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_offline_mock.assert_called_once_with(
                    (('models.json', 'random(vertex_coverage(100))'),),
                    output_file=None,
                    start_element=None,
                    unvisited=True,
                    verbose=False,
                    blocked=False,
                )
                cli_offline_mock.reset_mock()

    def test_blocked(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            for blocked_option in ["--blocked", "-b"]:
                result = self.runner.invoke(
                    offline, [blocked_option, "-m", "models.json", "random(vertex_coverage(100))"]
                )

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_offline_mock.assert_called_once_with(
                    (('models.json', 'random(vertex_coverage(100))'),),
                    output_file=None,
                    start_element=None,
                    unvisited=False,
                    verbose=False,
                    blocked=True,
                )
                cli_offline_mock.reset_mock()

    def test_output_file(self, cli_offline_mock):
        with run_isolation(self.runner, self.files):
            for output_file_option in ["--output-file", "-f"]:
                result = self.runner.invoke(
                    offline, [output_file_option, "output.txt", "-m", "models.json", "random(vertex_coverage(100))"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_offline_mock.assert_called_once_with(
                    (('models.json', 'random(vertex_coverage(100))'),),
                    output_file=mock.ANY,
                    start_element=None,
                    unvisited=False,
                    verbose=False,
                    blocked=False,
                )
                cli_offline_mock.reset_mock()


@mock.patch("altwalker.cli.cli_walk")
class TestWalk(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        self.folders = ["package"]
        self.files = [
            ("steps.json", "[]")
        ]

    def test_walk(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_walk_mock.assert_called_once_with(
                "package",
                "python",
                "steps.json",
                url="http://localhost:5000/",
                report_file=None,
                report_path=False,
                report_path_file=None,
            )

    def test_error(self, cli_walk_mock):
        cli_walk_mock.side_effect = FailedTestsError()

        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json"])

            self.assertEqual(result.exit_code, 1, msg=result.output)
            cli_walk_mock.assert_called_once_with(
                "package",
                "python",
                "steps.json",
                url="http://localhost:5000/",
                report_file=None,
                report_path=False,
                report_path_file=None,
            )

    def test_executor_type(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            for executor_type_option, exectuor_type in itertools.product(EXECUTOR_TYPE_OPTIONS, SUPPORTED_EXECUTORS):
                result = self.runner.invoke(walk, [executor_type_option, exectuor_type, "package", "steps.json"])

                self.assertEqual(result.exit_code, 0, msg=result.output)
                cli_walk_mock.assert_called_once_with(
                    "package",
                    exectuor_type,
                    "steps.json",
                    url="http://localhost:5000/",
                    report_file=None,
                    report_path=False,
                    report_path_file=None,
                )
                cli_walk_mock.reset_mock()

    def test_report_file(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-file", "output.txt"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_walk_mock.assert_called_once_with(
                "package",
                "python",
                "steps.json",
                url="http://localhost:5000/",
                report_file="output.txt",
                report_path=False,
                report_path_file=None,
            )

    def test_report_path(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-path"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_walk_mock.assert_called_once_with(
                "package",
                "python",
                "steps.json",
                url="http://localhost:5000/",
                report_file=None,
                report_path=True,
                report_path_file=None,
            )

    def test_report_path_file(self, cli_walk_mock):
        with run_isolation(self.runner, self.files, folders=self.folders):
            result = self.runner.invoke(walk, ["package", "steps.json", "--report-path-file", "new-steps.json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            cli_walk_mock.assert_called_once_with(
                "package",
                "python",
                "steps.json",
                url="http://localhost:5000/",
                report_file=None,
                report_path=False,
                report_path_file="new-steps.json",
            )
