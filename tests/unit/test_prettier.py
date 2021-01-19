import pytest
import click

import altwalker._prettier as prettier


class TestCoverageFormater:

    @pytest.mark.parametrize(
        "percentage, expected",
        [
            (0, "red"),
            (10, "red"),
            (25, "red"),
            (49, "red"),
            (50, "yellow"),
            (60, "yellow"),
            (70, "yellow"),
            (79, "yellow"),
            (80, "green"),
            (90, "green"),
            (100, "green")
        ]
    )
    def test_color(self, percentage, expected):
        assert prettier.CoverageFormater.color(percentage) == expected

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
    def test_format(self, percentage, expected):
        assert prettier.format_coverage(percentage) == expected


class TestFormatTeble:

    @pytest.mark.parametrize(
        "key, value, expected",
        [
            ("Coverage", "100%", "Coverage................................................100%\n"),
            ("Number of Models", "12", "Number of Models..........................................12\n")
        ]
    )
    def test_format_row(self, key, value, expected):
        assert prettier.TableFormater._format_row(key, value) == expected
