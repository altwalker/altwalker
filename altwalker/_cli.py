"""A collection of util functions for the CLI"""

import os
import json

import click

import altwalker.run as run
from altwalker.exceptions import handle_errors, AltWalkerException, FailedTestsError
from altwalker.generate import generate_methods, generate_class
from altwalker.reporter import create_reporters


def click_formatwarning(message, category, filename, lineno, file=None, line=None):
    """Format a warning on a single line and style the text."""

    return click.style("{}: {}\n".format(category.__name__, message), fg="yellow")


def _echo_model_issues(issues):
    """Pretty print the models validation issues."""

    global_issues = issues.pop("global", None)

    if global_issues:
        for error_message in global_issues:
            click.secho("  {}".format(error_message), fg="red")

        click.echo()
        return

    line_width = len(max(issues.keys(), key=len, default=""))

    for key, error_messages in issues.items():
        click.secho("  * {} ".format(key.ljust(line_width)), nl=False)

        if error_messages:
            click.secho("[FAILED]\n", fg="red")
        else:
            click.secho("[PASSED]", fg="green")

        for error_message in error_messages:
            click.secho("      {}".format(error_message), fg="red")

        click.echo()


def _cli_validate_models(model_paths):
    click.secho("Checking models syntax:\n", bold=True, fg="green")

    response = run.validate(model_paths)
    _echo_model_issues(response["issues"])

    return response["status"]


def _cli_check_models(models, blocked=False):
    click.secho("Checking models against stop conditions:\n", bold=True, fg="green")

    response = run.check(models, blocked=blocked)

    click.secho("  {}".format(response["output"]), fg="red" if not response["status"] else "")
    return response["status"]


@handle_errors
def cli_check(models, blocked=False):
    status = _cli_validate_models(model_path for model_path, stop_condition in models)

    if status:
        return _cli_check_models(models, blocked=blocked)

    return status


def _echo_code_issues(issues):
    status = True

    for model, error_messages in issues.items():
        click.secho("  * {} ".format(model), nl=False)

        if error_messages:
            status = False
            click.secho("[FAILED]\n", fg="red")
        else:
            click.secho("[PASSED]", fg="green")

        for error_message in error_messages:
            click.secho("    {}".format(error_message), fg="red")

        click.secho()

    if status:
        click.secho("No issues found with the code.\n")


def _echo_suggestions(language, methods, missing_methods):
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


@handle_errors
def cli_verify(test_package, model_paths, executor_type=None, executor_url=None, suggestions=False):
    click.secho("Verifying code against models:\n", bold=True, fg="green")

    response = run.verify(test_package, model_paths, executor_type=executor_type, executor_url=executor_url)
    _echo_code_issues(response["issues"])

    if suggestions and not response["status"]:
        _echo_suggestions(executor_type, response["methods"], response["missing"])

    return response["status"]


@handle_errors
def cli_init(dest_dir, model_paths=None, language="python", git=True):
    click.secho("Initiating a new project...\n", bold=True, fg="green")

    _, project_name = os.path.split(dest_dir)

    click.secho("  Name: {}".format(click.style(project_name, fg="yellow")))
    click.secho("  Language: {}".format(click.style(language if language else "none", fg="yellow")))
    click.secho("  Git: {}".format(click.style("yes" if git else "no", fg="yellow")))
    click.secho()

    try:
        run.init(dest_dir, model_paths=model_paths, language=language, git=git)
        click.secho("Successfully created project: {}.\n".format(project_name), fg="green")
    except FileExistsError as ex:
        raise AltWalkerException(str(ex))


@handle_errors
def cli_generate(dest_dir, model_paths, language="python"):
    language = language or "python"

    click.secho("Generating tests...\n", bold=True, fg="green")

    click.secho("  Language: {}".format(click.style(language if language else "none", fg="yellow")))
    click.secho()

    try:
        run.generate(dest_dir, model_paths, language=language)
        click.secho("Successfully generate tests.\n", fg="green")
    except FileExistsError as ex:
        raise AltWalkerException(str(ex))


@handle_errors
def cli_online(test_package, models, *args, executor_type=None, executor_url=None, gw_host=None, gw_port=8887,
               start_element=None, verbose=False, unvisited=False, blocked=False, **kwargs):
    reporter = create_reporters(**kwargs)
    response = run.online(
        test_package, models,
        executor_type=executor_type, executor_url=executor_url,
        gw_port=gw_port, gw_host=gw_host, start_element=start_element,
        verbose=verbose, unvisited=unvisited, blocked=blocked,
        reporter=reporter)

    if not response["status"]:
        raise FailedTestsError()


@handle_errors
def cli_offline(models, output_file=None, start_element=None, verbose=False, unvisited=False, blocked=False):
    steps = run.offline(
        models,
        start_element=start_element,
        verbose=verbose,
        unvisited=unvisited,
        blocked=blocked
    )

    steps = json.dumps(steps, sort_keys=True, indent=4)
    click.echo(steps, file=output_file)


@handle_errors
def cli_walk(test_package, steps_file, executor_type=None, executor_url=None, **kwargs):
    with open(steps_file) as fp:
        steps = json.load(fp)

    reporter = create_reporters(**kwargs)
    response = run.walk(test_package, steps, executor_type=executor_type, executor_url=executor_url, reporter=reporter)

    if not response["status"]:
        raise FailedTestsError()
