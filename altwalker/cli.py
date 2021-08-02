import os
import warnings
import logging

import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand

from altwalker.generate import SUPPORTED_LANGUAGES
from altwalker.executor import SUPPORTED_EXECUTORS
from altwalker._cli import click_formatwarning, cli_init, cli_generate, cli_check, cli_verify, \
    cli_offline, cli_online, cli_walk


warnings.formatwarning = click_formatwarning  # replace the default warning formating
warnings.simplefilter("default")  # print the first occurrence of warnings


CONTEXT_SETTINGS = dict(help_option_names=["--help", "-h"])

# mark deprecated options with red in the help messages
HELP_OPTIONS_CUSTOM_COLORS = {
    "--url": "red",
    "--port": "red"
}


model_and_generator_option = click.option(
    "--model", "-m", "models", type=(click.Path(exists=True, dir_okay=False), str),
    required=True, multiple=True,
    help="The model as a graphml/json file followed by a generator with a stop condition.")

model_file_option = click.option(
    "--model", "-m", "model_paths", type=click.Path(exists=True, dir_okay=False),
    required=True, multiple=True,
    help="The model as a graphml/json file.")


start_element_option = click.option(
    "--start-element", "-e",
    help="Sets the starting element in the first model.")

verbose_option = click.option(
    "--verbose", "-o", default=False, show_default=True, is_flag=True,
    help="Will also print the model data and the properties for each step.")

unvisited_option = click.option(
    "--unvisited", "-u", default=False, show_default=True, is_flag=True,
    help="Will also print the remaining unvisited elements in the model.")

blocked_option = click.option(
    "--blocked", "-b", default=False, show_default=True, is_flag=True,
    help="Will filter out elements with the blocked property.")

language_option = click.option(
    "--language", "-l", type=click.Choice(SUPPORTED_LANGUAGES, case_sensitive=False),
    help="Configure the programming language of the tests.")

executor_option = click.option(
    "--executor", "-x", "--language", "-l", "executor_type",
    type=click.Choice(SUPPORTED_EXECUTORS, case_sensitive=False),
    default="python", show_default=True,
    help="Configure the executor to be used.")


url_option = click.option(
    "--url", help="This option is deprecated, use --executor-url instead. [deprecated]")

executor_url_option = click.option(
    "--executor-url", help="Sets the url for the executor.")


graphwalker_host_option = click.option(
    "--gw-host",
    help="Sets the host of the GraphWalker REST service.")

port_option = click.option(
    "--port", "-p", type=int,
    help="This option is deprecated, use --gw-port instead. [deprecated]")

graphwalker_port_option = click.option(
    "--gw-port", default=8887, show_default=True,
    help="Sets the port of the GraphWalker REST service.")


report_file_option = click.option(
    "--report-file", type=click.Path(exists=False, dir_okay=False),
    help="Save the report in a file.")

report_path_option = click.option(
    "--report-path", default=False, is_flag=True,
    help="Report the execution path and save it into a file (path.json by default).")

report_path_file_option = click.option(
    "--report-path-file", type=click.Path(exists=False, dir_okay=False),
    help="Set the report path file.")

report_xml_option = click.option(
    "--report-xml", default=False, is_flag=True,
    help="Report the execution path and save it into a file (report.xml by default).")

report_xml_file_option = click.option(
    "--report-xml-file", type=click.Path(exists=False, dir_okay=False),
    help="Set the xml report file.")


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group(
    context_settings=CONTEXT_SETTINGS,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green')
@click.version_option(None, "--version", "-v", prog_name="AltWalker")
@click.option("--log-level",
              type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], case_sensitive=False),
              default="CRITICAL", show_default=True, envvar="ALTWALKER_LOG_LEVEL",
              help="Sets the AltWalker logger level to the specified level.")
@click.option("--log-file", type=click.Path(exists=False, dir_okay=False), envvar="ALTWALKER_LOG_FILE",
              help="Sends logging output to a file.")
@click.option("--graphwalker-log-level",
              type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"], case_sensitive=False),
              default="CRITICAL", show_default=True, envvar="GRAPHWALKER_LOG_LEVEL",
              help="Sets the GraphWalker logger level to the specified level.")
def cli(log_level, log_file, graphwalker_log_level):
    """A command line tool for running Model-Based Tests."""

    os.environ["GRAPHWALKER_LOG_LEVEL"] = graphwalker_log_level.upper()
    logging.basicConfig(filename=log_file, level=log_level.upper())


@cli.command(
    cls=HelpColorsCommand,
    help_options_custom_colors=HELP_OPTIONS_CUSTOM_COLORS)
