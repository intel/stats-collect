# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the 'IntroTable' class to generate the intro table for HTML reports. The intro table is a
top-level table summarizing test results.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from dataclasses import dataclass
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error

# Text displayed in a table cell when a value is unavailable for a specific set of results.
_NA_TEXT = "Not available"

def format_none(val: str | None) -> str:
    """
    Converts 'None' values to an empty string. If the input value is not 'None', it returns the
    original value.

    Args:
        val: The input value to format.

    Returns:
        The original value or an empty string in case of 'None'.
    """

    if val is None:
        return ""
    return val

@dataclass
class _TableCell:
    """
    A cell within the intro table.

    Attributes:
        value: The text to display in the cell.
        hovertext: The text to display when the cursur hovers over the cell.
        link: URL or path used as a clickable link for the cell.
    """

    value: str
    hovertext: str = ''
    link: str = ''

class TableRow:
    """A row within the intro table."""

    def __init__(self, value: str, hovertext: str | None = None, link: str | None  =None):
        """
        Initialize a class instance.

        Set up the first cell in the row under the "Title" column. The cell displays the provided
        'value' as text. Optionally, a 'hovertext' can be specified to show additional information
        when the user hovers over the cell. A 'link' can also be provided to make the text
        clickable, redirecting the user to the specified URL.

        Args:
            value: The text to display in the "Title" column cell.
            hovertext: The text to display when hovering over the cell.
            link: The URL to navigate to when the cell text is clicked.
        """

        self.title_cell = _TableCell(value, format_none(hovertext), format_none(link))
        self.res_cells: dict[str, _TableCell] = {}

    def add_cell(self,
                 reportid: str,
                 value: str | None = None,
                 hovertext: str | None = None,
                 link: str | None = None):
        """
        Add a cell to the row in the specified column.

        Add a cell to the row under the column identified by 'reportid'. The cell will display the
        provided 'value' as text. If 'value' is not provided or is None, a default placeholder text
        will be used to indicate that the value is unavailable.

        If 'hovertext' is provided, it will be displayed as a tooltip when the user overs over the
        cell. If 'link' is provided, the text in the cell will become clickable, and clicking it
        will navigate the user to the specified link.

        Args:
            reportid: The identifier of the column where the cell will be added.
            value: The text to display in the cell. Defaults to a placeholder if None.
            hovertext: Optional text to display on hover. Defaults to None.
            link: Optional URL to make the cell text clickable. Defaults to None.
        """

        value = value if value else _NA_TEXT
        self.res_cells[reportid] = _TableCell(value, format_none(hovertext), format_none(link))

class IntroTable:
    """
    A class to generate the intro table files for HTML reports. The intro table is a top-level table
    summarizing test results.

    The intro table has the following layout:

    | Title   | Result Report ID 1 | Result Report ID 2 |
    |---------|--------------------|--------------------|
    | Key 1   | Val 1              | Val 2              |
    | Key 2   | Val 2              | Val 2              |
    |---------|--------------------|--------------------|
    """

    def __init__(self):
        """The class constructor."""

        self.rows: list[TableRow] = []

    def _dump(self, path, reportids):
        """
        Write the summary table dictionary to a file in a project-specific format. This file will
        later be read and interpreted by the JavaScript code in the HTML report.

        The file format includes two types of lines:
        1. Header: A single header line that must be the first row in the file. It starts with
           'H' and includes the title and report IDs. Example:
        2. Table Row: A row representing data for a specific function or entry. It starts with
           'R' and includes the title cell and corresponding values for each report ID.
           Example: R;func_name|func_description|func_link;func_val|func_hovertext|func_link

        Args:
            path: The file path where the summary table will be written.
            reportids: A list of report IDs to include in the table.
        """

        try:
            with open(path, "w", encoding="utf-8") as fobj:
                lines = []
                lines.append(f"H;Title;{';'.join(reportids)}\n")

                for row in self.rows:
                    # Generate title cell for 'row'.
                    title_cell = row.title_cell
                    line = f"R;{title_cell.value}|{title_cell.hovertext}|{title_cell.link}"

                    for reportid in reportids:
                        cell = row.res_cells.get(reportid)

                        # If this row has no cell for 'reportid', show an cell with '_NA_TEXT'.
                        if cell is None:
                            cell = _TableCell(_NA_TEXT)

                        line += f";{cell.value}|{cell.hovertext}|{cell.link}"

                    lines.append(f"{line}\n")

                fobj.writelines(lines)
        except OSError as err:
            msg = Error(str(err)).indent(2)
            raise Error(f"Failed to dump the intro table to '{path}':\n{msg}") from None

    def add_row(self, value: str, hovertext: str | None = None, link: str | None = None):
        """
        Add a new row to the intro table.

        Create a new row in the intro table with the specified value as the text for the first cell
        in the "Title" column. The other cells can be populated later using the 'add_cell()' method
        of the created row.

        Args:
            value: The text to display in the first cell of the newly added row.
            hovertext: The text to display when hovering over the cell.
            link: The URL to navigate to when the cell is clicked.

        Returns:
            _TableRow: The newly created row object.
        """

        row = TableRow(value, hovertext, link)
        self.rows.append(row)
        return row

    def generate(self, path: Path):
        """
        Generate a text file representing this intro table and save it to the specified path. The
        fille will be read and interpreted by the JavaScript code in the HTML report.

        Args:
            path: The file path where the generated text file will be saved.
        """

        reportids: list[str] = []
        for row in self.rows:
            reportids += list(row.res_cells.keys())

        reportids = Trivial.list_dedup(reportids)

        self._dump(path, reportids)
