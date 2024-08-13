# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module contains the base class for turbostat level 2 tab builder classes.

'Level 2 turbostat tabs' refer to tabs in the second level of tabs in the turbostat tab hierarchy.
For each level 2 turbostat tab, we parse raw turbostat statistics files differently.  Therefore this
base class expects child classes to implement '_turbostat_to_df()'.
"""

from statscollectlibs.defs import TurbostatDefs
from statscollectlibs.dfbuilders import TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

class TurbostatL2TabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for turbostat level 2 tab builder classes.

    This base class requires child classes to implement the following methods:
    1. Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'.
       * '_turbostat_to_df()'
    """

    def _get_default_tab_cfg(self, metrics, smry_funcs):
        """
        Helper function for 'get_default_tab_cfg()'. Get the default tab configuration which is
        populated with 'metrics', 'smry_funcs' and using the C-states in 'self._hw_cstates' and
        'self._req_cstates'.
        """

        def fltr(unfiltered_metrics):
            """Helper function filters 'unfiltered_metrics' based on if they are in 'metrics'."""
            return [m for m in unfiltered_metrics if m in metrics]

        # Add frequency-related D-tabs to a separate C-tab.
        freq_tab = self._build_def_ctab_cfg("Frequency", fltr(self._freq_metrics),
                                            self._time_metric, smry_funcs, self._hover_defs)

        # Add temperature/power-related D-tabs to a separate C-tab.
        tmp_tab = self._build_def_ctab_cfg("Temperature / Power", fltr(self._tp_metrics),
                                           self._time_metric, smry_funcs, self._hover_defs)

        # Add miscellaneous D-tabs to a separate C-tab.
        misc_tab = self._build_def_ctab_cfg("Misc", fltr(self._misc_metrics), self._time_metric,
                                            smry_funcs, self._hover_defs)

        req_res_tab = self._build_def_ctab_cfg("Residency", self._cstates["requested"]["residency"],
                                               self._time_metric, smry_funcs, self._hover_defs)

        req_cnt_tab = self._build_def_ctab_cfg("Count", self._cstates["requested"]["count"],
                                               self._time_metric, smry_funcs, self._hover_defs)

        req_tabs = TabConfig.CTabConfig("Requested", ctabs=[req_res_tab, req_cnt_tab])

        hw_cstates = ["Busy%"] + self._cstates["hardware"]["core"]
        if self._totals:
            hw_cstates += self._cstates["hardware"]["module"]
            hw_cstates += self._cstates["hardware"]["package"]
        self._hw_cs_tab = self._build_def_ctab_cfg("Hardware", hw_cstates, self._time_metric,
                                                   smry_funcs, self._hover_defs)

        cs_tab = TabConfig.CTabConfig("C-states", ctabs=[self._hw_cs_tab, req_tabs])

        return TabConfig.CTabConfig(self.name, ctabs=[freq_tab, tmp_tab, misc_tab, cs_tab])

    def get_default_tab_cfg(self):
        """
        Returns a 'TabConfig.CTabConfig' instance, titled 'self.name', containing tab configurations
        which represent different metrics within raw turbostat statistic files.

        Note that the hierarchy of the tabs will will only include turbostat metrics which are
        common to all results.

        See '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.
        """

        # Find metrics which appear in the raw turbostat statistic files.
        metric_sets = [set(sdf.columns) for sdf in self._reports.values()]
        metrics = set.union(*metric_sets)

        # Limit metrics to only those with definitions.
        metrics.intersection_update(set(self._defs.info.keys()))

        # Define which plots should be generated in the data tab and which summary functions
        # should be included in the generated summary table for a given metric.
        plots = {}
        smry_funcs = {}
        for metric in metrics:
            defs_info = self._defs.info
            plots[metric] = {
                "scatter": [(defs_info[self._time_metric], defs_info[metric])],
                "hist": [defs_info[metric]]
            }
            if metric in ('IRQ', 'SMI'):
                smry_funcs[metric] = ["max", "avg", "min", "std"]
            else:
                smry_funcs[metric] = ["max", "99.999%", "99.99%", "99.9%", "99%",
                                      "med", "avg", "min", "std"]

        # All raw turbostat statistic files have been parsed so we can now get a tab config with
        # tabs which are common to all sets of results.
        return self._get_default_tab_cfg(metrics, smry_funcs)

    def _parse_colnames(self, dfs):
        """
        Iterate through columns in 'dfs' to find common C-states and uncore frequency columns
        present in all results and categorise them into the 'self._cstates' dictionary and
        'self._uncfreq_defs' list respectively. Returns a list of all of the C-states with data in
        one or more of 'dfs'.
        """

        req_rsdncy_cstates = []
        req_cnt_cstates = []
        core_cstates = []
        pkg_cstates = []
        mod_cstates = []
        all_cstates = []

        # Maintain the order that C-states appear in turbostat so that they are not jumbled.
        all_colnames = []
        for df in dfs.values():
            for column in df.columns:
                if column not in all_colnames:
                    all_colnames.append(column)

        for colname in all_colnames:
            if TurbostatDefs.ReqCSDef.check_metric(colname):
                req_rsdncy_cstates.append(colname)
                all_cstates.append(TurbostatDefs.ReqCSDef(colname).cstate)
            elif TurbostatDefs.ReqCSDefCount.check_metric(colname):
                req_cnt_cstates.append(colname)
                all_cstates.append(TurbostatDefs.ReqCSDefCount(colname).cstate)
            elif TurbostatDefs.CoreCSDef.check_metric(colname):
                core_cstates.append(colname)
                all_cstates.append(TurbostatDefs.CoreCSDef(colname).cstate)
            elif self._totals and TurbostatDefs.ModuleCSDef.check_metric(colname):
                mod_cstates.append(colname)
                all_cstates.append(TurbostatDefs.ModuleCSDef(colname).cstate)
            elif self._totals and TurbostatDefs.PackageCSDef.check_metric(colname):
                pkg_cstates.append(colname)
                all_cstates.append(TurbostatDefs.PackageCSDef(colname).cstate)
            elif TurbostatDefs.UncoreFreqDef.check_metric(colname):
                self._uncfreq_defs.append(TurbostatDefs.UncoreFreqDef(colname))

        self._cstates["hardware"]["core"] = core_cstates
        self._cstates["hardware"]["package"] = pkg_cstates
        self._cstates["hardware"]["module"] = mod_cstates
        self._cstates["requested"]["residency"] = req_rsdncy_cstates
        self._cstates["requested"]["count"] = req_cnt_cstates

        return all_cstates

    def __init__(self, rsts, outdir, basedir, totals=None, hover_defs=None):
        """
        The class constructor. Adding a turbostat level 2 tab will create a sub-directory and store
        data tabs inside it for metrics stored in the raw turbostat statistics file. The arguments
        are the same as in '_TabBuilderBase.TabBuilderBase' except for:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
         * totals - a boolean indicating whether the tab should include "totals" data summarising
                    'turbostat' statistics. By default, False and this class will attempt to show
                    data for the measured CPU of each result.
         * hover_defs - a mapping from 'reportid' to definition dictionaries of metrics which
                        should be included in the hovertext of scatter plots.
        """

        self._time_metric = "Time"
        self.outdir = outdir
        self._hover_defs = hover_defs if hover_defs else {}
        self._totals = totals

        self.name = "Totals" if totals else "Measured CPU"

        # After C-states have been extracted from the first raw turbostat statistics file, this
        # property will be assigned a 'TurbostatDefs.TurbostatDefs' instance.
        self._defs = None

        # Expose the "C-states -> Hardware" tab so that child classes can add to it.
        self._hw_cs_tab = None

        # Categorise 'turbostat' metrics into different tabs. Child classes can
        # modify these attributes to change which metrics will appear in the
        # tabs.
        # Frequency tab.
        self._freq_metrics = ["Bzy_MHz", "Avg_MHz"]
        # Temperature/Power tab.
        self._tp_metrics = ["CorWatt", "CoreTmp"]
        if self._totals:
            # Add non-CPU specific power metrics to the "Temperature/Power" tab.
            self._tp_metrics += ["PkgWatt", "PkgWatt%TDP", "GFXWatt", "RAMWatt", "PkgTmp"]
        # Misc tab.
        self._misc_metrics = ["IRQ", "SMI", "IPC"]

        # Store C-states for which there is data in each raw turbostat statistics file.
        self._cstates = {
            "requested": {
                "residency": [],
                "count": []
            },
            "hardware": {
                "core": [],
                "package": [],
                "module": []
            }
        }

        # Store metrics representing uncore frequency to update 'self._defs' accordingly.
        self._uncfreq_defs = []

        # Load 'pandas.DataFrames' from raw turbostat statistics files.
        dfs = {}
        for res in rsts:
            if "turbostat" not in res.info["stinfo"]:
                continue

            if self._totals:
                dfbldr = TurbostatDFBuilder.TotalsDFBuilder()
            else:
                cpunum = res.info.get("cpunum", None)
                dfbldr = TurbostatDFBuilder.MCPUDFBuilder(str(cpunum))

            dfs[res.reportid] = res.load_stat("turbostat", dfbldr, "turbostat.raw.txt")
            self._hover_defs[res.reportid] = res.get_label_defs("turbostat")

        super().__init__(dfs, outdir, basedir=basedir)

        all_cstates = self._parse_colnames(dfs)
        self._defs = TurbostatDefs.TurbostatDefs(all_cstates, self._uncfreq_defs)

        if self._totals:
            self._defs.mangle_descriptions()
            # Add uncore frequency tabs to the "Frequency" C-tab. Some versions of 'tubostat'
            # display uncore frequencies in descending order of domain ID, e.g. "UMHz3.0 UMHz2.0
            # UMHz1.0". So sort them into ascending order so that they are more intuitive.
            self._freq_metrics += sorted(udef.metric for udef in self._uncfreq_defs)
