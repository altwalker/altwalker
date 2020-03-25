import unittest
import unittest.mock as mock

from altwalker._cli_verify import _echo_issues, _echo_sugesstions, cli_verify


@mock.patch("click.secho")
class _TestEchoIssues(unittest.TestCase):

    def setUp(self):
        self.issues = {
            "ModelA": {"issues_A", "issues_B"},
            "ModelB": {"issues_C", "issues_D"},
            "ModelC": set(),
        }

    def test_no_issues(self, secho_mock):
        _echo_issues({})
        secho_mock.assert_called_once_with("No issues found with the code.\n")

    def test_issues(self, secho_mock):
        _echo_issues(self.issues)

        for error_messages in self.issues.values():
            for error_message in error_messages:
                secho_mock.assert_any_call("    {}".format(error_message), fg="red")

        secho_mock.assert_any_call("[PASSED]", fg="green")


@mock.patch("altwalker._cli_verify.generate_class")
@mock.patch("altwalker._cli_verify.generate_methods")
@mock.patch("click.secho")
class _TestEchoSugesstions(unittest.TestCase):

    def setUp(self):
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

        _echo_sugesstions(self.language, methods, missing_methods)
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

        _echo_sugesstions(self.language, methods, missing_methods)
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

        _echo_sugesstions(self.language, methods, missing_methods)

        self.assertEqual(generate_methods_mock.call_count, 0)
        self.assertEqual(generate_class_mock.call_count, 0)


@mock.patch("click.secho")
@mock.patch("altwalker._cli_verify._echo_sugesstions")
@mock.patch("altwalker._cli_verify._validate_code")
@mock.patch("altwalker._cli_verify.get_missing_methods")
@mock.patch("altwalker._cli_verify.get_methods")
@mock.patch("altwalker._cli_verify.validate_models")
@mock.patch("altwalker._cli_verify.create_executor")
class TestCliVerify(unittest.TestCase):

    def test_no_suggestions(self, *args):
        _echo_sugesstions_mock = args[5]

        cli_verify(
            "example",
            "python",
            mock.sentinel.models,
            "url",
            suggestions=False
        )

        self.assertEqual(_echo_sugesstions_mock.call_count, 0)

    def test_suggestions(self, *args):
        _get_methods_mock = args[2]
        _get_missing_methods_mock = args[3]
        _echo_sugesstions_mock = args[5]

        _get_methods_mock.return_value = mock.sentinel.methods
        _get_missing_methods_mock.return_value = mock.sentinel.missing_methods

        cli_verify(
            "example",
            "python",
            mock.sentinel.models,
            "url",
            suggestions=True
        )

        _echo_sugesstions_mock.assert_called_once_with(
            "python",
            mock.sentinel.methods,
            mock.sentinel.missing_methods
        )

    def test_success_status(self, *args):
        _get_missing_methods_mock = args[3]
        _get_missing_methods_mock.return_value = {}

        status = cli_verify(
            "example",
            "python",
            mock.sentinel.models,
            "url",
            suggestions=True
        )

        self.assertTrue(status)

    def test_failed_status(self, *args):
        _get_missing_methods_mock = args[3]
        _get_missing_methods_mock.return_value = {"ModelA": set()}

        status = cli_verify(
            "example",
            "python",
            mock.sentinel.models,
            "url",
            suggestions=True
        )

        self.assertFalse(status)
