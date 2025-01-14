# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for data tabs of the "SysInfo" container tab.
"""

from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs import _DTabBuilder

class SysInfoDTabBuilderBase(_DTabBuilder.DTabBuilder):
    """
    Base class for data tabs of the "SysInfo" container tab.
    """

    def get_tab(self) -> _Tabs.DTabDC:
        """
        Generate and return a D-tab of for the "Sysinfo" C-tab.

        Returns:
            The data tab object.
        """

        self.add_fpreviews(self.stats_paths, self.files)

        if self.fpreviews:
            return super().get_tab()

        raise Error(f"BUG: Unable to generate the \"{self.name}\" SysInfo D-tab, no file previews")

    def __init__(self, name: str, outdir, files: dict[str, Path], stats_paths: dict[str, Path],
                 basedir: Path | None = None):
        """
        The class constructor.

        Args:
            name: The name to give the generated D-tab.
            outdir: The output directory path (where the D-tab files should be placed).
            files: A dictionary containing the paths of raw statistics files to include to the
                   D-tab.
            stats_paths: A dictionary mapping report IDs to raw statistics directory paths.
            basedir: The report base directory directory path, defaults to 'outdir'.

        The expected format for 'files' is '{Title: FilePath}' where 'Title' is the title for the
        raw statistics file and 'FilePath' is path to the raw statistics file relative to the
        statistics directory ('stats_paths').
        """

        if not any(fp for fp in stats_paths.values()):
            raise Error("No raw statistics found")

        super().__init__({}, outdir, name, basedir=basedir)

        self.name = name
        self.files = files
        self.stats_paths = stats_paths
