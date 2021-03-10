import os
import re

import altwalker.graphwalker as graphwalker
from altwalker.exceptions import AltWalkerException
from altwalker.generate import init_project, generate_tests
from altwalker.model import _validate_models, get_models, validate_models
from altwalker.code import get_methods, get_missing_methods, _validate_code
from altwalker.planner import create_planner
from altwalker.executor import create_executor
from altwalker.walker import create_walker
from altwalker.reporter import create_reporters


def validate(model_paths, *args):
    """Check the model files for syntax errors."""

    models = get_models([model_path for model_path in model_paths if model_path.endswith(".json")])
    issues = _validate_models(models)

    return {
        "status": not any(issue for issue in issues.values()),
        "issues": issues
    }


def check(models, *args, blocked=False, **kwargs):
    """Check and analyze models for issues using the GraphWalker check command."""

    output = graphwalker.check(models, blocked=blocked)

    return {
        "status": output.startswith("No issues found with the model(s)"),
        "output": output
    }


def verify(test_package, model_paths, *args, executor_type=None, executor_url=None, **kwargs):
    """Verify and analyze test code for issues (missing classes or methods)."""

    validate_models(model_paths)
    methods = get_methods(model_paths)

    executor = create_executor(test_package, executor_type, url=executor_url)

    try:
        missing_methods = get_missing_methods(executor, methods)
        issues = _validate_code(executor, methods)
    finally:
        executor.kill()

    return {
        "status": not bool(missing_methods),
        "issues": issues,
        "methods": methods,
        "missing": missing_methods,
    }


def init(output_dir, *args, model_paths=None, language=None, git=True, **kwargs):
    """Initialize a new project."""

    init_project(output_dir, model_paths=model_paths, language=language, git=git)


def generate(output_dir, model_paths, *args, language=None, **kwargs):
    """Generate template code."""

    generate_tests(output_dir, model_paths, language=language)


def _normalize_stop_condition(stop_condition):
    """Normalize a stop condition for validation.

    Remove ``reached_vertex`` and ``reached_edge`` stop conditions because they may not pass
    the validation due to the element name (e.g. ``reached_vertex(v_never)``,
    ``reached_edge(v_timeduration)``).
    """

    result = stop_condition.lower().replace("_", "")
    result = re.sub(r'(reachedvertex|reachededge)\s*\(\s*[^\)]*\s*\)', '', result)

    return result


def _validate_stop_conditions(stop_conditions):
    """Validate stop conditions for the offline command.

    The ``never`` and ``time_duration`` stop conditions are not allowed in offline mode.
    """

    for stop_condition in stop_conditions:
        normalized_stop_condition = _normalize_stop_condition(stop_condition)

        if "never" in normalized_stop_condition or "timeduration" in normalized_stop_condition:
            raise AltWalkerException(
                "Invalid stop condition: '{}'. 'never' and 'time_duration' are not allowed in offline mode."
                .format(stop_condition))


def offline(models, *args, start_element=None, verbose=False, unvisited=False, blocked=False, **kwargs):
    """Generate a test sequence."""

    _validate_stop_conditions([stop_condition for _, stop_condition in models])

    steps = graphwalker.offline(
        models,
        start_element=start_element,
        verbose=verbose,
        unvisited=unvisited,
        blocked=blocked
    )

    return steps


def _run_tests(test_package, *args, executor_type=None, executor_url=None, models=None, steps=None,
               gw_host=None, gw_port=8887, start_element=None, verbose=False, unvisited=False, blocked=False,
               reporter=None, **kwargs):

    reporter = reporter or create_reporters()
    planner = None
    executor = None

    try:
        planner = create_planner(models=models, steps=steps, host=gw_host, port=gw_port, start_element=start_element,
                                 verbose=verbose, unvisited=unvisited, blocked=blocked)
        executor = create_executor(os.path.abspath(test_package), executor_type, url=executor_url)

        walker = create_walker(planner, executor, reporter=reporter)
        walker.run()
    finally:
        if planner is not None:
            planner.kill()

        if executor is not None:
            executor.kill()

    return {
        "status": walker.status,
        "report": reporter.report()
    }


def online(test_package, models, *args, executor_type=None, executor_url=None, gw_host=None, gw_port=8887,
           start_element=None, verbose=False, unvisited=False, blocked=False, reporter=None, **kwargs):
    """Generate and run a test sequence."""

    return _run_tests(test_package, *args, models=models, executor_type=executor_type, executor_url=executor_url,
                      gw_port=gw_port, gw_host=gw_host, start_element=None,
                      verbose=False, unvisited=False, blocked=False, reporter=reporter, **kwargs)


def walk(test_package, steps, *args, executor_type=None, executor_url=None, reporter=None, **kwargs):
    """Run a pre-generated test sequence."""

    return _run_tests(test_package, *args, steps=steps, executor_type=executor_type, executor_url=executor_url,
                      reporter=reporter, **kwargs)
