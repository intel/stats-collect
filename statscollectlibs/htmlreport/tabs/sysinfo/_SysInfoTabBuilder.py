# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the API to generate a 'SysInfo' container tab."""

import logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs.sysinfo import (_CPUFreqTabBuilder, _CPUIdleTabBuilder,
    _DMIDecodeTabBuilder, _DmesgTabBuilder, _EPPTabBuilder, _LspciTabBuilder, _MiscTabBuilder,
    _PepcTabBuilder, _ThermalThrottleTabBuilder)
from statscollectlibs.htmlreport.tabs.sysinfo import _TurbostatTabBuilder as _SysInfoTstatTabBuilder

_LOG = logging.getLogger()

class SysInfoTabBuilder:
    """This class provides the API to generate a 'SysInfo' container tab."""

    name = "SysInfo"
    stname = "sysinfo"

    def get_tab(self, rsts):
        """
        Generate and return the SysInfo container tab (as an instance of '_Tabs.CTab'). The
        container tab includes tabs representing various system information about the SUTs.

        The 'stats_paths' argument is a dictionary mapping in the following format:
           {'report_id': 'stats_directory_path'}
        where 'stats_directory_path' is the directory containing raw statistics files.
        """

        stats_paths = {res.reportid: res.stats_path for res in rsts}

        _LOG.info("Generating %s tabs.", self.name)

        tab_builders = [
            _PepcTabBuilder.PepcTabBuilder,
            _SysInfoTstatTabBuilder.TurbostatTabBuilder,
            _ThermalThrottleTabBuilder.ThermalThrottleTabBuilder,
            _DMIDecodeTabBuilder.DMIDecodeTabBuilder,
            _EPPTabBuilder.EPPTabBuilder,
            _CPUFreqTabBuilder.CPUFreqTabBuilder,
            _CPUIdleTabBuilder.CPUIdleTabBuilder,
            _DmesgTabBuilder.DmesgTabBuilder,
            _LspciTabBuilder.LspciTabBuilder,
            _MiscTabBuilder.MiscTabBuilder
        ]

        tabs = []

        sysinfo_dir = self._outdir / self.name
        for tab_builder in tab_builders:
            tbldr = tab_builder(sysinfo_dir, stats_paths, basedir=self._basedir)

            _LOG.info("Generating '%s' %s tab.", tbldr.name, self.name)
            try:
                tabs.append(tbldr.get_tab())
            except Error as err:
                _LOG.info("Skipping '%s' %s tab: error occurred during tab generation.",
                          tbldr.name, self.name)
                _LOG.debug(err)
                continue

        if not tabs:
            raise Error(f"all '{self.name}' tabs were skipped")

        return _Tabs.CTabDC(self.name, tabs=tabs)

    def __init__(self, outdir, basedir=None):
        """Class constructor. Arguments are the same as in '_TabBuilderBase.TabBuilderBase()'."""

        self._outdir = outdir
        self._basedir = basedir if basedir else outdir
