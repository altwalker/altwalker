#    Copyright(C) 2023 Altom Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

import functools
import logging

import click
from click._compat import get_text_stderr

logger = logging.getLogger(__name__)


class GraphWalkerException(Exception):
    """An internal exception that signals a GraphWalker error."""


class AltWalkerException(Exception):
    """An internal exception that signals a AltWalker error."""


class AltWalkerTypeError(AltWalkerException, TypeError):
    """An internal exception raised when an operation or function is applied to an object of inappropriate type or when
    passing arguments of the wrong type.
    """


class AltWalkerValueError(AltWalkerException, ValueError):
    """An internal exception raised when an operation or function receives an argument that has the right type but an
    inappropriate value.
    """


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

        click.secho("GraphWalker Error: ", file=file, bold=True, fg="red", nl=False)
        click.secho(f"{self.format_message()}\n", file=file, fg="red")


class AltWalkerError(click.ClickException):
    """An exception that handles the display of an AltWalker error in the command line."""

    exit_code = 4

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()

        click.secho("AltWalker Error: ", file=file, bold=True, fg="red", nl=False)
        click.secho(f"{self.format_message()}\n", file=file, fg="red")


def handle_errors(func):
    """Handle errors for the command line commands."""

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GraphWalkerException as error:
            raise GraphWalkerError(error)
        except AltWalkerException as error:
            raise AltWalkerError(error)
        except click.ClickException:
            raise
        except Exception as error:
            logger.exception(error)
            raise click.ClickException(error)

    return wrap
