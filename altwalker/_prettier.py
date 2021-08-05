"""A collection of classes and methods that convert data into “pretty” strings for the CLI."""

import json
import shutil
import textwrap
from collections import defaultdict
from enum import Enum

import click


class Status(Enum):
    RUNNING = "RUNNING..."
    PASSED = "PASSED"
    FAILED = "FAILED"

    def __str__(self):
        return self.value


class NumberFormatter:
    """Formats a ``int`` into a “pretty” string."""

    @staticmethod
    def format_coverage(percentage):
        color = "green"

        if percentage < 80:
            color = "yellow"

        if percentage < 50:
            color = "red"

        return click.style("{}%".format(percentage), fg=color, bold=True)

    @staticmethod
    def format_passed(number):
        color = "red" if number == 0 else "green"

        return click.style(str(number), fg=color, bold=True)

    @staticmethod
    def format_unvisited(number):
        color = "yellow" if number > 0 else "green"

        return click.style(str(number), fg=color, bold=True)

    @staticmethod
    def format_failed(number):
        color = "red" if number > 0 else "green"

        return click.style(str(number), fg=color, bold=True)

    @staticmethod
    def format_number(number):
        return click.style(str(number), fg="white", bold=True)

    @classmethod
    def format(cls, number, style=None):
        formatters_map = {
            "COVERAGE": cls.format_coverage,
            "PASSED": cls.format_passed,
            "UNVISITED": cls.format_unvisited,
            "FAILED": cls.format_failed
        }

        formatter = formatters_map.get(style, cls.format_number)
        return formatter(number)


class TableFormatter:
    """Formats a ``list`` of pairs into a “pretty” string."""

    @staticmethod
    def _format_row(key, value, fillchar=None):
        fillchar = fillchar or "."

        key = key.ljust(30, fillchar)
        value = str(value).rjust(30, fillchar)

        return "{}{}\n".format(key, value)

    @classmethod
    def format(cls, items, prefix=None, fillchar=None):
        if not items:
            return ""

        text = ""
        prefix = prefix or ""

        for key, value in items:
            text += cls._format_row(key, value, fillchar=fillchar)

        return textwrap.indent(text, prefix=prefix) + "\n"


class UnvisitedElementsFormatter:
    """Formats a list of unvisited elements ``list`` into a “pretty” string.

    Made for the ``verticesNotVisited``, ``edgesNotVisited`` and ``unvisitedElements``
    returned by the GraphWalker REST API.
    """

    @staticmethod
    def _format_element(element):
        element_id = element.get("vertexId") or element.get("edgeId") or element.get("elementId")
        model_name = element.get("modelName")
        element_name = element.get("vertexName") or element.get("edgeName") or element.get("elementName")

        if model_name:
            return click.style("{} - {}.{}".format(element_id, model_name, element_name), fg="yellow")
        else:
            return click.style("{} - {}".format(element_id, element_name), fg="yellow")

    @classmethod
    def _normalize_elements(cls, elements):
        return [cls._format_element(element) for element in elements]

    @classmethod
    def format(cls, elements, title=None, prefix=None):
        if not elements:
            return ""

        return format_unordered_list(cls._normalize_elements(elements), title=title, prefix=prefix)


class RequirementsFormatter:
    """Formats a requirement ``list`` into a “pretty” string.

    Made for ``requirementsPassed``, ``requirementsNotCovered`` and ``requirementsFailed``
    returned by the GraphWalker API.
    """

    @staticmethod
    def _normalize_requirement(requirement):
        return {
            "modelName": requirement.get("modelName"),
            "key": requirement.get("RequirementKey") or requirement.get("requirementKey")
        }

    @classmethod
    def _normalize_requirements(self, requirements):
        return [self._normalize_requirement(requirement) for requirement in requirements]

    @staticmethod
    def _group_requirements(requirements):
        result = defaultdict(set)

        for requirement in requirements:
            result[requirement["modelName"]].add(requirement["key"])

        return result

    @classmethod
    def format(cls, requirements, title=None, prefix=None, color=None):
        if not requirements:
            return ""

        requirements = cls._normalize_requirements(requirements)
        requirements = cls._group_requirements(requirements)

        items = [
            format_inline_list([click.style(key, fg=color) for key in keys], title=title)
            for title, keys in requirements.items()
        ]

        return format_unordered_list(items, title=title, prefix=prefix)


