# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the base class for data tabs in the "SysInfo" container tab.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from typing import TypedDict
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs import _DTabBuilder

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class FilePreviewInfoTypedDict(TypedDict):
    """
    A dictionary containing information about a file preview. A file preview is an element of a
    D-tab that displays the contents of a file for each raw result, and possibly a diff between
    the files. For example, the "pepc" D-tab of the "SysInfo" tab includes file previews for
    "pepc cstates info", "pepc pstates info", and so on. Each file preview includes the "pepc
    <something> info" output, and when multiple results are included in a single report, each
    preview will include multiple files, and possibly a diff between them.

    Attributes:
        title: The title of the file preview.
        path: The path to the file preview file relative to the raw result path.
        diff: Whether a diff should be generated.
    """

    title: str
    path: Path
    diff: bool

class SysInfoDTabBuilderBase(_DTabBuilder.DTabBuilder):
    """
    Base class for data tabs in the "SysInfo" container tab.
    """

    def __init__(self, name: str, outdir: Path, fpwis: list[FilePreviewInfoTypedDict],
                 stats_paths: dict[str, Path], basedir: Path | None = None):
        """
        Class constructor.

        Args:
            name: The name of the generated D-tab.
            outdir: The output directory path where the D-tab files should be placed.
            fpwis: A list of file preview information dictionaries describing the file previews
                   to be included in the D-tab.
            stats_paths: A dictionary mapping report IDs to raw statistics directory paths.
            basedir: The report base directory path, defaults to 'outdir'.

        The expected format for 'files' is '{Title: FilePath}' where 'Title' is the title for the
        raw statistics file and 'FilePath' is the path to the raw statistics file relative to the
        statistics directory ('stats_paths').
        """

        super().__init__({}, outdir, name, basedir=basedir)

        self.name = name
        self._fpws = fpwis
        self._stats_paths = stats_paths

    @staticmethod
    def _compat_adjust_paths(paths: dict[str, Path]) -> dict[str, Path]:
        """
        Adjust paths to some of the sysinfo statistics files that changed in 'stats-collect'
        version 1.0.39. For example, "dmidecode.raw.txt" became "dmidecode.before.raw.txt".
        Basically, all files got either "before" or "after" suffixes. This ensures that
        'stats-collect' version 1.0.39+ supports raw results from 'stats-collect' version 1.0.38
        and older.

        TODO: remove in 2026.

        Args:
            paths: The raw sysinfo statistics file paths for each raw result (same as in
                   'add_fpreview()).

        Returns:
            The adjusted version of 'paths'.
        """

        new_paths = paths.copy()

        for reportid, path in paths.items():
            if path.exists():
                continue

            if path.name.endswith(".after.raw.txt"):
                suffix = ".after.raw.txt"
            elif path.name.endswith(".before.raw.txt"):
                suffix = ".before.raw.txt"
            else:
                # Not our concern. The compatibility issue is about ".raw.txt" names changing to
                # ".before.raw.txt" or ".after.raw.txt".
                continue

            # Change file name from "xyz.after.raw.txt" to "xyz.raw.txt".
            new_name = path.name[:-len(suffix)] + ".raw.txt"
            new_path = path.parent / new_name
            if new_path.exists():
                new_paths[reportid] = new_path

        return new_paths

    def get_tab(self) -> _Tabs.BuiltDTab:
        """
        Generate and returns a D-tab for the "Sysinfo" C-tab.

        Returns:
            The data tab object.
        """

        paths = {}
        for fpwi in self._fpws:
            for reportid, stats_path in self._stats_paths.items():
                paths[reportid] = stats_path / fpwi["path"]

            paths = self._compat_adjust_paths(paths)

            try:
                self.add_fpreview(fpwi["title"], paths, diff=fpwi["diff"])
            except ErrorNotFound as err:
                _LOG.debug("Skipping file preview '%s' in the '%s' tab: %s",
                           fpwi["title"], self.name, err.indent(2))
                continue
            except Error as err:
                errmsg = err.indent(2)
                _LOG.warning("Skipping file preview '%s' in the '%s' tab: An error occurred during "
                             "file preview generation:\n%s", fpwi["title"], self.name, errmsg)
                continue

        return super().get_tab()
