# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the API to generate a 'Stats' container tab."""

from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound, ErrorBadFormat
from statscollectlibs.htmlreport.tabs import _Tabs
from statscollectlibs.htmlreport.tabs.stats import (_TurbostatTabBuilder, _InterruptsTabBuilder,
                                                    _ACPowerTabBuilder, _IPMITabBuilder)
from statscollectlibs.htmlreport.tabs.sysinfo import _SysInfoTabBuilder

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class StatsTabBuilder:
    """This class provides the API to generate a 'Stats' container tab."""

    name = "Stats"

    def get_default_tab_cfgs(self, stname=None):
        """
        Get the default tab configuration for statistic 'stname'. If 'stname' is not provided,
        returns all default tab configurations as a dictionary in the format
        '{stname: 'TabConfig.CTabConfig'}' with an entry for each 'stname'.
        """

        if stname is None:
            return {stname: tbldr.get_default_tab_cfg() for stname, tbldr in self._tbldrs.items()}

        try:
            return self._tbldrs[stname].get_default_tab_cfg()
        except KeyError:
            raise Error(f"unsupported statistic name '{stname}'") from None

    def get_tab(self, tab_cfgs=None):
        """
        Generate and return the Stats container tab (as an instance of '_Tabs.CTab'). The statistics
        tab includes metrics from the statistics collectors, such as 'turbostat'. Arguments are the
        same as in 'HTMLReport.generate_report()'.
        """

        if tab_cfgs is None:
            tab_cfgs = {}

        tabs = []
        for stname, tbldr in self._tbldrs.items():
            _LOG.info("Generating '%s' tab.", tbldr.name)
            try:
                tab_cfg = tab_cfgs.get(stname)
                tabs.append(tbldr.get_tab(tab_cfg=tab_cfg))
            except Error as err:
                _LOG.debug_print_stacktrace()
                _LOG.warning("failed to generate '%s' tab: %s", tbldr.name, err)
                continue

        if not tabs:
            _LOG.warning("all statistics tabs were skipped")

        return _Tabs.CTabDC(self.name, tabs)

    def _init_tab_bldrs(self):
        """Initialise tab builder classes."""

        tab_bldr_classes = (_TurbostatTabBuilder.TurbostatTabBuilder,
                            _InterruptsTabBuilder.InterruptsTabBuilder,
                            _ACPowerTabBuilder.ACPowerTabBuilder)
        tab_builders = {tab_bldr.stname: tab_bldr for tab_bldr in tab_bldr_classes}

        collected_stnames = set.union(*[set(res.info["stinfo"]) for res in self._rsts])

        # 'IPMITabBuilder' is used for both inband and out-of-band statistics. But only one instance
        # is necessary.
        collected_ipmi_stnames = set(_IPMITabBuilder.IPMITabBuilder.stnames) & collected_stnames
        if collected_ipmi_stnames:
            tab_builders[collected_ipmi_stnames.pop()] = _IPMITabBuilder.IPMITabBuilder

        supported_stnames = set(stname for stname in collected_stnames if stname in tab_builders)

        # The 'SysInfo' tab is generated by the 'SysInfoTabBuilder' class, so should not be
        # generated in this method.
        sysinfo_stname = _SysInfoTabBuilder.SysInfoTabBuilder.stname
        missing_tab_builders = collected_stnames - supported_stnames - {sysinfo_stname}
        if missing_tab_builders:
            _LOG.warning("the following statistics are not supported for HTML reports: %s",
                         ", ".join(missing_tab_builders))

        if not supported_stnames:
            raise Error("no results contain any statistics data")

        _LOG.info("Generating tabs for the following statistics: %s", ", ".join(supported_stnames))

        stats_dir = self._outdir / self.name

        for stname in tab_builders:
            if stname not in supported_stnames:
                continue

            tab_builder = tab_builders[stname]
            try:
                self._tbldrs[stname] = tab_builder(self._rsts, stats_dir, basedir=self._basedir)
            except ErrorNotFound as err:
                _LOG.info("Skipping '%s' tab as '%s' statistics not found for all reports.",
                          tab_builder.name, tab_builder.name)
                _LOG.debug(err)
                continue
            except ErrorBadFormat as err:
                _LOG.warning("Skipping '%s' tab as '%s' statistics has bad format:\n%s",
                             tab_builder.name, tab_builder.name, err.indent(2))
                continue

    def __init__(self, rsts, outdir, basedir=None):
        """Class constructor. Arguments are the same as in '_TabBuilderBase.TabBuilderBase()'."""

        self._rsts = rsts
        self._outdir = outdir
        self._basedir = basedir if basedir else outdir
        self._tbldrs = {}

        self._init_tab_bldrs()
