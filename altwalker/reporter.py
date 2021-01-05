import json
import datetime
from enum import Enum

import click


class Status(Enum):
    RUNNING = "RUNNING..."
    PASSED = "PASSED"
    FAILED = "FAILED"

    def __str__(self):
        return self.value


class Reporter:
    """The default reporter.

    This reporter does not emit any output. It is essentially a ‘no-op’ reporter for use.
    """

    def start(self, message=None):
        """Report the start of a run.

        Args:
            message (:obj:`str`): A message.
        """

    def end(self, message=None):
        """Report the end of a run.

        Args:
            message (:obj:`str`): A message.
        """

    def step_start(self, step):
        """Report the starting execution of a step.

        Args:
            step (:obj:`dict`): The step that will be executed next.
        """

    def step_end(self, step, step_result):
        """Report the result of the step execution.

        Args:
            step (:obj:`dict`): The step just executed.
            step_result (:obj:`dict`): The result of the step.
        """

    def error(self, step, message, trace=None):
        """Report an unexpected error.

        Args:
            step (:obj:`dict`): The step executed when the error occurred.
            message (:obj:`str`): The message of the error.
            trace (:obj:`str`): The traceback.
        """

    def report(self):
        """Return an report for the run, or ``None`` if the reporter doesn't have a report.

        Returns:
            None: This reporter doesn't have a report.
        """

    def _log(self, string):
        """This method does nothing."""


class Reporting:
    """This reporter combines a list of reporters into a singe one, by delegating the calls to every
    reporter from it's list.
    """

    def __init__(self):
        self._reporters = {}

    def register(self, key, reporter):
        """Register a reporter.

        Args:
            key (:obj:`str`): A key to identify the reporter.
            reporter (:obj:`Reporter`): A reporter.

        Raises:
            ValueError: If a reporter with the same key is already registered.
        """

        if key in self._reporters:
            raise ValueError("A reporter with the key: {} is already registered.".format(key))

        self._reporters[key] = reporter

    def unregister(self, key):
        """Unregister a reporter.

        Args:
            key (:obj:`str`): A key of a registered reporter.

        Raises:
            KeyError: If no reporter with the given key was registered.
        """

        del self._reporters[key]

    def start(self, message=None):
        """Report the start of a run on all reporters.

        Args:
            message (:obj:`str`): A message.
        """

        for reporter in self._reporters.values():
            reporter.start(message=message)

    def end(self, message=None):
        """Report the end of a run on all reporters.

        Args:
            message (:obj:`str`): A message.
        """

        for reporter in self._reporters.values():
            reporter.end(message=message)

    def step_start(self, step):
        """Report the starting execution of a step on all reporters.

        Args:
            step (:obj:`dict`): The step that will be executed next.
        """

        for reporter in self._reporters.values():
            reporter.step_start(step)

    def step_end(self, step, step_result):
        """Report the result of the step execution on all reporters.

        Args:
            step (:obj:`dict`): The step just executed.
            step_result (:obj:`dict`): The result of the step.
        """

        for reporter in self._reporters.values():
            reporter.step_end(step, step_result)

    def error(self, step, message, trace=None):
        """Report an unexpected error on all reporters.

        Args:
            step (:obj:`dict`): The step executed when the error occurred.
            message (:obj:`str`): The message of the error.
            trace (:obj:`str`): The traceback.
        """

        for reporter in self._reporters.values():
            reporter.error(step, message, trace=trace)

    def report(self):
        """Returns the reports from all registerd reporters.

        Returns:
            dict: Containing all the reports from all the register reports.
        """

        result = {}

        for key, reporter in self._reporters.items():
            report = reporter.report()

            if report:
                result[key] = report

        return result


class _Formater(Reporter):
    """Format the message for reporting."""

    def _timestamp(self):
        return datetime.datetime.now()

    def _add_timestamp(self, message):
        return "[{timestamp}] {message}".format(timestamp=self._timestamp(), message=message)

    def _format_step_name(self, step):
        if step.get("modelName"):
            string = "{}.{}".format(step["modelName"], step["name"])
        else:
            string = "{}".format(step["name"])

        return string

    def _format_status(self, status):
        return str(status)

    def _format_data(self, data):
        if data:
            content = "\n".join(["  {}: {}".format(key, value) for key, value in data.items()])

            return "\nData:\n\n{}\n".format(content)

        return ""

    def _format_unvisited(self, unvisited):
        if unvisited:
            content = "\n".join(["  * {elementId} - {elementName}".format(**element) for element in unvisited])

            return "\nUnvisited Elements:\n\n{}\n".format(content)

        return ""

    def _format_output(self, output):
        if output:
            return "\nOutput:\n\n{}\n".format(output.strip(" \n"))

        return ""

    def _format_result(self, result):
        if result:
            content = json.dumps(result, sort_keys=True, indent=4)

            return "\nResult:\n\n{}\n".format(content)

        return ""

    def _format_error(self, error):
        if error:
            message = "\nError: {}\n".format(error["message"])

            if error.get("trace"):
                message += "\n{}\n".format(error["trace"])

            return message

    def step_start(self, step):
        """Report the starting execution of a step.

        Args:
            step (:obj:`dict`): The step that will be executed next.
        """

        message = "{step_name} - {status}{data}{unvisited}".format(
            status=self._format_status(Status.RUNNING),
            step_name=self._format_step_name(step),
            data=self._format_data(step.get("data")),
            unvisited=self._format_unvisited(step.get("unvisitedElements"))
        )

        self._log(self._add_timestamp(message))

    def step_end(self, step, step_result):
        """Report the result of the step execution.

        Args:
            step (:obj:`dict`): The step just executed.
            step_result (:obj:`dict`): The result of the step.
        """

        output = step_result.get("output")
        result = step_result.get("result")
        error = step_result.get("error")

        status = Status.FAILED if error else Status.PASSED

        message = "{step_name} - {status}{output}{result}{error}".format(
            status=self._format_status(status),
            step_name=self._format_step_name(step),
            output=self._format_output(output),
            result=self._format_result(result),
            error=self._format_error(error)
        )

        self._log(self._add_timestamp(message))

    def error(self, step, message, trace=None):
        """Report an unexpected error.

        Args:
            step (:obj:`dict`): The step executed when the error occurred.
            message (:obj:`str`): The message of the error.
            trace (:obj:`str`): The traceback.
        """

        if step:
            error_message = "Unexpected error occurred while running {}.".format(self._format_step_name(step))
        else:
            error_message = "Unexpected error occurred."

        message = "{message}{error}".format(
            message=error_message,
            error=self._format_error({"message": message, "trace": trace})
        )

        self._log(self._add_timestamp(message))


