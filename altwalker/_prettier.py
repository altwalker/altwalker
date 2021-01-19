"""A collection of classes and methods that convert data into “pretty” strings for the CLI."""

import json
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


class CoverageFormater:
    """Formats a ``int`` into a “pretty” coverage string."""

    @staticmethod
    def color(percentage):
        if percentage < 50:
            return "red"

        if percentage < 80:
            return "yellow"

        return "green"

    def format(self, percentege):
        return click.style("{}%".format(percentege), fg=self.color(percentege), bold=True)


class TableFormater:
    """Formats a ``dict`` into a “pretty” table."""

    @staticmethod
    def _format_row(key, value, fillchar=None):
        fillchar = fillchar or "."

        key = key.ljust(30, fillchar)
        value = str(value).rjust(30, fillchar)

        return "{}{}\n".format(key, value)

    def format(self, data, prefix=None, fillchar=None):
        if not data:
            return ""

        text = ""
        prefix = prefix or "  "

        for key, value in data.items():
            text += self._format_row(key, value, fillchar=fillchar)

        return textwrap.indent(text, prefix=prefix) + "\n"


class UnvisitedElementsFormater:

    @staticmethod
    def _format_element(element):
        element_id = element.get("vertexId") or element.get("edgeId") or element.get("elementId")
        model_name = element.get("modelName")
        element_name = element.get("vertexName") or element.get("edgeName") or element.get("elementName")

        if model_name:
            return click.style("{} - {}.{}".format(element_id, model_name, element_name), fg="yellow")
        else:
            return click.style("{} - {}".format(element_id, element_name), fg="yellow")

    def _normalize_elements(self, elements):
        return [self._format_element(element) for element in elements]

    def format(self, elements, title=None, prefix=None):
        if not elements:
            return ""

        return format_unordered_list(self._normalize_elements(elements), title=title, prefix=prefix)


class RquirementsFormater:
    """Formats a requirement ``list`` into a “pretty” string."""

    def _normalize_requirement(self, requirement):
        return {
            "modelName": requirement.get("modelName"),
            "key": requirement.get("RequirementKey") or requirement.get("requirementKey")
        }

    def _normalize_requirements(self, requirements):
        return [self._normalize_requirement(requirement) for requirement in requirements]

    def _group_requirements(cls, requirements):
        result = defaultdict(list)

        for requirement in requirements:
            result[requirement["modelName"]].append(requirement["key"])

        return result

    def _format_keys(self, keys, color=None):
        return [click.style(key, fg=color) for key in keys]

    def format(self, requirements, title=None, prefix=None, color=None):
        requirements = self._normalize_requirements(requirements)
        requirements = self._group_requirements(requirements)

        items = [
            format_inline_list(self._format_keys(keys, color=color), title=title)
            for title, keys in requirements.items()
        ]

        return format_unordered_list(items, title=title, prefix=prefix)


class StatisticsFormater:
    """Formats statistics into a “pretty” string."""

    def _get_models_coverage(self, statistics):
        number_of_models = statistics["totalNumberOfModels"]
        number_of_complted_models = statistics["totalCompletedNumberOfModels"]

        return number_of_complted_models * 100 // number_of_models

    def _normalize_statistics(self, statistics):
        statistics["modelCoverage"] = self._get_models_coverage(statistics)
        return statistics

    def _format_number(self, number):
        return click.style(str(number), fg="white", bold=True)

    def _format_passed(self, number):
        color = "red" if number == 0 else "green"

        return click.style(str(number), fg=color, bold=True)

    def _format_unvisited(self, number):
        color = "yellow" if number > 0 else "green"

        return click.style(str(number), fg=color, bold=True)

    def _format_failed(self, number):
        color = "red" if number > 0 else "green"

        return click.style(str(number), fg=color, bold=True)

    def format(self, statistics):
        statistics = self._normalize_statistics(statistics)

        text = click.style("\nStatistics:\n\n", bold=True)

        text += format_table({
            "Model Coverage": format_coverage(statistics["modelCoverage"]),
            "Number of Models": self._format_number(statistics["totalNumberOfModels"]),
            "Completed Models": self._format_passed(statistics["totalCompletedNumberOfModels"]),
            "Incomplete Models": self._format_unvisited(statistics["totalIncompleteNumberOfModels"]),
            "Not Executed Models": self._format_unvisited(statistics["totalNotExecutedNumberOfModels"]),
            "Failed Models": self._format_failed(statistics["totalFailedNumberOfModels"])
        })

        text += format_table({
            "Vertex Coverage": format_coverage(statistics["vertexCoverage"]),
            "Number of Vertices": self._format_number(statistics["totalNumberOfVertices"]),
            "Visited Vertices": self._format_passed(statistics["totalNumberOfVisitedVertices"]),
            "Unvisited Vertices": self._format_unvisited(statistics["totalNumberOfUnvisitedVertices"])
        })

        if statistics["verticesNotVisited"]:
            text += format_unvisited_elements(
                statistics["verticesNotVisited"],
                title="Unvisited Vertices:",
                prefix="  "
            )
            text += "\n"

        text += format_table({
            "Edge Coverage": format_coverage(statistics["edgeCoverage"]),
            "Number of Edges": self._format_number(statistics["totalNumberOfEdges"]),
            "Visited Edges": self._format_passed(statistics["totalNumberOfVisitedEdges"]),
            "Unvisited Edges": self._format_unvisited(statistics["totalNumberOfUnvisitedEdges"])
        })

        if statistics["edgesNotVisited"]:
            text += format_unvisited_elements(
                statistics["edgesNotVisited"],
                title="Unvisited Edges:",
                prefix="  "
            )
            text += "\n"

        if (statistics.get("totalNumberOfRequirement", 0) > 0):
            text += format_table({
                "Requirement Coverage": format_coverage(statistics["requirementCoverage"]),
                "Number of Requirements": self._format_number(statistics["totalNumberOfRequirement"]),
                "Passed Requirements": self._format_passed(statistics["totalNumberOfPassedRequirement"]),
                "Uncovered Requirements": self._format_unvisited(statistics["totalNumberOfUncoveredRequirement"]),
                "Failed Requirements": self._format_failed(statistics["totalNumberOfFailedRequirement"])
            })

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


