"""A collection of util functions for the check command."""

import click

from altwalker.model import _get_issues, _validate_models, get_models
from altwalker.graphwalker import check


def _echo_issues(issues):
    """Pretty print the models validation issues."""

    global_issues = issues.pop("global", None)

    if global_issues:
        for error_message in global_issues:
            click.secho("  {}".format(error_message), fg="red")

        click.echo()
        return

    line_width = len(max(issues.keys(), key=len))

    for key, error_messages in issues.items():
        click.secho("  * {} ".format(key.ljust(line_width)), nl=False)

        if error_messages:
            click.secho("[FAILED]\n", fg="red")
        else:
            click.secho("[PASSED]", fg="green")

        for error_message in error_messages:
            click.secho("      {}".format(error_message), fg="red")

        click.echo()


def _cli_validate_models(models):
    """Check the models for syntax errors.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.

    Returns:
        bool: Return true if the models are valid, false otherwise.
    """

    click.secho("Checking models syntax:\n", bold=True, fg="green")

    json_models_paths = [model_path for model_path, _ in models if model_path.endswith(".json")]
    models = get_models(json_models_paths)

    issues = _validate_models(models)
    _echo_issues(issues)

    return not bool(_get_issues(issues))


def _cli_check_models(models, blocked=False):
    """Check the models for issues using GraphWalker's check command.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        blocked (:obj:`bool`): If set to true will fiter out elements with the keyword ``blocked``.

    Returns:
        bool: Return true if the models are valid, false otherwise.
    """

    click.secho("Checking models against stop conditions:\n", bold=True, fg="green")

    output = check(models, blocked=blocked)
    status = output.startswith("No issues found with the model(s)")

    click.secho("  {}".format(output), fg="red" if not status else "")
    return status


def cli_check(models, blocked=False):
    """Check the models for issues.

    Args:
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        blocked (:obj:`bool`): If set to true will fiter out elements with the keyword ``blocked``.
    """

    status = _cli_validate_models(models)

    if status:
        status = _cli_check_models(models, blocked=blocked)

    return status
