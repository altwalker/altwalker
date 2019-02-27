import json
import os

import click

import altwalker.graphwalker as graphwalker
from altwalker.exceptions import FailedTestsError, handle_errors
from altwalker.model import check_models, verify_code
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import ClickReporter
from altwalker.init import init_repo, generate_tests


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

model_option = click.option("--model", "-m", "models", type=(click.Path(exists=True, dir_okay=False), str),
                            required=True, multiple=True,
                            help="The model, as a graphml/json file followed by generator with stop condition.")

start_element_option = click.option("--start-element", "-e",
                                    help="Sets the starting element in the first model.")

verbose_option = click.option("--verbose", "-o", default=False, is_flag=True,
                              help="Will also print the model data and the properties for each step.")

unvisted_option = click.option("--unvisited", "-u", default=False, is_flag=True,
                               help="Will also print the remaining unvisited elements in the model. Default is False")

blocked_option = click.option("--blocked", "-b", default=False, is_flag=True,
                              help="Will fiter out elements with the keyword BLOCKED. Default is False.")


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, "-v", "--version", prog_name="AltWalker")
def cli():
    """A command line tool for running model-based tests."""


@cli.command()
@add_options([model_option, blocked_option])
@handle_errors
def check(models, blocked):
    """Check and analyze model(s) for issues."""

    check_models(models, blocked=blocked)
    click.echo("No issues found with the model(s).")


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              required=True, multiple=True,
              help="The model, as a graphml/json file.")
@handle_errors
def verify(test_package, models):
    """Verify test code against the model(s)."""

    path, package = os.path.split(test_package)

    verify_code(path, package, models)
    click.echo("No issues found with the code.")


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False))
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              required=False, multiple=True,
              help="The model, as a graphml/json file.")
@click.option("--no-git", "-n", "no_git", default=False, is_flag=True,
              help="If set it will not initialize a git repository.")
@handle_errors
def init(dest_dir, models, no_git):
    """Initialize an AltWalker project."""

    init_repo(dest_dir, models, no_git)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False))
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              required=True, multiple=True,
              help="The model, as a graphml/json file.")
@handle_errors
def generate(dest_dir, models):
    """Generate test code template based on the given model(s)."""

    generate_tests(dest_dir, models)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--port", "-p", default=8887,
              help="Sets the port of the GraphWalker service.")
@add_options([model_option, start_element_option, verbose_option, unvisted_option, blocked_option])
@handle_errors
def online(test_package, **options):
    """Run a test path using the GraphWalker online RESTFUL service."""

    run_command(test_package, models=options["models"],
                port=options["port"],
                verbose=options["verbose"],
                unvisited=options["unvisited"],
                blocked=options["blocked"])


@cli.command()
@click.option("--output-file", "-f", type=click.File(mode="w", lazy=True, atomic=True),
              help="Output file.")
@add_options([model_option, start_element_option, verbose_option, unvisted_option, blocked_option])
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
@handle_errors
def walk(test_package, steps_path):
    """Run a test path."""

    with open(steps_path) as f:
        steps = json.load(f)

    run_command(test_package, steps=steps)


def run_tests(path, package, models=None, steps=None, port=None,
              verbose=False, unvisited=False, blocked=False):

    planner = create_planner(models=models, steps=steps, port=port,
                             verbose=verbose, unvisited=unvisited, blocked=blocked)

    try:
        executor = create_executor(path, package=package)
        reporter = ClickReporter()

        walker = create_walker(planner, executor, reporter=reporter)
        walker.run()

        statistics = planner.get_statistics()
    finally:
        if port:
            planner.kill()

    return walker.status, statistics


def run_command(test_package, models=None, steps=None, port=None,
                verbose=False, unvisited=False, blocked=False):
    """Run tests and echo output."""

    path, package = os.path.split(test_package)

    click.echo("Running:")
    status, statistics = run_tests(path, package, models=models, steps=steps,
                                   port=port, verbose=verbose, unvisited=unvisited,
                                   blocked=blocked)

    click.echo("Statistics:")
    click.echo(json.dumps(statistics, sort_keys=True, indent=4))

    click.secho("Status: {}".format(status), fg="green" if status else "red")

    if not status:
        raise FailedTestsError()