class PrintReporter(_Formater):
    """This reporter outputs to stdout using the buildin :func:`print` function."""

    def _log(self, string):
        """Prints the string using the buildin :func:`print` function."""

        print(string)


class FileReporter(_Formater):
    """This reporter outputs to a file.

    Attributes:
        file (:obj:`str`): A path to a file to log the output.

    Note:
        If the path already exists the reporter will overwrite the content.
    """

    def __init__(self, file):
        self._file = file

        with open(self._file, "w+"):
            pass

    def _log(self, string):
        with open(self._file, "a") as fp:
            fp.write(string + "\n")


class ClickReporter(_Formater):
    """This reporter outputs using the :func:`click.echo` function."""

    def _timestamp(self):
        return click.style(str(datetime.datetime.now()), fg="bright_black", bold=True)

    def _format_status(self, status):
        colors = {
            Status.RUNNING: "yellow",
            Status.PASSED: "green",
            Status.FAILED: "red"
        }

        return click.style(str(status), fg=colors.get(status, "white"), bold=True)

    def _format_data(self, data):
        if data:
            title = click.style("Data:",  fg="bright_black", underline=True)
            content = "\n".join([
                "  {}: {}".format(click.style(key, fg="yellow", bold=True), value) for key, value in data.items()
            ])

            return "\n{}\n\n{}\n".format(title, content)

        return ""

    def _format_unvisited(self, unvisited):
        if unvisited:
            title = click.style("Unvisited Elements:",  fg="bright_black", underline=True)
            content = "\n".join(["  * {elementId} - {elementName}".format(**element) for element in unvisited])

            return "\n{}\n\n{}\n".format(title, content)

        return ""

    def _format_output(self, output):
        if output:
            title = click.style("Output:",  fg="bright_black", underline=True)
            content = click.style(output.strip(" \n"), fg="cyan")

            return "\n{}\n\n{}\n".format(title, content)

        return ""

    def _format_result(self, result):
        if result:
            title = click.style("Result:",  fg="bright_black", underline=True)
            content = click.style(json.dumps(result, sort_keys=True, indent=4), fg="bright_magenta")

            return "\n{}\n\n{}\n".format(title, content)

        return ""

    def _format_error(self, error):
        if error:
            title = click.style("Error:", fg="bright_black", underline=True)
            content = click.style(error["message"], fg="red", bold=True)

            if error.get("trace"):
                content += "\n\n{}".format(click.style(error["trace"], fg="red"))

            return "\n{} {}\n".format(title, content)

        return ""

    def _log(self, string):
        """Prints the string using the :func:`click.echo` function."""

        click.echo(string)


class PathReporter(Reporter):
    """This reporter keeps a list of all execute steps (without fixtures)."""

    def __init__(self, file=None, stdout=False):
        self._file = file
        self._stdout = False if file else stdout

        self._path = []

    def step_end(self, step, step_result):
        """Save the step in a list, if the step is not a fixture."""

        if step.get("id"):
            self._path.append(step)

    def end(self, message=None):
        steps = json.dumps(self._path, sort_keys=True, indent=4)

        if self._file:
            with open(self._file, "w") as fp:
                fp.write(steps)
        elif self._stdout:
            click.secho("Steps:\n")
            click.secho(steps, fg="cyan")
            click.secho()

    def report(self):
        """Return a list of all executed steps.

        Returns:
            list: Containing all executed steps.
        """

        return self._path


def create_reporters(report_file=None, report_path=False, report_path_file=None):
    """Create a reporter collection.

    Args:
        report_file (:obj:`str`): A file path. If set will add a ``FileReporter``.
        report_path (:obj:`bool`): If set to true will add a ``PathReporter``.
        report_path_file (:obj:`str`): If set will set the file for ``PathReporter``.
    """

    reporting = Reporting()
    reporting.register("click", ClickReporter())

    if report_path:
        reporting.register("path", PathReporter(file=report_path_file, stdout=True))

    if report_file:
        reporting.register("file", FileReporter(report_file))

    return reporting