class StatisticsFormatter:
    """Formats a run statistics into a “pretty” string.

    Made for the ``statistics`` returned by the GraphWalker API.
    """

    @staticmethod
    def _get_models_coverage(statistics):
        number_of_models = statistics["totalNumberOfModels"]
        number_of_completed_models = statistics["totalCompletedNumberOfModels"]

        return number_of_completed_models * 100 // number_of_models

    @classmethod
    def _normalize_statistics(cls, statistics):
        statistics["modelCoverage"] = cls._get_models_coverage(statistics)
        return statistics

    @staticmethod
    def _format_models_table(statistics):
        return format_table([
            ("Model Coverage", format_number(statistics["modelCoverage"], style="COVERAGE")),
            ("Number of Models", format_number(statistics["totalNumberOfModels"])),
            ("Completed Models", format_number(statistics["totalCompletedNumberOfModels"], style="PASSED")),
            ("Incomplete Models", format_number(statistics["totalIncompleteNumberOfModels"], style="UNVISITED")),
            ("Not Executed Models", format_number(statistics["totalNotExecutedNumberOfModels"], style="UNVISITED")),
            ("Failed Models", format_number(statistics["totalFailedNumberOfModels"], style="FAILED"))
        ], prefix="  ")

    @staticmethod
    def _format_vertices_table(statistics):
        text = format_table([
            ("Vertex Coverage", format_number(statistics["vertexCoverage"], style="COVERAGE")),
            ("Number of Vertices", format_number(statistics["totalNumberOfVertices"])),
            ("Visited Vertices", format_number(statistics["totalNumberOfVisitedVertices"], style="PASSED")),
            ("Unvisited Vertices", format_number(statistics["totalNumberOfUnvisitedVertices"], style="UNVISITED")),
        ], prefix="  ")

        if statistics.get("verticesNotVisited"):
            text += format_unvisited_elements(
                statistics["verticesNotVisited"],
                title="Unvisited Vertices:",
                prefix="  "
            )
            text += "\n"

        return text

    @staticmethod
    def _format_edges_table(statistics):
        text = format_table([
            ("Edge Coverage", format_number(statistics["edgeCoverage"], style="COVERAGE")),
            ("Number of Edges", format_number(statistics["totalNumberOfEdges"])),
            ("Visited Edges", format_number(statistics["totalNumberOfVisitedEdges"], style="PASSED")),
            ("Unvisited Edges", format_number(statistics["totalNumberOfUnvisitedEdges"], style="UNVISITED")),
        ], prefix="  ")

        if statistics["edgesNotVisited"]:
            text += format_unvisited_elements(
                statistics["edgesNotVisited"],
                title="Unvisited Edges:",
                prefix="  "
            )
            text += "\n"

        return text

    @staticmethod
    def _format_requirements_table(statistics):
        if (statistics.get("totalNumberOfRequirement", 0) == 0):
            return ""

        text = format_table([
            (
                "Requirement Coverage",
                format_number(statistics["requirementCoverage"], style="COVERAGE")
            ),
            (
                "Number of Requirements",
                format_number(statistics["totalNumberOfRequirement"])
            ),
            (
                "Passed Requirements",
                format_number(statistics["totalNumberOfPassedRequirement"], style="PASSED")
            ),
            (
                "Uncovered Requirements",
                format_number(statistics["totalNumberOfUncoveredRequirement"], style="UNVISITED")
            ),
            (
                "Failed Requirements",
                format_number(statistics["totalNumberOfFailedRequirement"], style="FAILED")
            )
        ], prefix="  ")

        text += format_requirements(
            statistics["requirementsPassed"],
            title="Passed Requirements",
            prefix="  ",
            color="green"
        )

        text += format_requirements(
            statistics["requirementsNotCovered"],
            title="Uncovered Requirements",
            prefix="  ",
            color="yellow"
        )

        text += format_requirements(
            statistics["requirementsFailed"],
            title="Failed Requirements",
            prefix="  ",
            color="red"
        )

        return text

    @classmethod
    def format(cls, statistics):
        if not statistics:
            return ""

        statistics = cls._normalize_statistics(statistics)

        text = click.style("\nStatistics:\n\n", bold=True)
        text += cls._format_models_table(statistics)
        text += cls._format_vertices_table(statistics)
        text += cls._format_edges_table(statistics)
        text += cls._format_requirements_table(statistics)

        return text


def fill(text, width=70, **kwargs):
    """Wraps the multiple paragraph in text (a string) so every line is at most ``width`` characters long.

    Returns:
        str: Returns a single string containing the wrapped paragraphs.
    """

    result = []

    for paragraph in text.split("\n"):
        result.append(textwrap.fill(paragraph, width=width, **kwargs))

    return "\n".join(result)


def format_number(number, style=None):
    """Formats a ``int`` into a “pretty” string."""

    return NumberFormatter.format(number, style=style)


