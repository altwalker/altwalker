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

    def step_end(self, step, result):
        """Report the result of the step execution.

        Args:
            step (:obj:`dict`): The step just executed.
            result (:obj:`dict`): The result of the step.
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

    def step_end(self, step, result):
        """Report the result of the step execution on all reporters.

        Args:
            step (:obj:`dict`): The step just executed.
            result (:obj:`dict`): The result of the step.
        """

        for reporter in self._reporters.values():
            reporter.step_end(step, result)

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

    def step_start(self, step):
        """Report the starting execution of a step.

        Args:
            step (:obj:`dict`): The step that will be executed next.
        """

        message = "{} Running".format(_format_step(step))
        message += _format_step_info(step)

        self._log(_add_timestamp(message))

    def step_end(self, step, result):
        """Report the result of the step execution.

        Args:
            step (:obj:`dict`): The step just executed.
            result (:obj:`dict`): The result of the step.
        """

        error = result.get("error")
        status = "FAIL" if error else "PASSED"
        message = "{} Status: {}\n".format(_format_step(step), status)

        output = result.get("output")
        if output:
            message += "Output:\n{}".format(output)

        if error:
            message += "\nError: {}\n".format(error["message"])

            if error.get("trace"):
                message += "\n{}\n".format(error["trace"])

        self._log(_add_timestamp(message))

    def error(self, step, message, trace=None):
        """Report an unexpected error.

        Args:
            step (:obj:`dict`): The step executed when the error occurred.
            message (:obj:`str`): The message of the error.
            trace (:obj:`str`): The traceback.
        """

        string = "Unexpected error ocurrent while running {}.\n".format(_format_step(step))
        string += "{}\n".format(message)

        if trace:
            string += "\n{}\n".format(trace)

        self._log(_add_timestamp(string))


class PrintReporter(_Formater):
    """This reporter outputs to stdout using the buildin :func:`print` function."""

    def _log(self, string):
        """Prints the string using the buildin :func:`print` function."""

        print(string)


class FileReporter(_Formater):
    """This reporter outputs to a file.

    Attributes:
        path (:obj:`str`): A path to a file to log the output.

    Note:
        If the path already exists the reporter will overwrite the content.
    """

    def __init__(self, path):
        self._path = path

        with open(self._path, "w+"):
            pass

    def _log(self, string):
        with open(self._path, "a") as fp:
            fp.write(string + "\n")


class ClickReporter(_Formater):
    """This reporter outputs using the :func:`click.echo` function."""

    def step_end(self, step, result):
        """Outputs a colored output for the result of the step execution.

        Args:
            step (:obj:`dict`): The step just executed.
            result (:obj:`dict`): The result of the step.
        """

        error = result.get("error")

        status = "FAIL" if error else "PASSED"
        status = click.style(status, fg="red" if error else "green")

        message = "{} Status: {}\n".format(_format_step(step), status)

        output = result.get("output")
        if output:
            message += "Output:\n{}".format(click.style(output, fg="cyan"))

        if error:
            message += "\nError: {}\n".format(click.style(error["message"], fg="red"))

            if error.get("trace"):
                message += "\n{}\n".format(click.style(error["trace"], fg="red"))

        self._log(_add_timestamp(message))

    def error(self, step, message, trace=None):
        """Outputs a colored output for an unexpected error.

        Args:
            step (:obj:`dict`): The step executed when the error occurred.
            message (:obj:`str`): The message of the error.
            trace (:obj:`str`): The traceback.
        """

        string = "Unexpected error ocurrent while running {}.\n".format(_format_step(step))
        string += "Error: {}\n".format(click.style(message, fg="red"))

        if trace:
            string += "\n{}\n".format(click.style(trace, fg="red"))

        self._log(_add_timestamp(string))

    def _log(self, string):
        """Prints the string using the :func:`click.echo` function."""

        click.echo(string)


class PathReporter(Reporter):
    """This reporter keeps a list of all execute steps (without fixtures)."""

    def __init__(self):
        self._path = []

    def step_end(self, step, result):
        """Save the step in a list, if the step is not a fixture."""

        if step.get("id"):
            self._path.append(step)

    def report(self):
        """Reutrn a list of all executed steps.

        Returns:
            list: Containing all executed steps.
        """

        return self._path


def create_reporters(report_file=None, report_path=False):
    """Create a reporter collection.

    Args:
        report_file: A file path. If set will add a ``FileReporter``.
        report_path: If set to true will add a ``PathReporter``.
    """

    reporting = Reporting()
    reporting.register("click", ClickReporter())

    if report_path:
        reporting.register("path", PathReporter())

    if report_file:
        reporting.register("file", FileReporter(report_file))

    return reporting
