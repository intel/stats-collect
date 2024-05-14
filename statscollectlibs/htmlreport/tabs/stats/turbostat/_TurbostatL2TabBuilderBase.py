# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
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
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

class TurbostatL2TabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for turbostat level 2 tab builder classes.

    This base class requires child classes to implement the following methods:
    1. Convert the 'tstat' dictionary produced by 'TurbostatParser' to a 'pandas.DataFrame'.
       * '_turbostat_to_df()'
    """

    def _get_ctab_cfg(self, metrics, smry_funcs):
        """
        Get the tab config which is populated with 'metrics' and using the C-states in
        'self._hw_cstates' and 'self._req_cstates'.
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

        req_res_cstates = [cs.metric for cs in self._cstates["requested"]["residency"]]
        req_res_tab = self._build_def_ctab_cfg("Residency", req_res_cstates, self._time_metric,
                                               smry_funcs, self._hover_defs)

        req_cnt_cstates = [cs.metric for cs in self._cstates["requested"]["count"]]
        req_cnt_tab = self._build_def_ctab_cfg("Count", req_cnt_cstates, self._time_metric,
                                               smry_funcs, self._hover_defs)

        req_tabs = TabConfig.CTabConfig("Requested", ctabs=[req_res_tab, req_cnt_tab])

        hw_cstates =  ["Busy%"] + [cs.metric for cs in self._cstates["hardware"]["core"]]
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
        return self._get_ctab_cfg(metrics, smry_funcs)

    def _init_cstates(self, dfs):
        """
        Find common C-states present in all results in 'dfs' and categorise them into the
        'self._cstates' dictionary. Returns a list of all of the common C-states.
        """

        req_rsdncy_cstates = []
        req_cnt_cstates = []
        core_cstates = []
        pkg_cstates = []
        mod_cstates = []

        # Maintain the order that C-states appear in turbostat so that they are not jumbled.
        all_colnames = []
        for df in dfs.values():
            for column in df.columns:
                if column not in all_colnames:
                    all_colnames.append(column)

        for colname in all_colnames:
            if TurbostatDefs.ReqCSDef.check_metric(colname):
                req_rsdncy_cstates.append(TurbostatDefs.ReqCSDef(colname))
            elif TurbostatDefs.ReqCSDefCount.check_metric(colname):
                req_cnt_cstates.append(TurbostatDefs.ReqCSDefCount(colname))
            elif TurbostatDefs.CoreCSDef.check_metric(colname):
                core_cstates.append(TurbostatDefs.CoreCSDef(colname))
            elif TurbostatDefs.ModuleCSDef.check_metric(colname):
                mod_cstates.append(TurbostatDefs.ModuleCSDef(colname))
            elif TurbostatDefs.PackageCSDef.check_metric(colname):
                pkg_cstates.append(TurbostatDefs.PackageCSDef(colname))

        self._cstates["hardware"]["core"] = core_cstates
        self._cstates["hardware"]["package"] = pkg_cstates
        self._cstates["hardware"]["module"] = mod_cstates
        self._cstates["requested"]["residency"] = req_rsdncy_cstates
        self._cstates["requested"]["count"] = req_cnt_cstates

        all_cstates = req_rsdncy_cstates + req_cnt_cstates + core_cstates
        all_cstates += pkg_cstates + mod_cstates
        return [csdef.cstate for csdef in all_cstates]

    def __init__(self, dfs, outdir, basedir, hover_defs=None):
        """
        The class constructor. Adding a turbostat level 2 tab will create a sub-directory and store
        data tabs inside it for metrics stored in the raw turbostat statistics file. The arguments
        are the same as in '_TabBuilderBase.TabBuilderBase' except for:
         * dfs - a dictionary in the format '{ReportId: pandas.DataFrame}' for each result where the
                 'pandas.DataFrame' contains that statistics data for that result.
         * hover_defs - a mapping from 'reportid' to definition dictionaries of metrics which
                        should be included in the hovertext of scatter plots.
        """

        self._time_metric = "Time"
        self.outdir = outdir
        self._hover_defs = hover_defs

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

        super().__init__(dfs, outdir, basedir=basedir)

        all_cstates = self._init_cstates(dfs)
        self._defs = TurbostatDefs.TurbostatDefs(all_cstates)
