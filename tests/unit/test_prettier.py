import sys

import pytest
import click

import altwalker._prettier as prettier


SAMPLE_TEST = """\
The textwrap module can be used to format text for output in situations where pretty-printing is desired.

It offers programmatic functionality similar to the paragraph wrapping or filling features found in many text editors.
"""

WRAPED_SAMPLE_TEST = """\
The textwrap module can be used to format text for
output in situations where pretty-printing is
desired.

It offers programmatic functionality similar to
the paragraph wrapping or filling features found
in many text editors.
"""


def test_fill():
    assert prettier.fill(SAMPLE_TEST, width=50) == WRAPED_SAMPLE_TEST


@pytest.mark.parametrize(
    "iterable, title, prefix, glue, expected",
    [
        (None, None, None, None, ""),
        ([], None, None, None, ""),
        ((), None, None, None, ""),
        (None, "Title", None, None, ""),
        (None, None, "  ", None, ""),
        (None, None, None, " - ", ""),
        (["A", "B", "C"], None, None, None, "A, B, C"),
        (["A", "B", "C"], "Letters", None, None, "Letters: A, B, C"),
        (["A", "B", "C"], None, "  ", None, "  A, B, C"),
        (["A", "B", "C"], "Letters", "  ", None, "  Letters: A, B, C"),
        (["A", "B", "C"], None, None, " - ", "A - B - C"),
    ]
)
def test_format_inline_list(iterable, title, prefix, glue, expected):
    assert prettier.format_inline_list(iterable, title=title, prefix=prefix, glue=glue) == expected


@pytest.mark.parametrize(
    "step, expected",
    [
        ({"name": "setUpRun"}, "setUpRun"),
        ({"name": "setUp", "modelName": "BuyModel"}, "BuyModel.setUp")
    ]
)
def test_format_step_name(step, expected):
    assert prettier.format_step_name(step) == expected


@pytest.mark.parametrize(
    "status, expected",
    [
        (prettier.Status.RUNNING, click.style("RUNNING...", fg="yellow", bold=True)),
        (prettier.Status.PASSED, click.style("PASSED", fg="green", bold=True)),
        (prettier.Status.FAILED, click.style("FAILED", fg="red", bold=True))
    ]
)
def test_format_step_status(status, expected):
    assert prettier.format_step_status(status) == expected


@pytest.mark.parametrize(
    "status, expected",
    [
        (None, ""),
        (True, "Status: {}\n".format(click.style(" PASSED ", bg="green", bold=True))),
        (False, "Status: {}\n".format(click.style(" FAILED ", bg="red", bold=True)))
    ]
)
def test_format_run_status(status, expected):
    assert prettier.format_run_status(status) == expected


class TestFormatNumber:

    @pytest.mark.parametrize(
        "percentage, expected",
        [
            (0, click.style("0%", fg="red", bold=True)),
            (10, click.style("10%", fg="red", bold=True)),
            (25, click.style("25%", fg="red", bold=True)),
            (49, click.style("49%", fg="red", bold=True)),
            (50, click.style("50%", fg="yellow", bold=True)),
            (60, click.style("60%", fg="yellow", bold=True)),
            (70, click.style("70%", fg="yellow", bold=True)),
            (79, click.style("79%", fg="yellow", bold=True)),
            (80, click.style("80%", fg="green", bold=True)),
            (90, click.style("90%", fg="green", bold=True)),
            (100, click.style("100%", fg="green", bold=True))
        ]
    )
    def test_coverage(self, percentage, expected):
        assert prettier.format_number(percentage, style="COVERAGE") == expected

    @pytest.mark.parametrize(
        "number, expected",
        [
            (0, click.style("0", fg="red", bold=True)),
            (1, click.style("1", fg="green", bold=True)),
            (5, click.style("5", fg="green", bold=True)),
            (10, click.style("10", fg="green", bold=True))
        ]
    )
    def test_passed(self, number, expected):
        assert prettier.format_number(number, style="PASSED") == expected

    @pytest.mark.parametrize(
        "number, expected",
        [
            (0, click.style("0", fg="green", bold=True)),
            (1, click.style("1", fg="yellow", bold=True)),
            (5, click.style("5", fg="yellow", bold=True)),
            (10, click.style("10", fg="yellow", bold=True))
        ]
    )
    def test_unvisited(self, number, expected):
        assert prettier.format_number(number, style="UNVISITED") == expected

    @pytest.mark.parametrize(
        "number, expected",
        [
            (0, click.style("0", fg="green", bold=True)),
            (1, click.style("1", fg="red", bold=True)),
            (5, click.style("5", fg="red", bold=True)),
            (10, click.style("10", fg="red", bold=True))
        ]
    )
    def test_failed(self, number, expected):
        assert prettier.format_number(number, style="FAILED") == expected

    @pytest.mark.parametrize(
        "number, expected",
        [
            (0, click.style("0", fg="white", bold=True)),
            (1, click.style("1", fg="white", bold=True)),
            (5, click.style("5", fg="white", bold=True)),
            (10, click.style("10", fg="white", bold=True))
        ]
    )
    def test_numver(self, number, expected):
        assert prettier.format_number(number) == expected


