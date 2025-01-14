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
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs import _DTabBuilder

class SysInfoDTabBuilderBase(_DTabBuilder.DTabBuilder):
    """
    Base class for data tabs of the "SysInfo" container tab.
    """

    @staticmethod
    def _compat_adjust_paths(paths: dict[str, Path]) -> dict[str, Path]:
        """
        Paths to some of the sysinfo statistics files changed in 'stats-collect' version 1.0.39. For
        example, "dmidecode.raw.txt" became "dmidecode.before.raw.txt". Basically all files got
        either "before" or "after" suffix. Make sure that 'stats-collect' version 1.0.39+ supports
        the raw results from 'stats-collect' version 1.0.38 and older. TODO: remove in 2026.

        Args:
            paths: the raw sysinfo statistics file paths for every raw result (same as in
                   'add_fpreview()).

        Returns:
            The adjusted version of 'paths'.
        """

        new_paths = paths.copy()

        for reportid, path in paths.items():
            if path.exists():
                continue

            if path.name.endswith(".after.raw.txt") or path.name.endswith(".before.raw.txt"):
                # The file does not exist, but it is not about the compatibility.
                continue

            for suffix in (".after.raw.txt", ".before.raw.txt"):
                # Turn file name from like "xyz.raw.txt" to like "xyz.after.raw.txt".
                new_name = path.name[:-len(".raw.txt")] + suffix
                new_path = path.parent / new_name
                if new_path.exists():
                    new_paths[reportid] = new_path
                    break

        return new_paths

    def get_tab(self) -> _Tabs.DTabDC:
        """
        Generate and return a D-tab of for the "Sysinfo" C-tab.

        Returns:
            The data tab object.
        """

        paths = {}
        for title, file in self._files.items():
            for reportid, stats_path in self._stats_paths.items():
                paths[reportid] = stats_path / file

            paths = self._compat_adjust_paths(paths)

            self.add_fpreview(title, paths)

        return super().get_tab()

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

        super().__init__({}, outdir, name, basedir=basedir)

        self.name = name
        self._files = files
        self._stats_paths = stats_paths