def format_json(data, title=None, prefix=None):
    """Formats a JSON object into a “pretty” string."""

    if not data:
        return ""

    prefix = prefix or ""
    text = ""

    if title:
        text += "{}\n\n".format(title)

    text += click.style(json.dumps(data, sort_keys=True, indent=2), fg="bright_magenta")

    return textwrap.indent(text + "\n", prefix=prefix)


def format_table(data, prefix=None, fillchar=None):
    """Formats a ``list`` of pairs into a “pretty” string."""

    formatter = TableFormatter()
    return formatter.format(data, prefix=prefix, fillchar=fillchar)


def format_inline_list(iterable, title=None, prefix=None, glue=None):
    """Formats a ``list`` into a single line “pretty” string."""

    if not iterable:
        return ""

    prefix = prefix or ""
    glue = glue or ", "
    text = ""

    if title:
        text += "{}: ".format(title)

    text += glue.join(iterable)

    return textwrap.indent(text, prefix=prefix)


def format_unordered_list(iterable, title=None, prefix=None, delimiter=None):
    """Formats a ``list`` into a “pretty” string."""

    if not iterable:
        return ""

    prefix = prefix or ""
    delimiter = delimiter or "*"
    text = ""

    if title:
        text += "{}\n\n".format(title)

    for item in iterable:
        text += textwrap.indent("{} {}\n".format(delimiter, item), prefix="  " if title else "")

    return textwrap.indent(text, prefix=prefix) + "\n"


def format_step_name(step):
    """Formats an step name into a “pretty” string."""

    if step.get("modelName"):
        text = "{}.{}".format(step["modelName"], step["name"])
    else:
        text = "{}".format(step["name"])

    return text


def format_step_status(status):
    """Formats a step status into a “pretty” string."""

    colors = {
        Status.RUNNING: "yellow",
        Status.PASSED: "green",
        Status.FAILED: "red"
    }

    return click.style(str(status), fg=colors.get(status, "white"), bold=True)


def format_data(data, prefix=None):
    """Formats a graph data object into a “pretty” string."""

    prefix = prefix or ""
    title = click.style("Data:", fg="bright_black")

    return format_json(data, title=title, prefix=prefix)


def format_output(output, prefix=None):
    """Formats an output of a test method into a “pretty” string."""

    if not output:
        return ""

    width, _ = shutil.get_terminal_size()
    prefix = prefix or ""
    output = fill(output, width=width - len(prefix))

    title = click.style("Output:", fg="bright_black")
    content = click.style(output.strip(" \n"), fg="cyan")

    text = "{}\n\n{}\n".format(title, content)

    return textwrap.indent(text, prefix=prefix)


def format_result(result, prefix=None):
    """Formats a result object returned by a test method into a “pretty” string."""

    prefix = prefix or ""
    title = click.style("Result:", fg="bright_black")

    return format_json(result, title=title, prefix=prefix)


def format_error(error, prefix=None):
    """Formats an error object into a “pretty” string."""

    if not error:
        return ""

    width, _ = shutil.get_terminal_size()
    prefix = prefix or ""

    title = click.style("Error:", fg="bright_black")
    content = click.style(error["message"], fg="red", bold=True)

    if error.get("trace"):
        content += "\n\n{}".format(click.style(error["trace"], fg="red"))

    text = "{} {}\n".format(title, content)
    text = fill(text, width=width - len(prefix))

    return textwrap.indent(text, prefix=prefix)


def format_unvisited_elements(elements, title=None, prefix=None):
    """Formats a list of unvisited elements ``list`` into a “pretty” string.

    Made for the ``verticesNotVisited``, ``edgesNotVisited`` and ``unvisitedElements``
    returned by the GraphWalker REST API.
    """

    return UnvisitedElementsFormatter.format(elements, title=title, prefix=prefix)


def format_requirements(requirements, title=None, prefix=None, color=None):
    """Formats a requirement ``list`` into a “pretty” string.

    Made for ``requirementsPassed``, ``requirementsNotCovered`` and ``requirementsFailed``
    returned by the GraphWalker API.
    """

    return RequirementsFormatter.format(requirements, title=title, prefix=prefix, color=color)


def format_statistics(statistics):
    """Formats a run statistics into a “pretty” string.

    Made for the ``statistics`` returned by the GraphWalker API.
    """

    return StatisticsFormatter.format(statistics)


def format_run_status(status):
    """Formats a run status into a “pretty” string.

    Args:
        status (:obj:`bool`): True if the run was successful, False otherwise.
    """

    if status is None:
        return ""

    message = "PASSED" if status else "FAILED"
    color = "green" if status else "red"

    text = click.style(" {} ".format(message), bg=color, bold=True)

    return "Status: {}\n".format(text)
