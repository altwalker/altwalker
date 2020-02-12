import unittest
import unittest.mock as mock

from altwalker._check import _echo_issues, _cli_validate_models, _cli_check_models, cli_check


@mock.patch("click.secho")
@mock.patch("click.echo")
class _TestEchoIssues(unittest.TestCase):

    def test_global_issues(self, echo_mock, secho_mock):
        issues = {
            "global": ["No models found."]
        }

        _echo_issues(issues)

        secho_mock.assert_called_once_with("  No models found.", fg="red")

    def test_models_with_issues(self, echo_mock, secho_mock):
        issues = {
            "sourceFile.json::ModelName": ["Issues with the model."]
        }

        _echo_issues(issues)

        secho_mock.assert_any_call("  * sourceFile.json::ModelName ", nl=False)
        secho_mock.assert_any_call("[FAILED]\n", fg="red")

    def test_models_without_issues(self, echo_mock, secho_mock):
        issues = {
            "sourceFile.json::ModelName": []
        }

        _echo_issues(issues)

        secho_mock.assert_any_call("  * sourceFile.json::ModelName ", nl=False)
        secho_mock.assert_any_call("[PASSED]", fg="green")


@mock.patch("altwalker._check._echo_issues")
@mock.patch("altwalker._check._validate_models")
@mock.patch("altwalker._check.get_models")
@mock.patch("click.secho")
class _TestCliValidateModels(unittest.TestCase):

    def test_no_models(self, secho_mock, get_models_mock, validate_models_mock, echo_issues_mock):
        _cli_validate_models([])

        get_models_mock.assert_called_once_with([])

    def test_graphml_models(self, secho_mock, get_models_mock, validate_models_mock, echo_issues_mock):
        models = [
            ("models/model.graphml", "random(never)"),
            ("models/model.json", "length(100)")
        ]
        _cli_validate_models(models)

        get_models_mock.assert_called_once_with(["models/model.json"])

    def test_json_models(self, secho_mock, get_models_mock, validate_models_mock, echo_issues_mock):
        models = [
            ("models/model_one.json", "length(100)"),
            ("models/model_two.json", "length(100)")
        ]
        _cli_validate_models(models)

        get_models_mock.assert_called_once_with(["models/model_one.json", "models/model_two.json"])

    def test_valid_models(self, secho_mock, get_models_mock, validate_models_mock, echo_issues_mock):
        get_models_mock.return_value = mock.sentinel.models
        validate_models_mock.return_value = {}

        status = _cli_validate_models([])

        validate_models_mock.assert_called_once_with(mock.sentinel.models)
        self.assertTrue(status)

    def test_invalid_models(self, secho_mock, get_models_mock, validate_models_mock, echo_issues_mock):
        get_models_mock.return_value = mock.sentinel.models
        validate_models_mock.return_value = {"global": ["No models."]}

        status = _cli_validate_models([])

        validate_models_mock.assert_called_once_with(mock.sentinel.models)
        self.assertFalse(status)


@mock.patch("altwalker._check.check")
@mock.patch("click.secho")
class _TestCliCheckModels(unittest.TestCase):

    def test_valid_models(self, secho_mock, check_mock):
        check_mock.return_value = "No issues found with the model(s)."

        status = _cli_check_models([])

        secho_mock.assert_any_call("  No issues found with the model(s).", fg="")
        self.assertTrue(status)

    def test_invalid_models(self, secho_mock, check_mock):
        check_mock.return_value = "Issues found with the model(s)."

        status = _cli_check_models([])

        secho_mock.assert_any_call("  Issues found with the model(s).", fg="red")
        self.assertFalse(status)

    def test_models(self, secho_mock, check_mock):
        check_mock.return_value = "No issues found with the model(s)."

        _cli_check_models(mock.sentinel.models)

        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)

    def test_blocked(self, secho_mock, check_mock):
        check_mock.return_value = "No issues found with the model(s)."

        _cli_check_models(mock.sentinel.models, blocked=True)

        check_mock.assert_called_once_with(mock.sentinel.models, blocked=True)

    def test_not_blocked(self, secho_mock, check_mock):
        check_mock.return_value = "No issues found with the model(s)."

        _cli_check_models(mock.sentinel.models, blocked=False)

        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)


@mock.patch("altwalker._check._cli_check_models")
@mock.patch("altwalker._check._cli_validate_models")
class TestCliCheck(unittest.TestCase):

    def test_valide_models(self, validate_mock, check_mock):
        validate_mock.return_value = False

        cli_check(mock.sentinel.models)

        validate_mock.assert_called_once_with(mock.sentinel.models)
        self.assertEqual(check_mock.call_count, 0)

    def test_invalid_models(self, validate_mock, check_mock):
        validate_mock.return_value = True

        cli_check(mock.sentinel.models)

        validate_mock.assert_called_once_with(mock.sentinel.models)
        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)

    def test_success_status(self, validate_mock, check_mock):
        validate_mock.return_value = True
        cli_check.return_value = True

        status = cli_check(mock.sentinel.models)

        self.assertTrue(status)

    def test_failed_status(self, validate_mock, check_mock):
        return_values = [(True, False), (False, True), (False, False)]

        for x, y in return_values:
            validate_mock.return_value = x
            check_mock.return_value = y

            status = cli_check(mock.sentinel.models)
            self.assertFalse(status)

    def test_blocked(self, validate_mock, check_mock):
        validate_mock.return_value = True

        cli_check(mock.sentinel.models, blocked=True)
        check_mock.assert_called_once_with(mock.sentinel.models, blocked=True)

    def test_not_blocked(self, validate_mock, check_mock):
        validate_mock.return_value = True

        cli_check(mock.sentinel.models, blocked=False)
        check_mock.assert_called_once_with(mock.sentinel.models, blocked=False)
