# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""Provide a capability of generating 'stats-collect' HTML reports."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
from pepclibs.helperlibs import Logging
from statscollectlibs.htmlreport import HTMLReport, IntroTable
from statscollectlibs.htmlreport.tabs import _CapturedOutputTabBuilder, _SPECjbb2015TabBuilder
from statscollectlibs.htmlreport.tabs import BuiltTab
from statscollectlibs.result import RORawResult, LoadedResult

if typing.TYPE_CHECKING:
    from typing import cast

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class StatsCollectHTMLReport:
    """
    A class for for generating 'stats-collect' HTML reports.

    The reports consist of the statistics tabs and the "results" tab, which may be
    workload-specific. The former tabs are implemented and rendered by the 'HTMLReport' class, the
    latter are implemented by and rendered by this class.
    """

    def __init__(self,
                 rsts: list[RORawResult.RORawResult],
                 outdir: Path,
                 cpus: list[int] | None = None,
                 logpath: Path | None = None):
        """
        Initialize a class instance.

        Args:
            rsts: List of of test results objects ('RORawResult') to generate the HTML report for.
            outdir: The output directory to place the HTML report in.
            cpus: List of CPU numbers to include in the report along with the system-wide
                  statistics.
            logpath: The HTML report generation log file path.
        """

        self.rsts = rsts
        self.outdir = outdir
        self.cpus = cpus
        self.logpath = logpath

        # Users can change this to 'True' to copy all the raw test results into the output
        # directory.
        self.copy_raw = False

        # The loaded test results for the raw test results.
        self._lrsts: list[LoadedResult.LoadedResult] = []

        self._intro_tbl: IntroTable.IntroTable

        # Paths to (copied) raw test result directories in the output directory, and logs/workload
        # data sub-directories in the output directory. The dictionary is indexed by report ID.
        self._raw_paths: dict[str, Path] = {}
        self._raw_logs_paths: dict[str, Path] = {}
        self._raw_wldata_paths: dict[str, Path] = {}

        # Build the loaded test result objects, but do not load them yet.
        for res in self.rsts:
            lres = LoadedResult.LoadedResult(res, cpus=cpus)
            self._lrsts.append(lres)

    def _add_intro_tbl_links(self, label: str, paths: dict[str, Path]):
        """
        Add links to the intro table.

        Args:
            label: The label that will be shown in the intro table for these links.
            paths: A dictionary in the format {Report ID: Path to Link to}.
        """

        valid_paths = {}
        for res in self.rsts:
            # Do not add links for 'label' if 'paths' does not contain a link for every result or
            # if a path points to somewhere outside of the report directory.
            if res.reportid not in paths:
                return
            path = paths[res.reportid]
            if path is None or self.outdir not in path.parents:
                return

            # If the path points to inside the report directory then make it relative to the output
            # directory so that the output directory is relocatable. That is, the whole directory
            # can be moved or copied without breaking the link.
            valid_paths[res.reportid] = path.relative_to(self.outdir)

        row = self._intro_tbl.add_row(label)

        for reportid, path in valid_paths.items():
            row.add_cell(reportid, label, link=path)

    def _init_intro_table(self, rsts: list[RORawResult.RORawResult]):
        """
        Initialize the intro table and populate it with data. The intro table is located at the top
        of the HTML report and provides general information, such as the command used for
        statistics collection, the collection date, and more.

        Args:
            rsts: List of raw results to be described in the intro table.
        """

        self._intro_tbl = IntroTable.IntroTable()
        descr = "The command run during statistics collection."
        cmd_row = self._intro_tbl.add_row("Command", hovertext=descr)
        for res in rsts:
            cmd_row.add_cell(res.reportid, res.info.get("cmd"))

        # Add tool information.
        tinfo_row = self._intro_tbl.add_row("Data Collection Tool")
        for res in rsts:
            tool_info = f"{res.info['toolname'].capitalize()} version {res.info['toolver']}"
            tinfo_row.add_cell(res.reportid, tool_info)

        # Add run date.
        date_row = self._intro_tbl.add_row("Collection Date")
        for res in rsts:
            date_row.add_cell(res.reportid, res.info.get("date"))

        # Add duration.
        date_row = self._intro_tbl.add_row("Duration")
        for res in rsts:
            date_row.add_cell(res.reportid, res.info.get("duration"))

        # Add links to the raw directories.
        if self.copy_raw:
            self._add_intro_tbl_links("Raw result", self._raw_paths)

        # Add links to the raw statistics directories.
        self._add_intro_tbl_links("Workload data", self._raw_wldata_paths)

        # Add links to the logs directories.
        self._add_intro_tbl_links("Logs", self._raw_logs_paths)

    def _build_results_tab(self, tabdir: Path) -> BuiltTab.BuiltCTab:
        """
        Build the "Results" tab (generate all the tab files for the HTML report)

        Args:
            tabdir: Path to the directory where all the "Results" tab files will be stored.

        Returns:
            The built container tab (C-Tab) object representing the built "Results" tab.
        """

        wlnames = {}
        wlnames_set = set()

        for res in self.rsts:
            wlnames[res.reportid] = res.wlname
            wlnames_set.add(res.wlname)

        if len(wlnames_set) > 1:
            msgs = []
            for res in self.rsts:
                if res.wlname in RORawResult.KNOWN_WORKLOADS:
                    descr = f"{RORawResult.KNOWN_WORKLOADS[res.wlname]}"
                else:
                    descr = "Unknown workload"
                msgs.append(f"{res.reportid}: {wlnames[res.reportid]} {descr}")
            msg = " * " + "\n * ".join(msgs)
            wlname = "generic"
            _LOG.warning("Multiple workload types detected, assuming a generic workload:\n%s", msg)
        else:
            wlname = next(iter(wlnames_set))

        if res.wlname in RORawResult.KNOWN_WORKLOADS:
            _LOG.info("Workload type: %s (%s)",
                    wlnames[res.reportid], RORawResult.KNOWN_WORKLOADS[res.wlname])

        if wlname == "specjbb2015":
            specjbb_bldr = _SPECjbb2015TabBuilder.SPECjbb2015TabBuilder(self._lrsts, tabdir,
                                                                        basedir=self.outdir)
            _ctab = specjbb_bldr.build_tab()
            if typing.TYPE_CHECKING:
                ctab = cast(BuiltTab.BuiltCTab, _ctab)
            else:
                ctab = _ctab
        else:
            capout_bldr = _CapturedOutputTabBuilder.CapturedOutputTabBuilder(self._lrsts, tabdir,
                                                                             basedir=self.outdir)
            ctab = capout_bldr.build_tab()

        return ctab

    def _copy_raw_data(self):
        """Copy raw test results or their parts to the output directory."""

        logs_paths = {}
        wldata_paths = {}

        for res in self.rsts:
            dstdir = self._raw_paths[res.reportid]

            if self.copy_raw:
                res.copy(dstdir)
            else:
                res.copy_logs(dstdir)
                res.link_wldata(dstdir)

            if res.logs_path:
                logs_paths[res.reportid] = dstdir / res.logs_path.name
            if res.wldata_path:
                wldata_paths[res.reportid] = dstdir / res.wldata_path.name

        return logs_paths, wldata_paths

    def generate(self):
        """Generate the stats-collect HTML report."""

        title="stats-collect report"
        rep = HTMLReport.HTMLReport(self._lrsts, title, self.outdir, logpath=self.logpath)

        results_tab = self._build_results_tab(rep.tabs_dir)

        # Do not include the results tab if it is empty (no sub-tabs).
        tabs = [results_tab] if results_tab.tabs else None

        for res in self.rsts:
            self._raw_paths[res.reportid] = self.outdir / f"raw-{res.reportid}"
        self._raw_logs_paths, self._raw_wldata_paths = self._copy_raw_data()

        self._init_intro_table(self.rsts)
        rep.generate_report(tabs=tabs, intro_tbl=self._intro_tbl)
