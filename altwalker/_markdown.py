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

"""Utils for generating markdown."""


def generate_markdown_table(data):
    """Generates an markdown table from the data.

    Args:
        data: The table rows.

    Returns:
        str: The markdown representation of the table.

    """

    table_markdown = []

    for row in data:
        row_markdown = []

        for cell in row:
            if isinstance(cell, str):
                row_markdown.append(wrap_tag("td", content=cell))
                continue

            tag = "th" if cell.get("header", False) else "td"
            row_markdown.append(wrap_tag(tag, content=cell.get("data")))

        table_markdown.append(wrap_tag("tr", content="".join(row_markdown)))

    return wrap_tag("table", "".join(table_markdown))


def wrap_tag(tag, content=None):
    """Wraps content in an HTML tag.

    Args:
        tag (str): The HTML tag to wrap.
        content (str): The content within the tag.

    Returns:
        str: The wrapped HTML tag with content.

    """

    if content:
        return f"<{tag}>{content}</{tag}>"

    return f"<{tag}>"
