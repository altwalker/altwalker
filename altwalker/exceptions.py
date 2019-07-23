import functools

import click
from click._compat import get_text_stderr


class GraphWalkerException(Exception):
    """An internal exception that signals a GraphWalker error."""


class AltWalkerException(Exception):
    """An internal exception that signals a AltWalker error."""


class ValidationException(AltWalkerException):
    """An internal exception that signals a model(s) or test code validation error."""


class ExecutorException(AltWalkerException):
    """An internal exception that signals a executor error."""


class FailedTestsError(click.ClickException):
    """An exception that handles the tests failure in the command line."""

    exit_code = 1

    def __init__(self):
        pass

    def show(self, file=None):
        pass


class GraphWalkerError(click.ClickException):
    """An exception that handles the display of an GraphWalker error in the command line."""

    exit_code = 3

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        click.secho("GraphWalker Error: {}".format(self.format_message()), file=file, fg="red")


class AltWalkerError(click.ClickException):
    """An exception that handles the display of an AltWalker error in the command line."""

    exit_code = 4

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()
        click.secho("AltWalker Error: {}".format(self.format_message()), file=file, fg="red")


def handle_errors(func):
    """Handle errors for the commnad line commands."""

    @functools.wraps(func)
    def wrap(*args, **kargs):
        try:
            func(*args, **kargs)
        except GraphWalkerException as error:
            raise GraphWalkerError(error)
        except AltWalkerException as error:
            raise AltWalkerError(error)
        except click.ClickException:
            raise
        except Exception as error:
            raise click.ClickException(error)

    return wrap
