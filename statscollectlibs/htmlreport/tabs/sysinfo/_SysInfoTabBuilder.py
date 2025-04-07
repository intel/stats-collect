# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>


"""
API to build the "SysInfo" container tab, which includes various system information such as "dmesg"
contents and more. Building the tab involves parsing raw system information files and generating all
necessary files for the HTML report.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import _BuiltTab
from statscollectlibs.htmlreport.tabs.sysinfo import (_CPUFreqDTabBuilder, _CPUIdleDTabBuilder,
    _DMIDecodeDTabBuilder, _DmesgDTabBuilder, _EPPDTabBuilder, _LspciDTabBuilder, _MiscDTabBuilder,
    _PepcDTabBuilder, _ThermalThrottleDTabBuilder, _TurbostatDTabBuilder)

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class SysInfoTabBuilder:
    """
    Build the "SysInfo" container tab, which includes various system information such as "dmesg"
    contents. Building the tab involves parsing raw system information files and generating all
    necessary files for the HTML report.
    """

    name = "SysInfo"
    stnames = ["sysinfo"]

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        The class constructor.

        Args:
            lrsts: list of loaded test result objects to build the SysInfo tab for.
            outdir: The output directory path where the SysInfo tab files should be placed.
            basedir: The report base directory path, defaults to 'outdir'.
        """

        self._lrsts = lrsts
        self._outdir = outdir
        self._basedir = basedir if basedir else outdir

    def build_tab(self) -> _BuiltTab.BuiltCTab:
        """
        Build the SysInfo tab and its sub-tabs. Parse the required raw system information files and
        generate the necessary files for the HTML report, such as diffs.

        Returns:
            The built SysInfo container tab (C-tab) object.
        """

        stats_paths: dict[str, Path] = {}

        for lres in self._lrsts:
            if lres.res.stats_path:
                stats_paths[lres.reportid] = lres.res.stats_path

        if not stats_paths:
            # If there are no statistics at all, the class instance should not have been even
            # created.
            raise Error("BUG: No statistics in the raw results")

        tab_builders = (_PepcDTabBuilder.PepcDTabBuilder,
                        _TurbostatDTabBuilder.TurbostatDTabBuilder,
                        _ThermalThrottleDTabBuilder.ThermalThrottleDTabBuilder,
                        _DMIDecodeDTabBuilder.DMIDecodeDTabBuilder,
                        _EPPDTabBuilder.EPPDTabBuilder,
                        _CPUFreqDTabBuilder.CPUFreqDTabBuilder,
                        _CPUIdleDTabBuilder.CPUIdleDTabBuilder,
                        _DmesgDTabBuilder.DmesgDTabBuilder,
                        _LspciDTabBuilder.LspciDTabBuilder,
                        _MiscDTabBuilder.MiscDTabBuilder)

        tabs = []

        sysinfo_dir = self._outdir / self.name
        for tab_builder in tab_builders:
            tbldr = tab_builder(sysinfo_dir, stats_paths, basedir=self._basedir)

            _LOG.info("Generating '%s' %s tab.", tbldr.name, self.name)
            try:
                tabs.append(tbldr.get_tab())
            except Error as err:
                _LOG.info("Skipping '%s' %s tab: An error occurred during tab generation",
                          tbldr.name, self.name)
                _LOG.debug(err)
                continue

        if not tabs:
            raise Error(f"All '{self.name}' tabs were skipped")

        return _BuiltTab.BuiltCTab(self.name, tabs=tabs)
