# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the IPMI statistics Tab.
"""

import logging
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.defs import DefsBase, IPMIDefs
from statscollectlibs.dfbuilders import IPMIDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

_LOG = logging.getLogger()

class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the IPMI statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.CTabDC' instance containing tabs which display IPMI statistics.
       * 'get_tab()'
    """

    name = "IPMI"
    stnames = ("ipmi-inband", "ipmi-oob",)

    def get_default_tab_cfg(self):
        """
        Generate the default tab configuration as a 'TabConfig.CTabConfig' instance.
        The default tab configuration will specify container tabs for each of the following
        categories:

            1. "Fan Speed"
            2. "Temperature"
            3. "Power"

        Each of these container tab configurations contain data tab configurations for each IPMI
        metric which is common to all results. For example, the "Fan Speed" container tab might
        contain several data tabs titled "Fan1", "Fan2" etc. if each raw IPMI statistics file
        contains these measurements. If there were no common IPMI metrics between all of the results
        for a given category, the container tab will not be generated.
        """

        # Define which summary functions should be included in the generated summary table
        # for a given metric.
        smry_funcs = {}
        for metric in self._common_cols:
            smry_funcs[metric] = ["max", "99.999%", "99.99%", "99.9%", "99%",
                                  "med", "avg", "min", "std"]

        # Dedupe cols in 'self._metrics'.
        for metric in self._metrics:
            self._metrics[metric] = Trivial.list_dedup(self._metrics[metric])

        ctabs = []
        # Add fan speed-related D-tabs to a separate C-tab.
        fspeed_cols = [col for col in self._metrics["FanSpeed"] if col in self._common_cols]
        ctabs.append(self._build_def_ctab_cfg("Fan Speed", fspeed_cols, self._time_metric,
                                              smry_funcs, self._hover_defs))

        # Add temperature-related D-tabs to a separate C-tab.
        temp_cols = [col for col in self._metrics["Temperature"] if col in self._common_cols]
        ctabs.append(self._build_def_ctab_cfg("Temperature", temp_cols, self._time_metric,
                                              smry_funcs, self._hover_defs))

        # Add power-related D-tabs to a separate C-tab.
        pwr_cols = self._metrics["Power"] + self._metrics["Current"] + self._metrics["Voltage"]
        ctabs.append(self._build_def_ctab_cfg("Power", pwr_cols, self._time_metric,
                                              smry_funcs, self._hover_defs))

        return TabConfig.CTabConfig(self.name, ctabs=ctabs)

    def get_tab(self, tab_cfg=None):
        """
        Preceeds 'super().get_tab()' by populating the available metrics with all of the 'ipmi'
        column names parsed from raw statistics files. See 'super().get_tab()' for more information.
        """

        col_sets = [set(sdf.columns) for sdf in self._reports.values()]
        self._common_cols = set.union(*col_sets)

        # Reports may have the "Time" column in common or none at all. In both of these cases, an
        # IPMI tab won't be generated.
        if len(self._common_cols) < 2:
            raise Error("unable to generate IPMI tab, no common IPMI metrics between reports.")

        # Update defs with IPMI column names for each column.
        for metric, colnames in self._metrics.items():
            for colname in colnames:
                if colname not in self._common_cols:
                    continue

                # Since we use column names which aren't known until runtime as tab titles, use the
                # defs for the metric but overwrite the 'name' and 'fsname' attributes. Use 'copy'
                # so that 'defs.info' can be used to create the container tab.
                col_def = self._defs.info[metric].copy()
                # Don't overwrite the 'title' attribute so that the metric name is shown in plots
                # and the summary table.
                col_def["fsname"] = DefsBase.get_fsname(colname)
                col_def["name"] = colname
                self._defs.info[colname] = col_def

        return super().get_tab(tab_cfg)

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Adding an IPMI statistics container tab will create an 'IPMI'
        sub-directory and store tabs inside it. These tabs will represent all of the metrics stored
        in the raw IPMI statistics file.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following: 
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
        """

        self._time_metric = "Time"

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns. Initialise it
        # with empty column sets for each metric.
        defs = IPMIDefs.IPMIDefs()
        self._metrics = {}

        self._common_cols = set()

        stnames = set()
        dfs = {}
        dfbldr = IPMIDFBuilder.IPMIDFBuilder()
        self._hover_defs = {}
        for res in rsts:
            for stname in self.stnames:
                if stname not in res.info["stinfo"]:
                    continue

                dfs[res.reportid] = res.load_stat(stname, dfbldr, f"{stname}.raw.txt")
                self._hover_defs[res.reportid] = res.get_label_defs(stname)
                self._metrics.update(dfbldr.metrics)
                stnames.add(stname)
                break

        if len(stnames) > 1:
            _LOG.warning("generating '%s' tab with a combination of data collected both inband "
                         "and out-of-band.", self.name)

        super().__init__(dfs, outdir, basedir=basedir, defs=defs)
