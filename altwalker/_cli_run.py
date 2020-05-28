"""A collection of util functions for the online and walk commands."""

import os
import json

import click

from altwalker.exceptions import FailedTestsError
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import create_reporters


def _percentege_color(percentage):
    if percentage < 50:
        return "red"

    if percentage < 80:
        return "yellow"

    return "green"


def _style_percentage(percentege):
    return click.style("{}%".format(percentege), fg=_percentege_color(percentege))


def _style_fail(number):
    color = "red" if number > 0 else "green"

    return click.style(str(number), fg=color)


def _echo_stat(title, value, indent=2):
    title = " " * indent + title.ljust(30, ".")
    value = str(value).rjust(15, ".")

    click.echo(title + value)


def _echo_statistics(statistics):
    """Pretty-print statistics."""

    click.echo("Statistics:")
    click.echo()

    total_models = statistics["totalNumberOfModels"]
    completed_models = statistics["totalCompletedNumberOfModels"]
    model_coverage = _style_percentage(completed_models * 100 // total_models)

    _echo_stat("Model Coverage", model_coverage)
    _echo_stat("Number of Models", click.style(str(total_models), fg="white"))
    _echo_stat("Completed Models", click.style(str(completed_models), fg="white"))

    _echo_stat("Failed Models", _style_fail(statistics["totalFailedNumberOfModels"]))
    _echo_stat("Incomplete Models", _style_fail(statistics["totalIncompleteNumberOfModels"]))
    _echo_stat("Not Executed Models", _style_fail(statistics["totalNotExecutedNumberOfModels"]))
    click.echo()

    edge_coverage = _style_percentage(statistics["edgeCoverage"])
    _echo_stat("Edge Coverage", edge_coverage)

    total_edges = statistics["totalNumberOfEdges"]
    _echo_stat("Number of Edges", click.style(str(total_edges), fg="white"))
    _echo_stat("Visited Edges", click.style(str(statistics["totalNumberOfVisitedEdges"]), fg="white"))
    _echo_stat("Unvisited Edges", click.style(str(statistics["totalNumberOfUnvisitedEdges"]), fg="white"))
    click.echo()

    vertex_coverage = _style_percentage(statistics["vertexCoverage"])
    _echo_stat("Vertex Coverage", vertex_coverage)

    total_vertices = statistics["totalNumberOfVertices"]
    _echo_stat("Number of Vertices", click.style(str(total_vertices), fg="white"))
    _echo_stat("Visited Vertices", click.style(str(statistics["totalNumberOfVisitedVertices"]), fg="white"))
    _echo_stat("Unvisited Vertices", click.style(str(statistics["totalNumberOfUnvisitedVertices"]), fg="white"))
    click.echo()


def _echo_status(status):
    """Pretty-print status."""

    status_message = "PASS" if status else "FAIL"

    click.echo("Status: ", nl=False)
    click.secho(" {} ".format(status_message), bg="green" if status else "red")
    click.echo()


def run_tests(path, executor_type, url=None, models=None, steps=None, port=8887, start_element=None,
              verbose=False, unvisited=False, blocked=False, host=None, **kwargs):
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

    planner = None
    executor = None
    statistics = {}

    try:
        planner = create_planner(models=models, steps=steps, port=port, start_element=start_element,
                                 verbose=verbose, unvisited=unvisited, blocked=blocked, host=host)
        executor = create_executor(os.path.abspath(path), executor_type, url=url)
        reporter = create_reporters(**kwargs)
        walker = create_walker(planner, executor, reporter=reporter)
        walker.run()

        statistics = planner.get_statistics()
    finally:
        if planner:
            planner.kill()

        if executor:
            executor.kill()

    return walker.status, statistics, reporter.report()


def cli_run(path, executor_type, url="http://localhost:5000/", models=None, steps=None, port=None, start_element=None,
            verbose=False, unvisited=False, blocked=False, **kwargs):
    """Run tests and echo the output."""

    kwargs["report_path"] = kwargs.get("report_path", False) or bool(kwargs.get("report_path_file"))

    click.echo("Running:")
    status, statistics, _ = run_tests(path, executor_type, url=url, models=models, steps=steps,
                                      port=port, start_element=start_element, verbose=verbose,
                                      unvisited=unvisited, blocked=blocked, **kwargs)

    if statistics:
        _echo_statistics(statistics)

    _echo_status(status)

    if not status:
        raise FailedTestsError()


def cli_online(test_package, executor_type, url="http://localhost:5000/", models=None, port=None, start_element=None,
               verbose=False, unvisited=False, blocked=False, host=None, report_file=None,
               report_path=False, report_path_file=None):

    cli_run(
        test_package,
        executor_type,
        url=url,
        models=models,
        port=port,
        start_element=start_element,
        verbose=verbose, unvisited=unvisited, blocked=blocked,
        host=host,
        report_path=report_path,
        report_path_file=report_path_file, report_file=report_file
    )


def cli_walk(test_package, executor_type, steps_file, url="http://localhost:5000/", report_file=None,
             report_path=False, report_path_file=None):

    with open(steps_file) as fp:
        steps = json.load(fp)

    cli_run(test_package, executor_type, url=url, steps=steps, report_path=report_path,
            report_path_file=report_path_file, report_file=report_file)
