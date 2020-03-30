"""A collection of util functions for the offline command."""

import re
import json

import click

import altwalker.graphwalker as graphwalker
from altwalker.exceptions import AltWalkerException


def _normalize_stop_condition(stop_condition):
    result = stop_condition.lower().replace("_", "")
    result = re.sub(r'(reachedvertex|reachededge)\s*\(\s*[^\)]*\s*\)', '', result)

    return result


def _validate_models(models):
    """Validate models for the offline commands."""

    for _, stop_condition in models:
        normalized_stop_condition = _normalize_stop_condition(stop_condition)

        if "never" in normalized_stop_condition or "timeduration" in normalized_stop_condition:
            raise AltWalkerException(
                "Invalid stop condition: '{}'. 'never' and 'time_duration' are not allowed with offline."
                .format(stop_condition))


def cli_offline(models, output_file=None, start_element=None, verbose=False, unvisited=False, blocked=False):

    _validate_models(models)

    steps = graphwalker.offline(
        models=models,
        start_element=start_element,
        verbose=verbose,
        unvisited=unvisited,
        blocked=blocked
    )

    steps = json.dumps(steps, sort_keys=True, indent=4)
    click.echo(steps, file=output_file)