class TestFormatJson:

    def test_no_data(self):
        assert prettier.format_json(None) == ""

    def test_title(self):
        title = "JSON Data"
        data = {"key": 1}

        assert prettier.format_json(data, title=title).startswith("{}\n\n".format(title))

    def test_format(self):
        data = {
            "string": "value",
            "integer": 1
        }

        expected = [
            '{',
            '  "integer": 1,',
            '  "string": "value"',
            '}'
        ]

        assert prettier.format_json(data) == click.style("\n".join(expected), fg="bright_magenta") + "\n"


class TestFormatTable:

    @pytest.mark.parametrize(
        "key, value, expected",
        [
            ("Coverage", "100%", "Coverage................................................100%\n"),
            ("Number of Models", "12", "Number of Models..........................................12\n")
        ]
    )
    def test_format_row(self, key, value, expected):
        assert prettier.TableFormatter._format_row(key, value) == expected

    def test_no_data(self):
        assert prettier.format_table(None) == ""

    def test_format(self):
        data = [
            ("Coverage", "100%"),
            ("Number of Models", "12")
        ]

        expected = [
            "Coverage................................................100%",
            "Number of Models..........................................12"
        ]

        assert prettier.format_table(data) == "\n".join(expected) + "\n\n"


class TestFormatUnorderedList:

    def test_no_data(self):
        assert prettier.format_unordered_list(None) == ""

    def test_title(self):
        title = "Unordered List"
        iterable = ["A", "B"]

        expected = [
            "Unordered List\n",
            "  * A",
            "  * B"
        ]

        assert prettier.format_unordered_list(iterable, title=title) == "\n".join(expected) + "\n\n"

    def test_format(self):
        iterable = ["A", "B"]

        expected = [
            "* A",
            "* B"
        ]

        assert prettier.format_unordered_list(iterable) == "\n".join(expected) + "\n\n"


class TestFormatData:

    def test_no_data(self):
        assert prettier.format_data(None) == ""

    def test_title(self):
        title = click.style("Data:", fg="bright_black")
        data = {"key": 1}

        assert prettier.format_data(data).startswith("{}\n\n".format(title))

    def test_format(self):
        data = {
            "string": "value",
            "integer": 1
        }

        expected = [
            '{',
            '  "integer": 1,',
            '  "string": "value"',
            '}'
        ]

        assert prettier.format_data(data).endswith(click.style("\n".join(expected), fg="bright_magenta") + "\n")


class TestFormatOutput:

    def test_no_output(self):
        assert prettier.format_output(None) == ""

    def test_title(self):
        title = click.style("Output:", fg="bright_black")
        output = "Sample text"

        assert prettier.format_output(output).startswith("{}\n\n".format(title))

    def test_format(self):
        output = "Sample text"

        assert prettier.format_output(output).endswith(click.style(output, fg="cyan") + "\n")


