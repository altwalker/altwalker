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

import datetime
import json

import click

import altwalker._prettier as prettier
import altwalker._xml as xml


class Reporter:
    """The default reporter.

    This reporter does not emit any output. It is essentially a ‘no-op’ reporter for use.
    """

    def start(self, message=None):
        """Report the start of a run.

        Args:
            message (:obj:`str`): A message.
        """

    def end(self, message=None, statistics=None, status=None):
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
            raise ValueError(f"A reporter with the key: {key} is already registered.")

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

    def end(self, message=None, statistics=None, status=None):
        """Report the end of a run on all reporters.

        Args:
            message (:obj:`str`): A message.
        """

        for reporter in self._reporters.values():
            reporter.end(message=message, statistics=statistics, status=status)

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
        """Returns the reports from all registered reporters.

        Returns:
            dict: Containing all the reports from all the register reports.
        """

        result = {}

        for key, reporter in self._reporters.items():
            report = reporter.report()

            if report:
                result[key] = report

        return result


class ClickReporter(Reporter):
    """This reporter outputs using the :func:`click.echo` function."""

    def _timestamp(self):
        return click.style(str(datetime.datetime.now()), fg="bright_black", bold=True)

    def _add_timestamp(self, message):
        return f"[{self._timestamp()}] {message}"

    def _log(self, string):
        """Prints the string using the :func:`click.echo` function."""

        click.echo(string)

    def start(self, message=None):
        self._log("Running:\n")

    def end(self, message=None, statistics=None, status=None):
        self._log(prettier.format_statistics(statistics))
        self._log(prettier.format_run_status(status))

    def step_start(self, step):
        """Report the starting execution of a step.

        Args:
            step (:obj:`dict`): The step that will be executed next.
        """

        data = step.get("data")
        unvisited_elements = step.get("unvisitedElements")

        text = f"{prettier.format_step_name(step)} - {prettier.format_step_status(prettier.Status.RUNNING)}"

        if data:
            text += f"\n{prettier.format_data(step.get('data'), prefix='  ')}"

        if unvisited_elements:
            title = click.style("Unvisited Elements:", fg="bright_black", underline=True)
            text += f"\n{prettier.format_unvisited_elements(unvisited_elements, title=title, prefix='  ')}"

        self._log(self._add_timestamp(text))

    def step_end(self, step, step_result):
        """Report the result of the step execution.

        Args:
            step (:obj:`dict`): The step just executed.
            step_result (:obj:`dict`): The result of the step.
        """

        output = step_result.get("output")
        result = step_result.get("result")
        error = step_result.get("error")

        status = prettier.Status.FAILED if error else prettier.Status.PASSED

        text = f"{prettier.format_step_name(step)} - {prettier.format_step_status(status)}"

        if output:
            text += f"\n{prettier.format_output(output, prefix='  ')}\n"

        if result:
            text += f"\n{prettier.format_result(result, prefix='  ')}\n"

        if error:
            text += f"\n{prettier.format_error(error, prefix='  ')}\n"

        self._log(self._add_timestamp(text))

    def error(self, step, message, trace=None):
        """Report an unexpected error.

        Args:
            step (:obj:`dict`): The step executed when the error occurred.
            message (:obj:`str`): The message of the error.
            trace (:obj:`str`): The traceback.
        """

        if step:
            error_message = f"Unexpected error occurred while running {prettier.format_step_name(step)}."
        else:
            error_message = "Unexpected error occurred."

        message = f"{error_message}{prettier.format_error({'message': message, 'trace': trace}, prefix='  ')}"

        self._log(self._add_timestamp(message))


class FileReporter(ClickReporter):
    """This reporter outputs to a file.

    Args:
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
            click.echo(string, file=fp, color=False)


class PathReporter(Reporter):
    """This reporter keeps a list of all execute steps (without fixtures).

    Args:
        file (:obj:`str`): A path to a file to log execution path.
        verbose (:obj:`bool`): Will print more details to stdout.

    Note:
        If the path already exists the reporter will overwrite the content.

    """

    def __init__(self, file="path.json", verbose=False):
        self._file = file
        self._verbose = verbose

        self._path = []

    def step_end(self, step, step_result):
        """Save the step in a list, if the step is not a fixture."""

        if step.get("id"):
            self._path.append(step)

    def end(self, message=None, statistics=None, status=None):
        steps = json.dumps(self._path, sort_keys=True, indent=4)

        with open(self._file, "w") as fp:
            fp.write(steps)

        if self._verbose:
            click.secho(f"Execution path written to file: {click.style(self._file, fg='green')}.\n", bold=True)

    def report(self):
        """Return a list of all executed steps.

        Returns:
            list: Containing all executed steps.
        """

        return self._path


class JUnitXMLReporter(Reporter):
    """This reporter generates a JUnit style XML.

    Args:
        file (:obj:`str`): A path to a file to log execution path.
        prettyxml (:obj:`bool`): Will generate a pretty-printed version of the document.
        verbose (:obj:`bool`): Will print more details to stdout.

    """

    def __init__(self, file="report.xml", prettyxml=True, verbose=False):
        self._file = file
        self._verbose = verbose
        self._prettyxml = prettyxml

        self._generator = xml.JUnitGenerator()

    def start(self, message=None):
        self._generator.start()

    def end(self, message=None, statistics=None, status=None):
        self._generator.end(statistics=statistics)
        self._generator.write(filename=self._file)

        if self._verbose:
            click.secho(f"JUnit XML written to file: {click.style(self._file, fg='green')}.\n", bold=True)

    def step_start(self, step):
        self._generator.step_start()

    def step_end(self, step, result):
        self._generator.step_end(step, result)

    def error(self, step, message, trace=None):
        self._generator.error(step, message, trace=trace)

    def report(self):
        return self._generator.to_string()


def create_reporters(report_file=None, report_path=False, report_path_file=None,
                     report_xml=False, report_xml_file=None, verbose=True):
    """Create a reporter collection.

    Args:
        report_file (:obj:`str`): A file path. If set will add a ``FileReporter``.
        report_path (:obj:`bool`): If set to true will add a ``PathReporter``.
        report_path_file (:obj:`str`): If set will set the file for ``PathReporter``.
        report_xml (:obj:`bool`): If set to true will add a ``JUnitXMLReporter``.
        report_xml_file (:obj:`str`): If set will set the file for ``JUnitXMLReporter``.
        verbose (:obj:`bool`): If set some reporters will print more details to stdout.
    """

    reporting = Reporting()
    reporting.register("click", ClickReporter())

    if report_file:
        reporting.register("file", FileReporter(report_file))

    if report_xml or report_xml_file:
        reporting.register("junit", JUnitXMLReporter(file=report_xml_file or "report.xml", verbose=verbose))

    if report_path or report_path_file:
        reporting.register("path", PathReporter(file=report_path_file or "path.json", verbose=verbose))

    return reporting
