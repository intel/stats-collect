# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide several dataclasses representing built tabs and tab components. These classes eventually get
serialised into JSON, which is read and interpreted by the JavaScript side of the HTML report.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from dataclasses import dataclass, field
from typing import Dict, List
from pathlib import Path

@dataclass
class BuiltDTabFilePreview:
    """
    The data required for adding a file preview to an HTML report. A file preview is a data tab
    element that includes the contents of one or multiple files, and possibly a diff between the
    files.

    Attributes:
        title: The title to be displayed at the top of the file preview.
        paths: A dictionary mapping report IDs to file paths in the format '{ReportID: FilePath}'.
        diff: The path to the diff file to be displayed in the file preview (no diff if 'None').
    """

    title: str
    paths: Dict[str, Path]
    diff: Path | None = None

@dataclass
class BuiltDTab:
    """
    The data required for adding a data tab (D-tab) to an HTML report. A data tab contains data such
    as a summary table and plots.

    Attributes:
        name: The name of the data tab, used as the tab label in the hierarchy of tabs in HTML
              report.
        ppaths: A list of relative paths to 'plotly' plots to include in the tab. No plots if None.
        smrytblpath: A relative path to the summary table dump for the metric. No summary table if
                     None.
        fpreviews: A list of file previews to include in the tab. No file previews if None.
        alerts: A list of alert messages to notify the report viewer of specific nuances or issues
                related to the tab, such as missing diagrams or other elements. No alerts if None.
    """

    name: str
    ppaths: List[Path] | None = field(default_factory=list)
    smrytblpath: Path | None = None
    fpreviews: List[BuiltDTabFilePreview] | None = field(default_factory=list)
    alerts: List[str] | None = field(default_factory=list)

@dataclass
class BuiltCTab:
    """
    The data required for adding a container tab (C-tab) to an HTML report. A container tab is a
    non-leaf tab in the HTML report's tab hierarchy. It can contain child tabs, which may either be
    other container tabs or data tabs.

    Attributes:
        name: The name of the C-tab, used as the tab label in the hierarchy of tabs in HTML report.
        tabs: The child tabs contained within this container tab. These can be either other
              container tabs or data tabs.
    """

    name: str
    tabs: List[BuiltCTab | BuiltDTab] | List[BuiltCTab] | List[BuiltDTab]