class TestFormatResult:

    def test_no_result(self):
        assert prettier.format_result(None) == ""

    def test_title(self):
        title = click.style("Result:", fg="bright_black")
        result = {"key": 1}

        assert prettier.format_result(result).startswith("{}\n\n".format(title))

    def test_format(self):
        result = {
            "string": "value",
            "integer": 1
        }

        expected = [
            '{',
            '  "integer": 1,',
            '  "string": "value"',
            '}'
        ]

        assert prettier.format_result(result).endswith(click.style("\n".join(expected), fg="bright_magenta") + "\n")


class TestFormatError:

    def test_no_error(self):
        assert prettier.format_error(None) == ""

    def test_title(self):
        title = click.style("Error:", fg="bright_black")
        error = {
            "message": "No file found."
        }

        assert prettier.format_error(error).startswith(title)

    def test_message(self):
        error = {
            "message": "No file found."
        }

        assert prettier.format_error(error).endswith(click.style(error["message"], fg="red", bold=True) + "\n")

    def test_trace(self):
        error = {
            "message": "No file found.",
            "trace": "Traceback (most recent call last) [...]",
        }

        assert prettier.format_error(error).endswith(click.style(error["trace"], fg="red") + "\n")


class TestFormatUnvisitedElements:

    @pytest.mark.parametrize(
        "element, expected",
        [
            (
                {"elementId": "v1", "modelName": "ModelName", "elementName": "v_name"},
                click.style("v1 - ModelName.v_name", fg="yellow"),
            ),
            (
                {"elementId": "v1", "elementName": "v_name"},
                click.style("v1 - v_name", fg="yellow"),
            ),
            (
                {"vertexId": "v1", "modelName": "ModelName", "vertexName": "v_name"},
                click.style("v1 - ModelName.v_name", fg="yellow"),
            ),
            (
                {"vertexId": "v1", "vertexName": "v_name"},
                click.style("v1 - v_name", fg="yellow"),
            ),
            (
                {"edgeId": "e1", "modelName": "ModelName", "edgeName": "e_name"},
                click.style("e1 - ModelName.e_name", fg="yellow"),
            ),
            (
                {"edgeId": "e1", "edgeName": "e_name"},
                click.style("e1 - e_name", fg="yellow"),
            )
        ]
    )
    def test_format_element(self, element, expected):
        formatter = prettier.UnvisitedElementsFormatter()
        assert formatter._format_element(element) == expected

    def test_normalize_elements(self):
        elements = [
            {"elementId": "v0", "elementName": "v_start"},
            {"vertexId": "v1", "modelName": "ModelName", "vertexName": "v_name"},
            {"edgeId": "e1", "modelName": "ModelName", "edgeName": "e_name"},
        ]

        expected = [
            click.style("v0 - v_start", fg="yellow"),
            click.style("v1 - ModelName.v_name", fg="yellow"),
            click.style("e1 - ModelName.e_name", fg="yellow"),
        ]

        formatter = prettier.UnvisitedElementsFormatter()
        assert formatter._normalize_elements(elements) == expected

    def test_no_elements(self):
        assert prettier.format_unvisited_elements(None) == ""

    def test_format(self):
        elements = [
            {"elementId": "v0", "elementName": "v_start"},
            {"vertexId": "v1", "modelName": "ModelName", "vertexName": "v_name"},
            {"edgeId": "e1", "modelName": "ModelName", "edgeName": "e_name"},
        ]

        expected = [
            "* " + click.style("v0 - v_start", fg="yellow"),
            "* " + click.style("v1 - ModelName.v_name", fg="yellow"),
            "* " + click.style("e1 - ModelName.e_name", fg="yellow"),
        ]

        assert prettier.format_unvisited_elements(elements) == "\n".join(expected) + "\n\n"


