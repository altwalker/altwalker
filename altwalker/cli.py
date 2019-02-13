import json
import os

import click

import altwalker.graphwalker as graphwalker
from altwalker.model import check_models, verify_code
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import ClickReporter
from altwalker.init import init_repo, generate_tests


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.option("--model", "-m", "models", type=(click.Path(exists=True, dir_okay=False), str),
              required=True, multiple=True,
              help="The model, as a graphml/json file followed by generator with stop condition.")
@click.option("--blocked", "-b", default=False, is_flag=True)
def check(models, blocked):
    """Check and analyze model(s) for issues."""

    try:
        check_models(models, blocked=blocked)
        click.echo("No issues found with the model(s).")
    except Exception as error:
        raise click.UsageError(error)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True), nargs=1, required=True)
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              nargs=1, required=False, multiple=True,
              help="The model, as a graphml/json file.")
def verify(test_package, models):
    """Verify test code against the model(s)."""

    path, package = os.path.split(test_package)

    try:
        verify_code(path, package, models)
        click.echo("No issues found with the code.")
    except Exception as error:
        raise click.ClickException(error)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False), nargs=1, required=True)
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              nargs=1, required=False, multiple=True,
              help="The model, as a graphml/json file.")
@click.option("--no-git", "-n", "no_git", default=False, is_flag=True,
              help="If set it will not initialize a git repository.")
def init(dest_dir, models, no_git):
    """Initiate an AltWalker project."""

    try:
        init_repo(dest_dir, models, no_git)
    except Exception as error:
        raise click.ClickException(error)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False), nargs=1, required=True)
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              nargs=1, required=False, multiple=True,
              help="The model, as a graphml/json file.")
def generate(dest_dir, models):
    """Generate a template for the test code based on the given model(s)."""

    try:
        generate_tests(dest_dir, models)
    except Exception as error:
        raise click.ClickException(error)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True), nargs=1, required=False)
@click.option("--port", "-p", default=8887, nargs=1,
              help="Sets the port of the GraphWalker service.")
@click.option("--model", "-m", "models", type=(click.Path(exists=True, dir_okay=False), str),
              required=True, multiple=True,
              help="The model, as a graphml/json file followed by generator with stop condition.")
@click.option("--start-element", "-e", "start_element", default="", nargs=1,
              help="Sets the starting element in the first model.")
@click.option("--verbose", "-o", default=False, is_flag=True)
@click.option("--unvisited", "-u", default=False, is_flag=True,
              help="Will also print the remaining unvisited elements in the model. Default is false")
@click.option("--blocked", "-b", default=False, is_flag=True,
              help="Will fiter out elements with the keyword BLOCKED. Default is false.")
def online(test_package, **options):
    """Run a test path using the GraphWalker online RESTFUL service."""

    path, package = os.path.split(test_package)

    try:
        click.echo("Running:")
        status, statistics = run_tests(path, package, models=options["models"], port=options["port"])

        click.echo("Statistics:")
        click.echo(json.dumps(statistics, sort_keys=True, indent=4))

        click.secho("Status: {}".format(status), fg="green" if status else "red")
    except Exception as error:
        raise click.ClickException(error)


@cli.command()
@click.option("--output-file", "-f", type=click.File(mode="w", lazy=True, atomic=True),
              help="Output file.")
@click.option("--model", "-m", type=(click.Path(exists=True, dir_okay=False), str),
              required=True, multiple=True,
              help="The model, as a graphml/json file followed by generator with stop condition.")
@click.option("--start-element", "-e", default="", nargs=1,
              help="Sets the starting element in the first model.")
@click.option("--verbose", "-o", default=False, is_flag=True,
              help="Will also print data and properties. Default is false.")
@click.option("--unvisited", "-u", default=False, is_flag=True,
              help="Will also print the remaining unvisited elements in the model. Default is false.")
@click.option("--blocked", "-b", default=False, is_flag=True,
              help="Will fiter out elements with the keyword BLOCKED. Default is false.")
def offline(**options):
    """Generate a test path once, that can be later run."""

    for _, stop_condition in options["model"]:
        if "never" in stop_condition:
            raise click.BadOptionUsage(
                "model",
                "Invalid stop condition: {}, never is not allowed with offline.".format(stop_condition))

    try:
        steps = graphwalker.offline(
            models=options["model"],
            start_element=options["start_element"],
            verbose=options["verbose"],
            unvisited=options["unvisited"],
            blocked=options["blocked"])

        steps = json.dumps(steps, sort_keys=True, indent=4)
        click.echo(steps, file=options["output_file"])
    except Exception as error:
        raise click.ClickException(error)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True), nargs=1, required=True)
@click.argument("steps_path", type=click.Path(exists=True, dir_okay=False),
                nargs=1, required=True)
def walk(test_package, steps_path):
    """Run an test path."""

    path, package = os.path.split(test_package)

    with open(steps_path) as f:
        steps = json.load(f)

    try:
        click.echo("Running:")
        status, statistics = run_tests(path, package, steps=steps)

        click.echo("Statistics:")
        click.echo(json.dumps(statistics, sort_keys=True, indent=4))

        click.secho("Status: {}".format(status), fg="green" if status else "red")
    except Exception as error:
        raise click.ClickException(error)


def run_tests(path, package, models=None, steps=None, port=None):
    try:
        planner = create_planner(models=models, steps=steps, port=port)
        executor = create_executor(path, package=package)
        reporter = ClickReporter()

        walker = create_walker(planner, executor, reporter=reporter)
        walker.run()

        statistics = planner.get_statistics()
    finally:
        if port:
            planner.kill()

    return walker.status, statistics
