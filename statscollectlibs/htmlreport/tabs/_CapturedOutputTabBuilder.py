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

# TODO: finish adding type hints to this module.
from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport.tabs import FilePreviewBuilder, _BuiltTab, _DTabBuilder
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

    Public methods overview:
     * 'get_tab()' - Generate a '_BuiltTab.BuiltDTab' instance containing file previews of the captured
                     'stdout' and 'stderr' logs from 'stats-collect start'.
    """

    name = "Captured Output"

    def _write_lines(self, lines, dstpath):
        """Helper function for 'generate_captured_output_tab()'."""

        try:
            dstpath.parent.mkdir(parents=True, exist_ok=True)
            with open(dstpath, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except OSError as err:
            errmsg = Error(str(err)).indent(2)
            errmsg = f"unable to write trimmed captured output file at '{dstpath}':\n{errmsg}"
            raise Error(errmsg) from None

    def _trim_lines(self, lines, top, bottom):
        """
        Copy the file at 'srcpath' to 'dstpath' and removes all but the top 'top' lines and bottom
        'bottom' lines. Return a boolean representing if the file was trimmed or not.
        """

        trim_notice_lines = [
            "==========================\n",
            "FILE CONTENTS REMOVED HERE\n",
            "==========================\n"
            ]

        if len(lines) <= top + bottom:
            trimmed_lines = lines
        else:
            trimmed_lines = lines[:top] + trim_notice_lines + lines[-bottom:]

        return trimmed_lines

    def get_tab(self):
        """
        Return a '_BuiltTab.BuiltDTab' instance containing file previews of the captured 'stdout' and
        'stderr' logs from 'stats-collect start'.
        """

        _LOG.info("Generating '%s' tab.", self.name)

        fpbuilder = FilePreviewBuilder.FilePreviewBuilder(self._outdir, basedir=self._basedir)
        fpreviews = []
        trimmed_lrsts = set()
        for stream_name in ("stdout", "stderr"):
            files = {}
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
                    with open(srcpath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except OSError as err:
                    raise Error(f"unable to open captured output file at '{srcpath}':\n"
                                f"{Error(str(err)).indent(2)}") from None

                trimmed_lines = self._trim_lines(lines, _MAX_FILE_START, _MAX_FILE_END)

                if len(trimmed_lines) < len(lines):
                    trimmed_lrsts.add(lres.reportid)
                    dstpath = resdir / f"trimmed-{srcpath.name}"
                else:
                    dstpath = resdir / srcpath.name

                self._write_lines(trimmed_lines, dstpath)

                files[lres.reportid] = dstpath

            if files:
                fpreviews.append(fpbuilder.build_fpreview(stream_name, files))

        if not fpreviews:
            return None

        if trimmed_lrsts:
            # Convert the set of report IDs into a list which maintains the order of reports used
            # elsewhere.
            trimmed = [lres.reportid for lres in self._lrsts if lres.reportid in trimmed_lrsts]
            msg = f"Note - the outputs of the following results have been trimmed to save time " \
                  f"during report generation: {', '.join(trimmed)}"
            alerts = [msg]
        else:
            alerts = []

        dtab = _BuiltTab.BuiltDTab(self.name, fpreviews=fpreviews, alerts=alerts)
        return _BuiltTab.BuiltCTab(self.name, tabs=[dtab])

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        The class constructor. The arguments are as follows.
         * lrsts - a list of loaded test result objects for which data should be included in the
                   tab.
         * outdir - the output directory in which to create the sub-directory for the container tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._lrsts = lrsts
        self._basedir = basedir if basedir else outdir
        self._outdir = outdir / _DTabBuilder.get_fsname(self.name)
