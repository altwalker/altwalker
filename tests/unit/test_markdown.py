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

import pytest

from altwalker._markdown import generate_markdown_table, wrap_tag


@pytest.mark.parametrize("data, expected", [
    ([["A"]], "<table><tr><td>A</td></tr></table>"),
    ([["A"], ["B"]], "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"),
    ([[{"data": "A"}], [{"data": "B"}]], "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"),
    (
        [[{"data": "A", "header": False}], [{"data": "B", "header": False}]],
        "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"
    ),
    ([["A", "B"], ["C", "D"]], "<table><tr><td>A</td><td>B</td></tr><tr><td>C</td><td>D</td></tr></table>"),
    ([[{"header": True, "data": "A"}]], "<table><tr><th>A</th></tr></table>"),
    (
        [[{"data": "A", "header": True}, {"data": "B", "header": True}], ["C", "D"]],
        "<table><tr><th>A</th><th>B</th></tr><tr><td>C</td><td>D</td></tr></table>"
    )
])
def test_generate_markdown_table(data, expected):
    assert generate_markdown_table(data) == expected


@pytest.mark.parametrize("tag, content, expected", [
    ("td", None, "<td>"),
    ("td", "Content", "<td>Content</td>")
])
def test_wrap_tag(tag, content, expected):
    assert wrap_tag(tag, content=content) == expected
