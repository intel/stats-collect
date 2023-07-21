# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the API to generate a 'Stats' container tab."""

import logging
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.htmlreport.tabs import _ACPowerTabBuilder, _IPMITabBuilder, _Tabs
from statscollectlibs.htmlreport.tabs.turbostat import _TurbostatTabBuilder

_LOG = logging.getLogger()

class StatsTabBuilder:
    """This class provides the API to generate a 'Stats' container tab."""

    def get_tab(self, rsts):
        """
        Generate and return the Stats container tab (as an instance of '_Tabs.CTab'). The statistics
        tab includes metrics from the statistics collectors, such as 'turbostat'.
        """

        tab_bldr_classes = (_ACPowerTabBuilder.ACPowerTabBuilder,
                            _TurbostatTabBuilder.TurbostatTabBuilder)
        tab_builders = {tab_bldr.stname: tab_bldr for tab_bldr in tab_bldr_classes}

        # 'IPMITabBuilder' is used for inband and out-of-band IPMI collection
        # so has two statistic names.
        for stname in _IPMITabBuilder.IPMITabBuilder.stnames:
            tab_builders[stname] = _IPMITabBuilder.IPMITabBuilder

        collected_stnames = set.union(*[set(res.info["stinfo"]) for res in rsts])

        filtered_stnames = set(stname for stname in collected_stnames if stname in tab_builders)
        # The 'SysInfo' tab is generated in '_generate_sysinfo_tabs()', so should not be generated
        # in this method.
        missing_tab_builders = collected_stnames - filtered_stnames - {"sysinfo"}
        if missing_tab_builders:
            _LOG.warning("the following statistics are not supported for HTML reports: %s",
                         ", ".join(missing_tab_builders))

        if not filtered_stnames:
            raise Error("no results contain any statistics data")

        _LOG.info("Generating tabs for the following statistics: %s", ", ".join(filtered_stnames))

        # Create 'Stats' tabs directory.
        stats_dir = self._outdir / "Stats"

        tabs = []
        for stname in tab_builders:
            if stname not in filtered_stnames:
                continue

            tab_builder = tab_builders[stname]
            try:
                tbldr = tab_builder(rsts, stats_dir, basedir=self._basedir)
            except ErrorNotFound as err:
                _LOG.info("Skipping '%s' tab as '%s' statistics not found for all reports.",
                          tab_builder.name, tab_builder.name)
                _LOG.debug(err)
                continue

            _LOG.info("Generating '%s' tab.", tbldr.name)
            try:
                tabs.append(tbldr.get_tab())
            except Error as err:
                _LOG.info("Skipping '%s' statistics: error occurred during tab generation.",
                          tab_builder.name)
                _LOG.debug(err)
                continue

        if not tabs:
            raise Error("all 'Stats' tabs were skipped")

        return _Tabs.CTabDC("Stats", tabs)

    def __init__(self, outdir, basedir=None):
        """
        Class constructor. Arguments are as follows:
         * outdir - the directory to store tab files in.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._outdir = outdir
        self._basedir = basedir if basedir else outdir
