import os
import warnings
import logging

import click

from altwalker._utils import click_formatwarning
from altwalker._cli_check import cli_check
from altwalker._cli_verify import cli_verify
from altwalker._cli_init import cli_init
from altwalker._cli_generate import cli_generate
from altwalker._cli_offline import cli_offline
from altwalker._cli_run import cli_online, cli_walk
from altwalker.exceptions import handle_errors
from altwalker.generate import SUPPORTED_LANGUAGES
from altwalker.executor import SUPPORTED_EXECUTORS


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

language_option = click.option("--language", "-l", type=click.Choice(SUPPORTED_LANGUAGES, case_sensitive=False),
                               help="The programming language of the tests.")

executor_option = click.option("--executor", "-x", "--language", "-l", "executor_type",
                               type=click.Choice(SUPPORTED_EXECUTORS, case_sensitive=False),
                               default="python", show_default=True,
                               help="Configure the executor to be used.")

url_option = click.option("--url", default="http://localhost:5000/", show_default=True,
                          help="The url for the executor.")


report_file_option = click.option("--report-file", type=click.Path(exists=False, dir_okay=False),
                                  help="Save the report in a file.")

report_path_option = click.option("--report-path", default=False, is_flag=True,
                                  help="Report the execution path.")

report_path_file_option = click.option("--report-path-file", type=click.Path(exists=False, dir_okay=False),
                                       help="Report the execution path to a file.")


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(None, "--version", "-v", prog_name="AltWalker")
@click.option("--log-level",
              type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], case_sensitive=False),
              default="CRITICAL", show_default=True, envvar="ALTWALKER_LOG_LEVEL",
              help="Sets the logger level to the specified level.")
@click.option("--log-file", type=click.Path(exists=False, dir_okay=False), envvar="ALTWALKER_LOG_FILE",
              help="Sends logging output to a file.")
@click.option("--graphwalker-log-level",
              type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], case_sensitive=False),
              default="CRITICAL", show_default=True, envvar="GRAPHWALKER_LOG_LEVEL",
              help="Sets the GraphWalker logger level to the specified level.")
def cli(log_level, log_file, graphwalker_log_level):
    """A command line tool for running model-based tests."""

    os.environ["GRAPHWALKER_LOG_LEVEL"] = graphwalker_log_level.upper()
    logging.basicConfig(filename=log_file, level=log_level.upper())


@cli.command()
@add_options([model_and_generator_option, blocked_option])
@handle_errors
def check(models, blocked):
    """Check and analyze model(s) for issues."""

    status = cli_check(models, blocked=blocked)

    if status:
        exit(0)
    else:
        exit(4)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--suggestions/--no-suggestions", "suggestions", default=True, is_flag=True,
              help="If set will print code suggestions for missing steps.", show_default=True)
@add_options([model_file_option, executor_option, url_option])
@handle_errors
def verify(test_package, executor_type, models, **options):
    """Verify and analyze test code against model(s)."""

    status = cli_verify(test_package, executor_type, models, **options)

    if status:
        exit(0)
    else:
        exit(4)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False, file_okay=False))
@click.option("--model", "-m", "models", type=click.Path(exists=True, dir_okay=False),
              required=False, multiple=True,
              help="The model, as a graphml/json file.")
@click.option("--git/--no-git", " /-n", "git", default=True, is_flag=True,
              help="If set to true will initialize a git repository.", show_default=True)
@add_options([language_option])
@handle_errors
def init(dest_dir, models, git, language):
    """Initialize a new project."""

    cli_init(dest_dir, model_paths=models, language=language, git=git)


@cli.command()
@click.argument("dest_dir", type=click.Path(exists=False))
@add_options([model_file_option, language_option])
@handle_errors
def generate(dest_dir, models, language):
    """Generate test code template based on the given model(s)."""

    cli_generate(dest_dir, models, language=language)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--port", "-p", default=8887,
              help="Sets the port of the GraphWalker service.")
@add_options([model_and_generator_option, start_element_option, executor_option, url_option,
              verbose_option, unvisted_option, blocked_option, report_path_option, report_path_file_option,
              report_file_option])
@handle_errors
def online(test_package, executor_type, **options):
    """Generate and run a test path."""

    cli_online(test_package, executor_type, **options)


@cli.command()
@click.option("--output-file", "-f", type=click.File(mode="w", lazy=True, atomic=True),
              help="Output file.")
@add_options([model_and_generator_option, start_element_option, verbose_option, unvisted_option, blocked_option])
@handle_errors
def offline(models, **options):
    """Generate a test path once, that can be runned later."""

    cli_offline(models, **options)


@cli.command()
@click.argument("test_package", type=click.Path(exists=True))
@click.argument("steps_file", type=click.Path(exists=True, dir_okay=False))
@add_options([executor_option, url_option, report_path_option, report_path_file_option, report_file_option])
@handle_errors
def walk(test_package, steps_file, executor_type, url, report_path, report_path_file, report_file):
    """Run the tests with steps from a file."""

    cli_walk(test_package, executor_type, steps_file, url=url, report_path=report_path,
             report_path_file=report_path_file, report_file=report_file)
