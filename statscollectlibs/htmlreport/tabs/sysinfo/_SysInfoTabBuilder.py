# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>


"""
Provide an API for generating a "SysInfo" container tab, which includes various system information,
such as "dmesg" contents, and more.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.rawresultlibs import RORawResult
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs.sysinfo import (_CPUFreqDTabBuilder, _CPUIdleDTabBuilder,
    _DMIDecodeDTabBuilder, _DmesgDTabBuilder, _EPPDTabBuilder, _LspciDTabBuilder, _MiscDTabBuilder,
    _PepcDTabBuilder, _ThermalThrottleDTabBuilder, _TurbostatDTabBuilder)

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class SysInfoTabBuilder:
    """
    Provide an API for generating a "SysInfo" container tab, which includes various system
    information, such as "dmesg" contents, and more.
    """

    name = "SysInfo"
    stname = "sysinfo"

    def get_tab(self, rsts: list[RORawResult.RORawResult]) -> _Tabs.CTabDC:
        """
        Generate and return the "SysInfo" container tab for the given raw results.

        Args:
            rsts: A list of 'RORawResult' objects to generate the "SysInfo" tab for.

        Returns:
            The "SysInfo" container tab for the given raw results.
        """

        stats_paths = {res.reportid: res.stats_path for res in rsts}

        # Sanity check - ensure there are statistics in the raw results.
        if not any(path for path in stats_paths.values()):
            raise Error("No statistics in the raw results")

        _LOG.info("Generating %s tabs.", self.name)

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

        return _Tabs.CTabDC(self.name, tabs=tabs)

    def __init__(self, outdir: Path, basedir: Path | None = None):
        """
        The class constructor.

        Args:
            outdir: The output directory path where the "SysInfo" tab files should be placed.
            basedir: The report base directory path, defaults to 'outdir'.
        """

        self._outdir = outdir
        self._basedir = basedir if basedir else outdir
