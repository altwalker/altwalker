import json
import warnings
import logging

import click

import altwalker.graphwalker as graphwalker
from altwalker._utils import click_formatwarning, echo_status, echo_statistics
from altwalker.exceptions import FailedTestsError, handle_errors
from altwalker.model import check_models, verify_code
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import create_reporters
from altwalker.init import init_project, generate_tests


# replace the default warning formating
warnings.formatwarning = click_formatwarning


CONTEXT_SETTINGS = dict(help_option_names=["--help", "-h"])


model_and_generator_option = click.option(
    "--model", "-m", "models",
    type=(click.Path(exists=True, dir_okay=False), str), required=True, multiple=True,
    help="The model, as a graphml/json file followed by generator with stop condition.")

model_file_option = click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
                                 required=True, multiple=True,
                                 help="The model, as a graphml/json file.")

start_element_option = click.option("--start-element", "-e",
                                    help="Sets the starting element in the first model.")

verbose_option = click.option("--verbose", "-o", default=False, is_flag=True,
                              help="Will also print the model data and the properties for each step.")

unvisted_option = click.option("--unvisited", "-u", default=False, is_flag=True,
                               help="Will also print the remaining unvisited elements in the model.")

blocked_option = click.option("--blocked", "-b", default=False, is_flag=True,
                              help="Will fiter out elements with the keyword BLOCKED.")

language_option = click.option("--language", "-l", type=click.Choice(["python", "c#", "dotnet"]),
                               help="The programming language of the tests.")

executor_option = click.option("--executor", "-x", "--language", "-l", "executor",
                               type=click.Choice(["python", "c#", "dotnet", "http"]),
                               default="python", show_default=True,
                               help="Configure the executor to be used.")

url_option = click.option("--url", default="http://localhost:5000/", show_default=True,
                          help="The url for the executor.")


report_file_option = click.option("--report-file", type=click.Path(exists=False, dir_okay=False),
                                  help="Save the report in a file.")

report_path_option = click.option("--report-path", default=False, is_flag=True,
                                  help="Report the path.")


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, "--version", "-v", prog_name="AltWalker")
@click.option("--log-level", type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
              case_sensitive=False), default="WARNING", show_default=True, envvar="ALTWALKER_LOG_LEVEL",
              help="Sets the logger level to the specified level.")
@click.option("--log-file", type=click.Path(exists=False, dir_okay=False), envvar="ALTWALKER_LOG_FILE",
              help="Sends logging output to a file.")
def cli(log_level, log_file):
    """A command line tool for running model-based tests."""

    logging.basicConfig(filename=log_file, level=log_level.upper())


@cli.command()
@add_options([model_and_generator_option, blocked_option])
@handle_errors
def check(models, blocked):
    """Check and analyze model(s) for issues."""

    check_models(models, blocked=blocked)
    click.echo("No issues found with the model(s).")


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@add_options([model_file_option, executor_option, url_option])
@handle_errors
def verify(test_package, models, url, **options):
    """Verify test code from TEST_PACAKGE against the model(s)."""

    executor = options["executor"]

    verify_code(test_package, executor, models, url)
    click.echo("No issues found with the code.")


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False))
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              required=False, multiple=True,
              help="The model, as a graphml/json file.")
@click.option("--git/--no-git", " /-n", "git", default=True, is_flag=True,
              help="If set to true will initialize a git repository.", show_default=True)
@add_options([language_option])
@handle_errors
def init(dest_dir, models, git, language):
    """Initialize a new project."""

    init_project(dest_dir, model_paths=models, language=language, git=git)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False))
@add_options([model_file_option, language_option])
@handle_errors
def generate(dest_dir, models, language):
    """Generate test code template based on the given model(s)."""

    if language is None:
        language = "python"

    generate_tests(dest_dir, models, language=language)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--port", "-p", default=8887,
              help="Sets the port of the GraphWalker service.")
@add_options([model_and_generator_option, start_element_option, executor_option, url_option,
              verbose_option, unvisted_option, blocked_option, report_path_option, report_file_option])
@handle_errors
def online(test_package, **options):
    """Run the tests from TEST_PACKAGE path using the GraphWalker online RESTFUL service."""

    executor = options.pop("executor")
    url = options.pop("url")

    run_command(test_package, executor, url, **options)


@cli.command()
@click.option("--output-file", "-f", type=click.File(mode="w", lazy=True, atomic=True),
              help="Output file.")
@add_options([model_and_generator_option, start_element_option, verbose_option, unvisted_option, blocked_option])
@handle_errors
def offline(**options):
    """Generate a test path once, that can be runned later."""

    for _, stop_condition in options["models"]:
        if "never" in stop_condition or "time_duration" in stop_condition:
            raise click.BadOptionUsage(
                "model",
                "Invalid stop condition: {}, never and time_duration are not allowed with offline."
                .format(stop_condition))

    steps = graphwalker.offline(
        models=options["models"],
        start_element=options["start_element"],
        verbose=options["verbose"],
        unvisited=options["unvisited"],
        blocked=options["blocked"])

    steps = json.dumps(steps, sort_keys=True, indent=4)
    click.echo(steps, file=options["output_file"])


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.argument("steps_path", type=click.Path(exists=True, dir_okay=False))
@add_options([executor_option, url_option, report_path_option, report_file_option])
@handle_errors
def walk(test_package, steps_path, executor, url, report_path, report_file):
    """Run the tests from TEST_PACKAGE with steps from STEPS_PATH."""

    with open(steps_path) as f:
        steps = json.load(f)

    run_command(test_package, executor, url, steps=steps, report_path=report_path, report_file=report_file)


def run_tests(path, executor, url=None, models=None, steps=None, port=None, start_element=None,
              verbose=False, unvisited=False, blocked=False, **kargs):
    """Run tests.

    Args:
        path: Path to test code.
        executor: The type of executor to use.
        url: The url for the executor, if the executor type is ``http``.
        models: A sequence of tuples containing the ``model_path`` and the ``stop_condition``.
        steps: A sequence of steps.
        port: The port for the GraphWalker REST Service.
        verbose: Will run the GraphWalker command with the verbose flag.
        unvisited: Will run the GraphWalker command with the unvisited flag.
        blocked: Will run the GraphWalker command with the blocked flag.
    """

    report_file = kargs.get("report_file")
    report_path = kargs.get("report_path", False)

    planner = create_planner(models=models, steps=steps, port=port, start_element=start_element,
                             verbose=verbose, unvisited=unvisited, blocked=blocked)

    try:
        executor = create_executor(path, executor, url=url)
        try:
            reporter = create_reporters(report_path=report_path, report_file=report_file)
            walker = create_walker(planner, executor, reporter=reporter)
            walker.run()

            statistics = planner.get_statistics()
        finally:
            executor.kill()
    finally:
        planner.kill()

    return walker.status, statistics, reporter.report()


def run_command(path, executor, url=None, models=None, steps=None, port=None, start_element=None,
                verbose=False, unvisited=False, blocked=False, **kargs):
    """Run tests and echo output."""

    click.echo("Running:")
    status, statistics, report = run_tests(path, executor, url, models=models, steps=steps,
                                           port=port, start_element=start_element, verbose=verbose,
                                           unvisited=unvisited, blocked=blocked, **kargs)

    if statistics:
        echo_statistics(statistics)

    if report:
        click.echo()
        click.echo("Report:")
        click.echo(json.dumps(report, sort_keys=True, indent=4))

    echo_status(status)

    if not status:
        raise FailedTestsError()
