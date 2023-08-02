# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the 'Captured Output' tab.
"""

import logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.defs import DefsBase
from statscollectlibs.htmlreport.tabs import FilePreviewBuilder, _Tabs

_LOG = logging.getLogger()

class CapturedOutputTabBuilder():
    """
    This class provides the capability of populating the 'Captured Output' tab.

    Public methods overview:
     * 'get_tab()' - Generate a '_Tabs.DTabDC' instance containing file previews of the captured
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
            msg = Error(err).indent(2)
            msg = f"unable to write trimmed captured output file at '{dstpath}':\n{msg}"
            raise Error(msg) from None

    def _trim_lines(self, lines, top, bottom):
        """
        Helper function for 'generate_captured_output_tab()'. Copies the file at 'srcpath' to
        'dstpath' and removes all but the top 'top' lines and bottom 'bottom' lines. Returns a
        boolean representing if the file was trimmed or not.
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
        Returns a '_Tabs.DTabDC' instance containing file previews of the captured 'stdout' and
        'stderr' logs from 'stats-collect start'.
        """

        _LOG.info("Generating '%s' tab.", self.name)

        fpbuilder = FilePreviewBuilder.FilePreviewBuilder(self._outdir, basedir=self._basedir)
        fpreviews = []
        trimmed_rsts = set()
        for ftype in ("stdout", "stderr"):
            files = {}
            for res in self._rsts:
                resdir = self._outdir / res.reportid
                fp = res.info.get(ftype)
                if not fp:
                    continue

                srcpath = res.dirpath / fp
                if not srcpath.exists():
                    continue

                try:
                    with open(srcpath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except OSError as err:
                    raise Error(f"unable to open captured output file at '{srcpath}':\n"
                                f"{Error(err).indent(2)}") from None

                trimmed_lines = self._trim_lines(lines, 16, 32)

                dstpath = resdir / f"trimmed-{srcpath.name}"
                if len(trimmed_lines) < len(lines):
                    trimmed_rsts.add(res.reportid)

                self._write_lines(trimmed_lines, dstpath)

                files[res.reportid] = dstpath

            if files:
                fpreviews.append(fpbuilder.build_fpreview(ftype, files))

        if not fpreviews:
            return None

        if trimmed_rsts:
            # Convert the set of report IDs into a list which maintains the order of reports used
            # elsewhere.
            trimmed_rsts = [res.reportid for res in self._rsts if res.reportid in trimmed_rsts]
            msg = f"Note - the outputs of the following results have been trimmed to save time " \
                  f"during report generation: {', '.join(trimmed_rsts)}"
            alerts = (msg,)
        else:
            alerts = []

        dtab = _Tabs.DTabDC(self.name, fpreviews=fpreviews, alerts=alerts)
        return _Tabs.CTabDC(self.name, tabs=[dtab])

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Adding a "Captured Output" tab will create an 'CapturedOutput'
        sub-directory and store 'stdout' and 'stderr' log files in it. Arguments are as follows:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
         * outdir - the output directory in which to create the sub-directory for the built tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._rsts = rsts
        self._basedir = basedir if basedir else outdir
        self._outdir = outdir / DefsBase.get_fsname(self.name)