@pytest.mark.skipif(sys.version_info < (3, 6), reason="Requires python3.6 or higher")
class TestFormatRequirements:

    @pytest.mark.parametrize(
        "requirement, expected",
        [
            (
                {"RequirementKey": "Requirement 1", "modelName": "ModelName"},
                {"key": "Requirement 1", "modelName": "ModelName"}
            ),
            (
                {"requirementKey": "Requirement 1", "modelName": "ModelName"},
                {"key": "Requirement 1", "modelName": "ModelName"}
            )
        ]
    )
    def test_normalize_requirement(self, requirement, expected):
        assert prettier.RequirementsFormatter._normalize_requirement(requirement) == expected

    def test_normalize_requirements(self):
        requirements = [
            {"RequirementKey": "Requirement 1", "modelName": "ModelName1"},
            {"requirementKey": "Requirement 2", "modelName": "ModelName2"}
        ]

        expected = [
            {"key": "Requirement 1", "modelName": "ModelName1"},
            {"key": "Requirement 2", "modelName": "ModelName2"}
        ]

        assert prettier.RequirementsFormatter._normalize_requirements(requirements) == expected

    def test_group_requirements(self):
        requirements = [
            {"key": "Requirement 1", "modelName": "ModelName1"},
            {"key": "Requirement 2", "modelName": "ModelName1"},
            {"key": "Requirement 3", "modelName": "ModelName2"},
            {"key": "Requirement 4", "modelName": "ModelName2"}
        ]

        expected = {
            "ModelName1": {"Requirement 1", "Requirement 2"},
            "ModelName2": {"Requirement 3", "Requirement 4"}
        }

        assert prettier.RequirementsFormatter._group_requirements(requirements) == expected

    def test_no_requirements(self):
        assert prettier.format_requirements(None) == ""

    def test_format(self):
        requirements = [
            {"RequirementKey": "Requirement 1", "modelName": "ModelName1"},
            {"requirementKey": "Requirement 2", "modelName": "ModelName2"}
        ]

        expected = [
            "* ModelName1: Requirement 1",
            "* ModelName2: Requirement 2"
        ]

        assert click.unstyle(prettier.format_requirements(requirements)) == "\n".join(expected) + "\n\n"


