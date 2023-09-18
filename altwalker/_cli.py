#    Copyright(C) 2023 Altom Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

"""A collection of util functions for the CLI"""

import json
import os

import click

import altwalker.run as run
from altwalker.exceptions import (AltWalkerException, FailedTestsError,
                                  handle_errors)
from altwalker.generate import generate_class, generate_methods
from altwalker.reporter import create_reporters


def click_formatwarning(message, category, filename, lineno, file=None, line=None):
    """Format a warning on a single line and style the text."""

    return click.style(f"{category.__name__}: {message}\n", fg="yellow")


def _echo_model_issues(issues):
    """Pretty print the models validation issues."""

    global_issues = issues.pop("global", None)

    if global_issues:
        for error_message in global_issues:
            click.secho(f"  {error_message}", fg="red")

        click.echo()
        return

    line_width = len(max(issues.keys(), key=len, default=""))

    for key, error_messages in issues.items():
        click.secho(f"  * {key.ljust(line_width)} ", nl=False)

        if error_messages:
            click.secho("[FAILED]\n", fg="red")
        else:
            click.secho("[PASSED]", fg="green")

        for error_message in error_messages:
            click.secho(f"      {error_message}", fg="red")

        click.echo()


def _cli_validate_models(model_paths):
    click.secho("Checking models syntax:\n", bold=True, fg="green")

    response = run.validate(model_paths)
    _echo_model_issues(response["issues"])

    return response["status"]


def _cli_check_models(models, blocked=False):
    click.secho("Checking models against stop conditions:\n", bold=True, fg="green")

    response = run.check(models, blocked=blocked)

    click.secho(f"  {response['output']}", fg="red" if not response["status"] else "")
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
        click.secho(f"  * {model} ", nl=False)

        if error_messages:
            status = False
            click.secho("[FAILED]\n", fg="red")
        else:
            click.secho("[PASSED]", fg="green")

        for error_message in error_messages:
            click.secho(f"    {error_message}", fg="red")

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
            click.secho(generate_class(model, elements, language=language), fg="cyan")
        else:
            click.secho(f"# Append the following methods to your '{model}' class.\n")
            click.secho(generate_methods(elements, language=language), fg="cyan")


@handle_errors
def cli_verify(test_package, model_paths, executor_type=None, executor_url=None, import_mode=None, suggestions=False):
    click.secho("Verifying code against models:\n", bold=True, fg="green")

    response = run.verify(
        test_package, model_paths,
        executor_type=executor_type,
        executor_url=executor_url,
        import_mode=import_mode
    )
    _echo_code_issues(response["issues"])

    if suggestions and not response["status"]:
        _echo_suggestions(executor_type, response["methods"], response["missing"])

    return response["status"]


@handle_errors
def cli_init(dest_dir, model_paths=None, language="python", git=True):
    click.secho("Initiating a new project...\n", bold=True, fg="green")

    _, project_name = os.path.split(dest_dir)

    click.secho(f"  Name: {click.style(project_name, fg='yellow')}")
    click.secho(f"  Language: {click.style(language if language else 'none', fg='yellow')}")
    click.secho(f"  Git: {click.style('yes' if git else 'no', fg='yellow')}")
    click.secho()

    try:
        run.init(dest_dir, model_paths=model_paths, language=language, git=git)
        click.secho(f"Successfully created project: {project_name}.\n", fg="green")
    except FileExistsError as ex:
        raise AltWalkerException(str(ex))


@handle_errors
def cli_generate(dest_dir, model_paths, language="python"):
    language = language or "python"

    click.secho("Generating tests...\n", bold=True, fg="green")

    click.secho(f"  Language: {click.style(language if language else 'none', fg='yellow')}")
    click.secho()

    try:
        run.generate(dest_dir, model_paths, language=language)
        click.secho("Successfully generate tests.\n", fg="green")
    except FileExistsError as ex:
        raise AltWalkerException(str(ex))


@handle_errors
def cli_online(test_package, models, *args, executor_type=None, executor_url=None, gw_host=None, gw_port=8887,
               start_element=None, verbose=False, unvisited=False, blocked=False, import_mode=None, **kwargs):
    reporter = create_reporters(**kwargs)
    response = run.online(
        test_package, models,
        executor_type=executor_type, executor_url=executor_url, import_mode=import_mode,
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
def cli_walk(test_package, steps_file, executor_type=None, executor_url=None, import_mode=None, **kwargs):
    with open(steps_file) as fp:
        steps = json.load(fp)

    reporter = create_reporters(**kwargs)
    response = run.walk(
        test_package, steps,
        executor_type=executor_type,
        executor_url=executor_url,
        import_mode=import_mode,
        reporter=reporter
    )

    if not response["status"]:
        raise FailedTestsError()