def fill(text, width=70, **kwargs):
    """Wraps the multiple paragraph in text, and returns a single string containing the wrapped paragraphs."""

    result = []

    for paragraph in text.split("\n"):
        result.append(textwrap.fill(paragraph, width=width, **kwargs))

    return "\n".join(result)


def format_coverage(percentage):
    """Formats a number into a “pretty” percentage."""

    formater = CoverageFormater()
    return formater.format(percentage)


def format_json(data, title=None, prefix=None):
    if not data:
        return ""

    prefix = prefix or ""
    text = ""

    if title:
        text += "{}\n\n".format(title)

    text += click.style(json.dumps(data, sort_keys=True, indent=2), fg="bright_magenta")

    return textwrap.indent(text + "\n", prefix=prefix)


def format_table(data, prefix=None, fillchar=None):
    """Formats a ``dict`` into a “pretty” string."""

    formater = TableFormater()
    return formater.format(data, prefix=prefix, fillchar=fillchar)


def format_inline_list(iterable, title=None, prefix=None, glue=None):
    """Formats a ``list`` into a “pretty” string."""

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
    if step.get("modelName"):
        string = "{}.{}".format(step["modelName"], step["name"])
    else:
        string = "{}".format(step["name"])

    return string


def format_step_status(status):
    colors = {
        Status.RUNNING: "yellow",
        Status.PASSED: "green",
        Status.FAILED: "red"
    }

    return click.style(str(status), fg=colors.get(status, "white"), bold=True)


def format_data(data, prefix=None):
    if not data:
        return ""

    prefix = prefix or "  "

    title = click.style("Data:", fg="bright_black", underline=True)

    return format_json(data, title=title, prefix=prefix)


def format_output(output, prefix=None):
    if not output:
        return ""

    width, _ = click.get_terminal_size()
    prefix = prefix or ""

    title = click.style("Output:", fg="bright_black", underline=True)
    content = click.style(output.strip(" \n"), fg="cyan")

    text = "{}\n\n{}\n".format(title, content)
    text = fill(text, width=width - len(prefix))

    return textwrap.indent(text, prefix=prefix)


def format_result(result, prefix=None):
    if not result:
        return ""

    prefix = prefix or "  "

    title = click.style("Result:", fg="bright_black", underline=True)

    return format_json(result, title=title, prefix=prefix)


def format_error(error, prefix=None):
    if not error:
        return ""

    width, _ = click.get_terminal_size()
    prefix = prefix or "  "

    title = click.style("Error:", fg="bright_black", underline=True)
    content = click.style(error["message"], fg="red", bold=True)

    if error.get("trace"):
        content += "\n\n{}".format(click.style(error["trace"], fg="red"))

    text = "\n{} {}\n".format(title, content)
    text = fill(text, width=width - len(prefix))

    return textwrap.indent(text, prefix=prefix)


def format_unvisited_elements(elements, title=None, prefix=None):
    formater = UnvisitedElementsFormater()
    return formater.format(elements, title=title, prefix=prefix)


def format_requirements(requirements, title=None, prefix=None, color=None):
    formater = RquirementsFormater()
    return formater.format(requirements, title=title, prefix=prefix, color=color)


def format_statistics(statistics):
    formater = StatisticsFormater()
    return formater.format(statistics)


def format_run_status(status):
    message = "PASSED" if status else "FAILED"
    color = "green" if status else "red"

    text = click.style(" {} ".format(message), bg=color, bold=True)

    return "Status: {}\n".format(text)
