"""A collection of util functions for the generate command."""

import click

from altwalker.exceptions import AltWalkerException
from altwalker.generate import generate_tests


def cli_generate(dest_dir, models, language=None):
    if not language:
        language = "python"

    click.secho("Generating tests...\n", bold=True, fg="green")

    click.secho("  Language: {}".format(click.style(language if language else "none", fg="yellow")))
    click.secho()

    try:
        generate_tests(dest_dir, models, language=language)
        click.secho("Successfully generate tests.\n", fg="green")
    except FileExistsError as ex:
        raise AltWalkerException(str(ex))
