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

from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import HTMLReport, _IntroTable
from statscollectlibs.htmlreport.tabs import _CapturedOutputTabBuilder, _SPECjbb2015TabBuilder
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.result import RORawResult, LoadedResult

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
                 logpath: Path | None = None):
        """
        Initialize a class instance.

        Args:
            rsts: List of of test results objects ('RORawResult') to generate the HTML report for.
            outdir: The output directory to place the HTML report in.
            logpath: The HTML report generation log file path.
        """

        self.rsts = rsts
        self.outdir = outdir
        self.logpath = logpath

        # Users can change this to 'True' to copy all the raw test results into the output
        # directory.
        self.copy_raw = False

        # The loaded test results for the raw test results.
        self._lrsts: list[LoadedResult.LoadedResult] = []

        self._intro_tbl: _IntroTable.IntroTable

        # Paths to (copied) raw test result directories in the output directory, and logs/workload
        # data sub-directories in the output directory. The dictionary is indexed by report ID.
        self._raw_paths: dict[str, Path] = {}
        self._raw_logs_paths: dict[str, Path] = {}
        self._raw_wldata_paths: dict[str, Path] = {}

        # Build the loaded test result objects, but do not load them yet.
        for res in self.rsts:
            self._lrsts.append(LoadedResult.LoadedResult(res))

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

        row = self._intro_tbl.create_row(label)

        for reportid, path in valid_paths.items():
            row.add_cell(reportid, label, link=path)

    def _generate_intro_table(self, rsts: list[RORawResult.RORawResult]):
        """
        Generate an intro table for test results in 'rsts'.

        Args:
            rsts: A list of raw result objects.
        """

        self._intro_tbl = _IntroTable.IntroTable()
        descr = "The command run during statistics collection."
        cmd_row = self._intro_tbl.create_row("Command", hovertext=descr)
        for res in rsts:
            cmd_row.add_cell(res.reportid, res.info.get("cmd"))

        # Add tool information.
        tinfo_row = self._intro_tbl.create_row("Data Collection Tool")
        for res in rsts:
            tool_info = f"{res.info['toolname'].capitalize()} version {res.info['toolver']}"
            tinfo_row.add_cell(res.reportid, tool_info)

        # Add run date.
        date_row = self._intro_tbl.create_row("Collection Date")
        for res in rsts:
            date_row.add_cell(res.reportid, res.info.get("date"))

        # Add duration.
        date_row = self._intro_tbl.create_row("Duration")
        for res in rsts:
            date_row.add_cell(res.reportid, res.info.get("duration"))

        # Add links to the raw directories.
        if self.copy_raw:
            self._add_intro_tbl_links("Raw result", self._raw_paths)

        # Add links to the raw statistics directories.
        self._add_intro_tbl_links("Workload data", self._raw_wldata_paths)

        # Add links to the logs directories.
        self._add_intro_tbl_links("Logs", self._raw_logs_paths)

    def _get_results_tab(self, tabs_dir: Path) -> _Tabs.CTabDC:
        """
        Create and return the results tab object.

        Args:
            tabs_dir: Path to the directory where the tabs will be stored.

        Returns:
            _Tabs.CTabDC: The resulting container tab object.
        """

        wltypes = {}
        wltypes_set = set()

        for res in self.rsts:
            wltypes[res.reportid] = res.wltype
            wltypes_set.add(res.wltype)

        if len(wltypes_set) > 1:
            msgs = []
            for res in self.rsts:
                msgs.append(f"{res.reportid}: {wltypes[res.reportid]} "
                            f"({RORawResult.SUPPORTED_WORKLOADS[res.wltype]})")
            msg = " * " + "\n * ".join(msgs)
            wltype = "generic"
            _LOG.warning("Multiple workload types detected, assuming a generic workload:\n%s", msg)
        else:
            wltype = next(iter(wltypes_set))

        _LOG.info("Workload type: %s (%s)",
                  wltypes[res.reportid], RORawResult.SUPPORTED_WORKLOADS[res.wltype])

        if wltype == "generic":
            return _CapturedOutputTabBuilder.CapturedOutputTabBuilder(self._lrsts, tabs_dir,
                                                                      basedir=self.outdir).get_tab()
        if wltype == "specjbb2015":
            return _SPECjbb2015TabBuilder.SPECjbb2015TabBuilder(self._lrsts, tabs_dir,
                                                                basedir=self.outdir).get_tab()

        raise Error(f"BUG: unsupported workload type '{wltype}'")

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
        """Generate the HTML report."""

        rep = HTMLReport.HTMLReport(self.outdir, self.logpath)

        results_tab = self._get_results_tab(rep.tabs_dir)
        tabs = [results_tab] if results_tab else None

        for res in self.rsts:
            self._raw_paths[res.reportid] = self.outdir / f"raw-{res.reportid}"
        self._raw_logs_paths, self._raw_wldata_paths = self._copy_raw_data()

        self._generate_intro_table(self.rsts)
        rep.generate_report(tabs=tabs, lrsts=self._lrsts, intro_tbl=self._intro_tbl,
                            title="stats-collect report")
