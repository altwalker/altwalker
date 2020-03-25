"""A collection of util functions for the init command."""

import os

import click

from altwalker.exceptions import AltWalkerException
from altwalker.generate import init_project


def cli_init(dest_dir, model_paths=None, language=None, git=True):
    click.secho("Initiating a new project...\n", bold=True, fg="green")

    _, project_name = os.path.split(dest_dir)

    click.secho("  Name: {}".format(click.style(project_name, fg="yellow")))
    click.secho("  Language: {}".format(click.style(language if language else "none", fg="yellow")))
    click.secho("  Git: {}".format(click.style("yes" if git else "no", fg="yellow")))
    click.secho()

    try:
        init_project(dest_dir, model_paths=model_paths, language=language, git=git)
        click.secho("Successfully created project: {}.\n".format(project_name), fg="green")
    except FileExistsError as ex:
        raise AltWalkerException(str(ex))
