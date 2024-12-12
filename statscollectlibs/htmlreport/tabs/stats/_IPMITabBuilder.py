# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
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
from statscollectlibs.dfbuilders import _IPMIDFBuilder
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

        See '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.
        """

        def build_ctab_cfg(colnames, ctab_name):
            """Construct an IPMI container tab called 'ctab_name' for each column in 'colnames'."""

            dtabs = []
            for colname in colnames:
                metric, col = self._dfbldr.decode_ipmi_colname(colname)
                if not col or metric not in self._defs.info:
                    continue
                dtabs.append(self._build_def_dtab_cfg(colname, self._time_metric, smry_funcs,
                                                      self._hover_defs, title=col))

            return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

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
        ctabs.append(build_ctab_cfg(fspeed_cols, "FanSpeed"))

        # Add temperature-related D-tabs to a separate C-tab.
        temp_cols = [col for col in self._metrics["Temperature"] if col in self._common_cols]
        ctabs.append(build_ctab_cfg(temp_cols, "Temperature"))

        # Add power-related D-tabs to a separate C-tab.
        pwr_cols = self._metrics["Power"] + self._metrics["Current"] + self._metrics["Voltage"]
        ctabs.append(build_ctab_cfg(pwr_cols, "Power"))

        return TabConfig.CTabConfig(self.name, ctabs=ctabs)

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

        defs = IPMIDefs.IPMIDefs()

        # Metrics in IPMI statistics can be represented by multiple columns. For example the
        # "FanSpeed" of several different fans can be measured and represented in columns "Fan1",
        # "Fan2" etc. This dictionary maps the metrics to the appropriate columns. Initialise it
        # with empty column sets for each metric.
        self._metrics = {metric: [] for metric in defs.info}

        self._common_cols = set()

        stnames = set()
        dfs = {}
        self._dfbldr = _IPMIDFBuilder.IPMIDFBuilder()
        self._hover_defs = {}
        for res in rsts:
            for stname in self.stnames:
                if stname not in res.info["stinfo"]:
                    continue

                dfs[res.reportid] = res.load_stat(stname, self._dfbldr)
                self._hover_defs[res.reportid] = res.get_label_defs(stname)
                stnames.add(stname)
                break

        if len(stnames) > 1:
            _LOG.warning("generating '%s' tab with a combination of data collected both inband "
                         "and out-of-band", self.name)

        super().__init__(dfs, outdir, basedir=basedir, defs=defs)

        col_sets = [set(sdf.columns) for sdf in self._reports.values()]
        self._common_cols = set.union(*col_sets)

        # Reports may have the "Time" column in common or none at all. In both of these cases, an
        # IPMI tab won't be generated.
        if len(self._common_cols) < 2:
            raise Error("unable to generate IPMI tab, no common IPMI metrics between reports")

        # Update defs with IPMI column names for each column.
        for colname in self._common_cols:
            # Since we use column names which aren't known until runtime as tab titles, use the
            # defs for the metric but overwrite the 'name' and 'fsname' attributes.

            metric, ipmi_name = self._dfbldr.decode_ipmi_colname(colname)
            if not ipmi_name:
                continue

            self._metrics[metric].append(colname)

            col_def = self._defs.info[metric].copy()
            # Don't overwrite the 'title' attribute so that the metric name is shown in plots
            # and the summary table.
            col_def["fsname"] = DefsBase.get_fsname(colname)
            col_def["name"] = colname
            col_def["title"] = ipmi_name
            self._defs.info[colname] = col_def
