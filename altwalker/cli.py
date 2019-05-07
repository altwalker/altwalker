import json

import click

import altwalker.graphwalker as graphwalker
from altwalker.exceptions import FailedTestsError, handle_errors
from altwalker.model import check_models, verify_code
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import ClickReporter
from altwalker.init import init_project, generate_tests


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


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, "--version", "-v", prog_name="AltWalker")
def cli():
    """A command line tool for running model-based tests."""


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
    """Verify test code against the model(s)."""

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

    init_project(dest_dir, language, models, git)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False))
@add_options([model_file_option, language_option])
@handle_errors
def generate(dest_dir, models, language):
    """Generate test code template based on the given model(s)."""

    if language is None:
        language = "python"

    generate_tests(dest_dir, models, language)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--port", "-p", default=8887,
              help="Sets the port of the GraphWalker service.")
@add_options([model_and_generator_option, start_element_option,
              executor_option, url_option,
              verbose_option, unvisted_option, blocked_option])
@handle_errors
def online(test_package, **options):
    """Run a test path using the GraphWalker online RESTFUL service."""

    executor = options["executor"]
    url = options["url"]

    run_command(test_package, executor, url, models=options["models"],
                port=options["port"],
                verbose=options["verbose"],
                unvisited=options["unvisited"],
                blocked=options["blocked"])


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
@add_options([executor_option, url_option])
@handle_errors
def walk(test_package, steps_path, executor, url):
    """Run a test path."""

    with open(steps_path) as f:
        steps = json.load(f)

    run_command(test_package, executor, url, steps=steps)


def run_tests(path, executor, url=None, models=None, steps=None, port=None,
              verbose=False, unvisited=False, blocked=False):
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

    planner = create_planner(models=models, steps=steps, port=port,
                             verbose=verbose, unvisited=unvisited, blocked=blocked)

    try:
        executor = create_executor(path, executor, url=url)
        try:
            reporter = ClickReporter()

            walker = create_walker(planner, executor, reporter=reporter)
            walker.run()

            statistics = planner.get_statistics()
        finally:
            executor.kill()
    finally:
        planner.kill()

    return walker.status, statistics


def run_command(path, executor, url=None, models=None, steps=None, port=None,
                verbose=False, unvisited=False, blocked=False):
    """Run tests and echo output."""

    click.echo("Running:")
    status, statistics = run_tests(path, executor, url, models=models, steps=steps,
                                   port=port, verbose=verbose, unvisited=unvisited,
                                   blocked=blocked)

    click.echo("Statistics:")
    click.echo(json.dumps(statistics, sort_keys=True, indent=4))

    click.secho("Status: {}".format(status), fg="green" if status else "red")

    if not status:
        raise FailedTestsError()
