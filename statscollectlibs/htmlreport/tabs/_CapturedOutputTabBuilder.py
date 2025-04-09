# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the tab builder for the "Captured Output" tab, which just shows and compares the stdout and
stderr of the workload(s).
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport.tabs import FilePreviewBuilder, BuiltTab, _DTabBuilder
from statscollectlibs.result.LoadedResult import LoadedResult

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

# The number of lines at the start and end of captured output files to preserve. Lines outside of
# those limits will be trimmed and will not be copied to the report directory.
_MAX_FILE_START = 128
_MAX_FILE_END = 256

class CapturedOutputTabBuilder():
    """
    The tab builder class for the "Captured Output" tab, which just shows and compares the stdout
    and stderr of the workload(s).
    """

    name = "Captured Output"

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: List of loaded test result objects to include in the tab.
            outdir: Output directory where the sub-directory for tab data files will be created.
            basedir: Base directory of the report. All HTML links in the tab will be made relative
                     to this directory. Defaults to 'outdir' if not provided.
        """

        self._lrsts = lrsts
        self._basedir = basedir if basedir else outdir
        self._outdir = outdir / _DTabBuilder.get_fsname(self.name)

    def _write_lines(self, lines: list[str], dstpath: Path) -> None:
        """
        Write the provided lines to the specified destination path.

        Args:
            lines: A list of strings representing the lines to be written to the file.
            dstpath: The destination path where the lines will be written.
        """

        try:
            dstpath.parent.mkdir(parents=True, exist_ok=True)
            with open(dstpath, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            raise Error(f"unable to write trimmed captured output file at '{dstpath}':\n"
                        f"{errmsg}") from None

    def _trim_file_lines(self, lines: list[str], top: int, bottom: int) -> list[str]:
        """
        Trim the provided list of lines to include only the first 'top' lines and the last 'bottom'
        lines.

        Args:
            lines: The lines of a file to be trimmed.
            top: Number of lines to preserve from the start of the file.
            bottom: Number of lines to preserve from the end of the file.

        Returns:
            A list of strings representing the trimmed lines of the file.
        """

        trim_notice_lines = [
            "==========================\n",
            "FILE CONTENTS REMOVED HERE\n",
            "==========================\n"
        ]

        # If the total number of lines is less than or equal to the sum of 'top' and 'bottom',
        # no trimming is necessary.
        if len(lines) <= top + bottom:
            trimmed_lines = lines
        else:
            # Preserve the top 'top' lines, add a notice, and preserve the bottom 'bottom' lines.
            trimmed_lines = lines[:top] + trim_notice_lines + lines[-bottom:]

        return trimmed_lines

    def build_tab(self) -> BuiltTab.BuiltCTab:
        """
        Build and return the tab object with file previews of the captured 'stdout' and 'stderr'
        logs from the 'stats-collect start' process.

        Returns:
            BuiltTab.BuiltCTab: A built C-tab object containing a D-tab object that includes the
            file previews.

        Raises:
            Error: If there is an issue reading or processing the captured output files.
        """

        _LOG.info("Generating '%s' tab", self.name)

        fpbuilder = FilePreviewBuilder.FilePreviewBuilder(self._outdir, basedir=self._basedir)
        fpreviews: list[BuiltTab.BuiltDTabFilePreview] = []
        trimmed_reportids: set[str] = set()

        for stream_name in ("stdout", "stderr"):
            files: dict[str, Path] = {}

            for lres in self._lrsts:
                if stream_name not in lres.res.info:
                    continue

                resdir = self._outdir / lres.reportid
                relative_path = lres.res.info[stream_name]
                if not relative_path:
                    continue

                srcpath = lres.res.dirpath / relative_path
                if not srcpath.exists():
                    continue

                try:
                    with open(srcpath, "r", encoding="utf-8") as fobj:
                        lines = fobj.readlines()
                except OSError as err:
                    raise Error(f"Failed to open captured output file at '{srcpath}':\n"
                                f"{Error(str(err)).indent(2)}") from None

                trimmed_lines = self._trim_file_lines(lines, _MAX_FILE_START, _MAX_FILE_END)

                if len(trimmed_lines) < len(lines):
                    trimmed_reportids.add(lres.reportid)
                    dstpath = resdir / f"trimmed-{srcpath.name}"
                else:
                    dstpath = resdir / srcpath.name

                self._write_lines(trimmed_lines, dstpath)
                files[lres.reportid] = dstpath

            if files:
                fpreviews.append(fpbuilder.build_fpreview(stream_name, files))

        if not fpreviews:
            return BuiltTab.BuiltCTab(self.name, tabs=[])

        if trimmed_reportids:
            # Add a notice about trimmed contents to the HTML report.
            #
            # Convert the set of report IDs into a list which maintains the order of reports used
            # elsewhere.
            trimmed = [lres.reportid for lres in self._lrsts if lres.reportid in trimmed_reportids]
            msg = f"Note - the outputs of the following results have been trimmed to save time " \
                  f"during report generation: {', '.join(trimmed)}"
            alerts = [msg]
        else:
            alerts = []

        dtab = BuiltTab.BuiltDTab(self.name, fpreviews=fpreviews, alerts=alerts)
        return BuiltTab.BuiltCTab(self.name, tabs=[dtab])
