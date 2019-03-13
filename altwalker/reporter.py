import json
import datetime

import click


def _add_timestamp(string):
    return "[{}] {}".format(datetime.datetime.now(), string)


def _format_step(step):
    if step.get("modelName"):
        string = "{}.{}".format(step["modelName"], step["name"])
    else:
        string = "{}".format(step["name"])

    return string


def _format_step_info(step):
    string = ""

    if step.get("data"):
        data = json.dumps(step["data"], sort_keys=True, indent=4)
        string += "\nData:\n{}\n".format(data)

    if step.get("unvisitedElements"):
        unvisited_elements = json.dumps(step["unvisitedElements"], sort_keys=True, indent=4)
        string += "\nUnvisited Elements:\n{}\n".format(unvisited_elements)

    return string


class Reporter:
    """Default reporter."""

    def start(self, message=None):
        """Report the start of a run."""

    def end(self, message=None):
        """Report the end of a run."""

    def step_start(self, step):
        """Report the starting execution of a step."""

    def step_status(self, step, failure=False, output=""):
        """Report the status of a step."""

    def error(self, message, trace=None):
        """Report an error."""

    def _log(self, string):
        """Emmit the string."""


class Formater(Reporter):
    """Format the message for reporting."""

    def step_start(self, step):
        """Report the starting execution of a step."""

        message = "{} Running".format(_format_step(step))
        message += _format_step_info(step)

        self._log(_add_timestamp(message))

    def step_status(self, step, failure=False, output=""):
        """Report the status of a step."""

        status = "PASSED" if not failure else "FAIL"
        message = "{} Status: {}".format(_format_step(step), status)

        if output:
            message += "\nOutput:\n{}".format(output)

        self._log(_add_timestamp(message))

    def error(self, message, trace=None):
        """Report an error followed by the stack trace."""

        if trace:
            message += "\n{}".format(trace)

        self._log(_add_timestamp(message))


class PrintReporter(Formater):
    """Output reports to stdout."""

    def _log(self, string):
        print(string)


class FileReporter(Formater):
    """Output reports to a file."""

    def __init__(self, path):
        self.path = path

        with open(self.path, "w+"):
            pass

    def _log(self, string):
        with open(self.path, "a") as file:
            file.write(string + "\n")


class ClickReporter(Formater):
    """Output reports using the click.echo function."""

    def step_status(self, step, failure=False, output=""):
        status = "PASSED" if not failure else "FAIL"
        status = click.style(status, fg="red" if failure else "green")

        message = "{} Status: {}".format(_format_step(step), status)

        if output:
            output_string = click.style(output, fg="cyan")
            message += "\nOutput:\n{}".format(output_string)

        self._log(_add_timestamp(message))

    def error(self, message, trace=None):
        if trace:
            trace_string = click.style(trace, fg="red")
            message += "\n{}".format(trace_string)

        self._log(_add_timestamp(message))

    def _log(self, string):
        click.echo(string)
