"""A collection of util functions for the verify command."""

import click

from altwalker._utils import _get_issues
from altwalker.executor import create_executor
from altwalker.model import validate_models
from altwalker.code import _validate_code, get_methods, get_missing_methods
from altwalker.generate import generate_methods, generate_class


def _echo_issues(issues):
    for model, error_messages in issues.items():
        click.secho("  * {} ".format(model), nl=False)

        if error_messages:
            click.secho("[FAILED]\n", fg="red")
        else:
            click.secho("[PASSED]", fg="green")

        for error_message in error_messages:
            click.secho("    {}".format(error_message), fg="red")

        click.secho()

    if not _get_issues(issues):
        click.secho("No issues found with the code.\n")


def _echo_sugesstions(language, methods, missing_methods):
    click.secho("\nCode suggestions:\n", bold=True, fg="cyan")

    for model, elements in missing_methods.items():
        if not elements:
            break
        elif elements == methods[model]:
            click.secho("# Append the following class to your test file.\n")
            click.secho(generate_class(language, model, elements), fg="cyan")
        else:
            click.secho("# Append the following methods to your '{}' class.\n".format(model))
            click.secho(generate_methods(language, elements), fg="cyan")


def cli_verify(test_package, excutor_type, models, url, suggestions=False):
    click.secho("Verifying code agains models:\n", bold=True, fg="green")

    executor = create_executor(test_package, excutor_type, url)
    try:
        validate_models(models)

        methods = get_methods(models)
        missing_methods = get_missing_methods(executor, methods)

        issues = _validate_code(executor, methods)
        _echo_issues(issues)

        if suggestions and missing_methods:
            _echo_sugesstions(excutor_type, methods, missing_methods)

        return not bool(missing_methods)
    finally:
        executor.kill()
