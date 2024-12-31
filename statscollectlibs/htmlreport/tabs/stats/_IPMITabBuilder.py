# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of populating the IPMI statistics tab.
"""

import logging
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.defs import MDCBase, IPMIMDC
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

_LOG = logging.getLogger()

class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the IPMI statistics tab."""

    name = "IPMI"
    stnames = ("ipmi-inband", "ipmi-oob",)

    def get_default_tab_cfg(self):
        """
        Generate the default tab configuration as a 'TabConfig.CTabConfig' instance. The default tab
        configuration will specify container tabs for each of the following categories:
          * "Fan Speed"
          * "Temperature"
          * "Power"

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
                category, metric = self._dfbldr.split_colname(colname)
                if not metric or category not in self._defs.info:
                    continue
                dtabs.append(self._build_def_dtab_cfg(colname, self._time_metric, smry_funcs,
                                                      self._hover_defs, title=metric))

            return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

        # Define which summary functions should be included in the generated summary table
        # for a given metric.
        smry_funcs = {}
        for colname in self._common_colnames:
            smry_funcs[colname] = ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                                   "std"]

        ctabs = []
        # Add fan speed-related D-tabs to a separate C-tab.
        fspeed_cols = [col for col in self._categories["FanSpeed"] if col in self._common_colnames]
        ctabs.append(build_ctab_cfg(fspeed_cols, "FanSpeed"))

        # Add temperature-related D-tabs to a separate C-tab.
        temp_cols = [col for col in self._categories["Temperature"] if col in self._common_colnames]
        ctabs.append(build_ctab_cfg(temp_cols, "Temperature"))

        # Add power-related D-tabs to a separate C-tab.
        pwr_cols = self._categories["Power"] + self._categories["Current"] + \
                                               self._categories["Voltage"]
        ctabs.append(build_ctab_cfg(pwr_cols, "Power"))

        return TabConfig.CTabConfig(self.name, ctabs=ctabs)

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. The arguments are the same as in '_TabBuilderBase.TabBuilderBase()'
        except for the following.
          * rsts - an iterable collection of 'RORawResult' instances for which data should be
                   included in the built tab.
        """

        self._time_metric = "Time"
        self._dfbldr = None
        self._hover_defs = {}

        # Different results include different IPMI metrics. This is the set of metrics common to all
        # the results.
        self._common_colnames = set()

        defs = IPMIMDC.IPMIMDC()
        self._dfbldr = _IPMIDFBuilder.IPMIDFBuilder(defs=defs)

        # The IPMI metric categories (e.g., "FanSpeed").
        self._categories = {category: [] for category in defs.info}

        dfs = {}
        found_stnames = set()
        for res in rsts:
            for stname in self.stnames:
                if stname not in res.info["stinfo"]:
                    continue

                dfs[res.reportid] = res.load_stat(stname, self._dfbldr)
                self._hover_defs[res.reportid] = res.get_label_defs(stname)
                found_stnames.add(stname)
                break

        if len(found_stnames) > 1:
            _LOG.notice("a mix of in-band and out-of-band IPMI statistics detected")

        super().__init__(dfs, outdir, basedir=basedir, defs=defs)

        col_sets = [set(sdf.columns) for sdf in self._dfs.values()]
        self._common_colnames = set.union(*col_sets)

        # One of the metrics must be the time, so min. 2 columns are required.
        if len(self._common_colnames) < 2:
            raise Error("unable to generate IPMI tab, no common IPMI metrics between reports")

        # Currently the definitions include just category names. Change them to include metric
        # names.
        # TODO: but this should be done in 'IPMIMDC' instead. May be similarly to 'TurbostatDefs'.
        for colname in self._common_colnames:
            category, metric = self._dfbldr.split_colname(colname)
            if not category:
                continue

            self._categories[category].append(colname)

            info = self._defs.info[category].copy()
            # Don't overwrite the 'title' attribute so that the metric name is shown in plots
            # and the summary table.
            info["fsname"] = MDCBase.get_fsname(colname)
            info["name"] = colname
            info["title"] = metric
            self._defs.info[colname] = info

        # De-dubplicate column names.
        for colname in self._categories:
            self._categories[colname] = Trivial.list_dedup(self._categories[colname])
