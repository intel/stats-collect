# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""API for generating 'stats-collect' HTML reports."""

import logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport import HTMLReport, _IntroTable
from statscollectlibs.htmlreport.tabs import _CapturedOutputTabBuilder, _SPECjbb2015TabBuilder
from statscollectlibs.rawresultlibs import RORawResult

_LOG = logging.getLogger()

class StatsCollectHTMLReport:
    """
    API for generating 'stats-collect' HTML reports.

    'stats-collect' HTML reports consist of the statistics tabs and the "results" tab, which may
    be workload-specific. The former tabs are implemented and rendered by the 'HTMLReport' class,
    the latter are implemented by and rendered by this class.
    """

    def _add_intro_tbl_links(self, label, paths):
        """
        Add links in 'paths' to the 'self._intro_tbl' dictionary. The arguments are as follows.
          * label - the label that will be shown in the intro table for these links.
          * paths - dictionary in the format {Report ID: Path to Link to.
        """

        valid_paths = {}
        for res in self.rsts:
            reportid = res.reportid
            path = paths.get(reportid)

            # Do not add links for 'label' if 'paths' does not contain a link for every result or
            # if a path points to somewhere outside of the report directory.
            if path is None or self.outdir not in path.parents:
                return

            # If the path points to inside the report directory then make it relative to the output
            # directory so that the output directory is relocatable. That is, the whole directory
            # can be moved or copied without breaking the link.
            valid_paths[reportid] = path.relative_to(self.outdir)

        row = self._intro_tbl.create_row(label)

        for reportid, path in valid_paths.items():
            row.add_cell(reportid, label, link=path)

    def _generate_intro_table(self, rsts):
        """Generate an intro table based on results in 'rsts'."""

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

    def _get_results_tab(self, tabs_dir):
        """Create and return the results tab object."""

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
            _LOG.warning("multiple workload types detected, assuming a generic workload:\n%s", msg)
        else:
            wltype = next(iter(wltypes_set))

        _LOG.info("Workload type: %s (%s)",
                  wltypes[res.reportid], RORawResult.SUPPORTED_WORKLOADS[res.wltype])
        if wltype == "generic":
            tbldr = _CapturedOutputTabBuilder.CapturedOutputTabBuilder(self.rsts, tabs_dir,
                                                                       basedir=self.outdir)
            return tbldr.get_tab()
        if wltype == "specjbb2015":
            tbldr = _SPECjbb2015TabBuilder.SPECjbb2015TabBuilder(self.rsts, tabs_dir,
                                                                 basedir=self.outdir)
            return tbldr.get_tab()

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
            if self.copy_raw and res.wldata_path:
                wldata_paths[res.reportid] = dstdir / res.wldata_path.name

        return logs_paths, wldata_paths

    def generate(self):
        """Generate the HTML report."""

        HTMLReport.reportids_dedup(self.rsts)
        rep = HTMLReport.HTMLReport(self.outdir, self.logpath)

        results_tab = self._get_results_tab(rep.tabs_dir)
        tabs = [results_tab] if results_tab else None

        for res in self.rsts:
            self._raw_paths[res.reportid] = self.outdir / f"raw-{res.reportid}"
        self._raw_logs_paths, self._raw_wldata_paths = self._copy_raw_data()

        self._generate_intro_table(self.rsts)
        rep.generate_report(tabs=tabs, rsts=self.rsts, intro_tbl=self._intro_tbl,
                            title="stats-collect report")

    def __init__(self, rsts, outdir, logpath=None):
        """
        Class constructor. The arguments are as follows.
          * rsts - an iterable collection of test results objects ('RORawResult') to generate the
                   HTML report for.
          * outdir - the output directory to place the HTML report to.
          * logpath - the HTML report generation log file path.
        """

        self.rsts = rsts
        self.outdir = outdir
        self.logpath = logpath

        # Users can change this to 'True' to copy all the raw test results into the output
        # directory.
        self.copy_raw = False

        self._intro_tbl = None
        # Paths to (copied) raw test result directories in the output directory, and logs/workload
        # data sub-directories in the output directory. The dictionary is indexed by report ID.
        self._raw_paths = {}
        self._raw_logs_paths = {}
        self._raw_wldata_paths = {}