@add_options([model_and_generator_option, blocked_option])
def check(models, blocked):
    """Check and analyze models for issues."""

    status = cli_check(models, blocked=blocked)

    if not status:
        exit(4)


@cli.command(
    cls=HelpColorsCommand,
    help_options_custom_colors=HELP_OPTIONS_CUSTOM_COLORS)
@click.argument("test_package", type=click.Path(exists=True))
@click.option("--suggestions/--no-suggestions", "suggestions", default=True, is_flag=True,
              help="If set will print code suggestions for missing elements.", show_default=True)
@add_options([model_file_option, executor_option, url_option, executor_url_option])
def verify(test_package, model_paths, **options):
    """Verify and analyze test code for issues."""

    if options["url"]:
        warnings.warn("The --url option is deprecated, use --executor-url instead.", DeprecationWarning)

    options["executor_url"] = options["url"] or options["executor_url"]

    status = cli_verify(
        test_package, model_paths,
        executor_type=options["executor_type"], executor_url=options["executor_url"],
        suggestions=options["suggestions"])

    if not status:
        exit(4)


@cli.command(
    cls=HelpColorsCommand,
    help_options_custom_colors=HELP_OPTIONS_CUSTOM_COLORS)
@click.argument("output_dir", type=click.Path(exists=False, file_okay=False))
@click.option("--model", "-m", "model_paths", type=click.Path(exists=True, dir_okay=False),
              required=False, multiple=True,
              help="The model, as a graphml/json file.")
@click.option("--git/--no-git", " /-n", "git", default=True, is_flag=True,
              help="If set to true will initialize a git repository.", show_default=True)
@add_options([language_option])
def init(output_dir, model_paths, git, language):
    """Initialize a new project."""

    cli_init(output_dir, model_paths=model_paths, language=language, git=git)


@cli.command()
@click.argument("output_dir", default="tests", type=click.Path(exists=False))
@add_options([model_file_option, language_option])
def generate(output_dir, model_paths, language):
    """Generate template code based on the models."""

    cli_generate(output_dir, model_paths, language=language)


@cli.command(
    cls=HelpColorsCommand,
    help_options_custom_colors=HELP_OPTIONS_CUSTOM_COLORS)
@click.argument("test_package", type=click.Path(exists=True))
@add_options([graphwalker_host_option, port_option, graphwalker_port_option,
              model_and_generator_option, start_element_option, executor_option, url_option, executor_url_option,
              verbose_option, unvisited_option, blocked_option,
              report_path_option, report_path_file_option, report_file_option,
              report_xml_option, report_xml_file_option])
def online(test_package, models, **options):
    """Generate and run a test path."""

    if options["port"]:
        warnings.warn("The --port/-p option is deprecated, use --gw-port instead.", DeprecationWarning)

    options["gw_port"] = options["port"] or options["gw_port"]

    if options["url"]:
        warnings.warn("The --url option is deprecated, use --executor-url instead.", DeprecationWarning)

    options["executor_url"] = options["url"] or options["executor_url"]

    cli_online(
        test_package, models, executor_type=options["executor_type"], executor_url=options["executor_url"],
        gw_host=options["gw_host"], gw_port=options["gw_port"], start_element=options["start_element"],
        verbose=options["verbose"], unvisited=options["unvisited"], blocked=options["blocked"],
        report_file=options["report_file"], report_path=options["report_path"],
        report_path_file=options["report_path_file"], report_xml=options["report_xml"],
        report_xml_file=options["report_xml_file"])


@cli.command(
    cls=HelpColorsCommand,
    help_options_custom_colors=HELP_OPTIONS_CUSTOM_COLORS)
@click.option("--output-file", "-f", type=click.File(mode="w", lazy=True, atomic=True),
              help="Output file.")
@add_options([model_and_generator_option, start_element_option, verbose_option, unvisited_option, blocked_option])
def offline(models, **options):
    """Generate a test path."""

    cli_offline(models, **options)


@cli.command(
    cls=HelpColorsCommand,
    help_options_custom_colors=HELP_OPTIONS_CUSTOM_COLORS)
@click.argument("test_package", type=click.Path(exists=True))
@click.argument("steps_file", type=click.Path(exists=True, dir_okay=False))
@add_options([executor_option, url_option, executor_url_option,
              report_path_option, report_path_file_option, report_file_option,
              report_xml_option, report_xml_file_option])
def walk(test_package, steps_file, executor_type, url, executor_url, **options):
    """Run the tests with steps from a file."""

    if url:
        warnings.warn("The --url option is deprecated, use --executor-url instead.", DeprecationWarning)

    executor_url = url or executor_url

    cli_walk(test_package, steps_file, executor_type=executor_type, executor_url=executor_url, **options)
