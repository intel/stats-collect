# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the API for generating 'stats-collect' HTML reports."""

import logging
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import HTMLReport, _IntroTable
from statscollectlibs.htmlreport.tabs import _Tabs, FilePreviewBuilder

_LOG = logging.getLogger()

class StatsCollectReport:
    """
    This class provides the API for generating 'stats-collect' HTML reports.

    This class uses the generic report class 'HTMLReport' to implement the tabs
    which are specific to 'stats-collect' HTML reports.
    """

    def _trim_file(self, srcpath, dstpath, top, bottom):
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

        try:
            with open(srcpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) <= top + bottom:
                    trimmed_lines = lines
                else:
                    trimmed_lines = lines[:top] + trim_notice_lines + lines[-bottom:]
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"unable to open captured output file at '{srcpath}':\n{msg}") from None

        try:
            dstpath.parent.mkdir(parents=True, exist_ok=True)
            with open(dstpath, "w", encoding="utf-8") as f:
                f.writelines(trimmed_lines)
        except OSError as err:
            msg = Error(err).indent(2)
            msg = f"unable to write trimmed captured output file at '{dstpath}':\n{msg}"
            raise Error(msg) from None

        return len(trimmed_lines) < len(lines)

    def generate_captured_output_tab(self, rsts, outdir):
        """Generate a container tab containing the output captured in 'stats-collect start'."""

        tab_title = "Captured Output"

        _LOG.info("Generating '%s' tab.", tab_title)

        files = {}
        trimmed_rsts = []
        for ftype in ("stdout", "stderr"):
            fp = rsts[0].info.get(ftype)

            if not fp or not all(((res.dirpath / fp).exists() for res in rsts)):
                continue

            srcfp = Path(fp)
            dstfp = srcfp.parent / f"trimmed-{srcfp.name}"
            for res in rsts:
                trimmed = self._trim_file(res.dirpath / srcfp,
                                          outdir / res.reportid / dstfp, 16, 32)
                if trimmed:
                    trimmed_rsts.append(res.reportid)

            files[ftype] = dstfp

        fpbuilder = FilePreviewBuilder.FilePreviewBuilder(outdir)
        fpreviews = fpbuilder.build_fpreviews({res.reportid: outdir / res.reportid for res in rsts},
                                               files)

        if not fpreviews:
            return None

        if trimmed_rsts:
            msg = f"Note - the outputs of the following results have been trimmed to save time " \
                  f"during report generation: {', '.join(trimmed_rsts)}"
            alerts = (msg,)
        else:
            alerts = []

        dtab = _Tabs.DTabDC(tab_title, fpreviews=fpbuilder.fpreviews, alerts=alerts)
        return _Tabs.CTabDC(tab_title, tabs=[dtab])

    def _generate_intro_table(self, rsts):
        """
        Helper function for 'generate_stc_report()'. Generates an intro table based on results in
        'rsts'.
        """

        intro_tbl = _IntroTable.IntroTable()
        cmd_row = intro_tbl.create_row("Command", "The command run during statistics collection.")
        for res in rsts:
            cmd_row.add_cell(res.reportid, res.info.get("cmd"))

        # Add tool information.
        tinfo_row = intro_tbl.create_row("Data Collection Tool")
        for res in rsts:
            tool_info = f"{res.info['toolname'].capitalize()} version {res.info['toolver']}"
            tinfo_row.add_cell(res.reportid, tool_info)

        # Add run date.
        date_row = intro_tbl.create_row("Collection Date")
        for res in rsts:
            date_row.add_cell(res.reportid, res.info.get("date"))

        # Add duration.
        date_row = intro_tbl.create_row("Duration")
        for res in rsts:
            date_row.add_cell(res.reportid, res.info.get("duration"))

        return intro_tbl

    def generate(self):
        """Generate a 'stats-collect' report from the results 'rsts' with 'outdir'."""

        HTMLReport.reportids_dedup(self.rsts)

        rep = HTMLReport.HTMLReport(self.outdir)
        stdout_tab = self.generate_captured_output_tab(self.rsts, self.outdir)
        tabs = [stdout_tab] if stdout_tab else None
        intro_tbl = self._generate_intro_table(self.rsts)
        rep.generate_report(tabs=tabs, rsts=self.rsts, intro_tbl=intro_tbl,
                            title="stats-collect report")

    def __init__(self, rsts, outdir):
        """Class constructor."""

        self.rsts = rsts
        self.outdir = outdir