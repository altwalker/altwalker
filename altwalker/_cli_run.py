"""A collection of util functions for the online and walk commands."""

import os
import json

from altwalker.exceptions import FailedTestsError
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import create_reporters


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

    status, statistics, _ = run_tests(path, executor_type, url=url, models=models, steps=steps,
                                      port=port, start_element=start_element, verbose=verbose,
                                      unvisited=unvisited, blocked=blocked, **kwargs)

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