class TestFormatStatistics:

    @pytest.mark.parametrize(
        "total, completed, expected",
        [
            (10, 10, 100),
            (10, 7, 70),
            (10, 5, 50),
            (10, 3, 30),
        ]
    )
    def test_get_models_coverage(self, total, completed, expected):
        statistics = {
            "totalNumberOfModels": total,
            "totalCompletedNumberOfModels": completed
        }

        assert prettier.StatisticsFormatter._get_models_coverage(statistics) == expected

    @pytest.mark.parametrize(
        "total, completed, expected",
        [
            (10, 10, 100),
            (10, 7, 70),
            (10, 5, 50),
            (10, 3, 30),
        ]
    )
    def test_normalize_statistics(self, total, completed, expected):
        statistics = {
            "totalNumberOfModels": total,
            "totalCompletedNumberOfModels": completed
        }
        statistics = prettier.StatisticsFormatter._normalize_statistics(statistics)

        assert statistics["modelCoverage"] == expected

    def test_format_models_table(self):
        statistics = {
            "modelCoverage": 100,
            "totalNumberOfModels": 50,
            "totalCompletedNumberOfModels": 40,
            "totalIncompleteNumberOfModels": 30,
            "totalNotExecutedNumberOfModels": 20,
            "totalFailedNumberOfModels": 10,
        }

        expected = [
            "  Model Coverage.............................100%",
            "  Number of Models.............................50",
            "  Completed Models.............................40",
            "  Incomplete Models............................30",
            "  Not Executed Models..........................20",
            "  Failed Models................................10"
        ]

        actual = prettier.StatisticsFormatter._format_models_table(statistics)
        actual = click.unstyle(actual)

        assert actual == "\n".join(expected) + "\n\n"

    def test_format_vertices_table(statistics):
        statistics = {
            "vertexCoverage": 100,
            "totalNumberOfVertices": 30,
            "totalNumberOfVisitedVertices": 20,
            "totalNumberOfUnvisitedVertices": 10,
            "verticesNotVisited": [
                {
                    "vertexId": "v1",
                    "vertexName": "v_a",
                    "modelName": "ModelA"
                },
                {
                    "vertexId": "v2",
                    "vertexName": "v_b",
                    "modelName": "ModelB"
                },
            ]
        }

        expected = [
            "  Vertex Coverage............................100%",
            "  Number of Vertices...........................30",
            "  Visited Vertices.............................20",
            "  Unvisited Vertices...........................10",
            "",
            "  Unvisited Vertices:",
            "",
            "    * v1 - ModelA.v_a",
            "    * v2 - ModelB.v_b"
        ]

        actual = prettier.StatisticsFormatter._format_vertices_table(statistics)
        actual = click.unstyle(actual)

        assert actual == "\n".join(expected) + "\n\n\n"

    def test_format_edges_table(statistics):
        statistics = {
            "edgeCoverage": 100,
            "totalNumberOfEdges": 30,
            "totalNumberOfVisitedEdges": 20,
            "totalNumberOfUnvisitedEdges": 10,
            "edgesNotVisited": [
                {
                    "edgeId": "e1",
                    "edgeName": "e_a",
                    "modelName": "ModelA"
                },
                {
                    "edgeId": "e2",
                    "edgeName": "e_b",
                    "modelName": "ModelB"
                },
            ]
        }

        expected = [
            "  Edge Coverage..............................100%",
            "  Number of Edges..............................30",
            "  Visited Edges................................20",
            "  Unvisited Edges..............................10",
            "",
            "  Unvisited Edges:",
            "",
            "    * e1 - ModelA.e_a",
            "    * e2 - ModelB.e_b"
        ]

        actual = prettier.StatisticsFormatter._format_edges_table(statistics)
        actual = click.unstyle(actual)

        assert actual == "\n".join(expected) + "\n\n\n"

    @pytest.mark.skipif(sys.version_info < (3, 6), reason="Requires python3.6 or higher")
    def test_format_requirements_tabel(statistics):
        statistics = {
            "requirementCoverage": 100,
            "totalNumberOfRequirement": 40,
            "totalNumberOfPassedRequirement": 30,
            "totalNumberOfUncoveredRequirement": 20,
            "totalNumberOfFailedRequirement": 10,
            "requirementsPassed": [
                {"RequirementKey": "Requirement 1", "modelName": "ModelName1"},
                {"requirementKey": "Requirement 2", "modelName": "ModelName2"}
            ],
            "requirementsNotCovered": [
                {"RequirementKey": "Requirement 3", "modelName": "ModelName1"},
                {"requirementKey": "Requirement 4", "modelName": "ModelName2"}
            ],
            "requirementsFailed": [
                {"RequirementKey": "Requirement 5", "modelName": "ModelName1"},
                {"requirementKey": "Requirement 6", "modelName": "ModelName2"}
            ]
        }

        expected = [
            "  Requirement Coverage.......................100%",
            "  Number of Requirements.......................40",
            "  Passed Requirements..........................30",
            "  Uncovered Requirements.......................20",
            "  Failed Requirements..........................10",
            "",
            "  Passed Requirements",
            "",
            "    * ModelName1: Requirement 1",
            "    * ModelName2: Requirement 2",
            "",
            "  Uncovered Requirements",
            "",
            "    * ModelName1: Requirement 3",
            "    * ModelName2: Requirement 4",
            "",
            "  Failed Requirements",
            "",
            "    * ModelName1: Requirement 5",
            "    * ModelName2: Requirement 6"
        ]

        actual = prettier.StatisticsFormatter._format_requirements_table(statistics)
        actual = click.unstyle(actual)

        assert actual == "\n".join(expected) + "\n\n"

    def test_no_requirements(self):
        statistics = {
            "totalNumberOfRequirement": 0
        }

        assert prettier.StatisticsFormatter._format_requirements_table(statistics) == ""

    def test_no_statistics(self):
        assert prettier.format_statistics(None) == ""
