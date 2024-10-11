# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the turbostat statistics tab.
"""

from statscollectlibs.defs import TurbostatDefs
from statscollectlibs.dfbuilders import TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

class TurbostatTabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the turbostat statistics tab.

    Public methods overview:
    1. Optionally, retrieve the default 'TabConfig.CTabConfig' instance. See 'TabConfig' for more
       information on tab configurations.
       * 'get_default_tab_cfg()'
    2. Generate a '_Tabs.CTabDC' instance containing turbostat level 2 tabs. Optionally provide a
       tab configuration as a 'CTabConfig' to customise the tab. This can be based on the default
       configuration retrieved using 'get_default_tab_cfg()'.
       * 'get_tab()'
    """

    name = "Turbostat"
    stname = "turbostat"

    def _get_default_tab_cfg(self, metrics, smry_funcs, sname):
        """
        Helper function for 'get_default_tab_cfg()'. Get the default tab configuration which is
        populated with 'metrics', 'smry_funcs' and using the C-states in 'self._hw_cstates' and
        'self._req_cstates'.
        """

        def build_ctab_cfg(ctab_name, tab_metrics):
            """Helper function to build a C-tab config named 'ctab_name' for 'tab_metrics'."""

            tab_metrics = [col for col, raw in self._col2rawnames.items() if raw in tab_metrics]
            dtabs = []
            for metric in tab_metrics:
                if metric not in self._defs.info or metric not in metrics:
                    continue
                dtab = self._build_def_dtab_cfg(metric, self._time_metric, smry_funcs,
                                                self._hover_defs, title=self._col2rawnames[metric])
                dtabs.append(dtab)
            return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

        # Add frequency-related D-tabs to a separate C-tab.
        freq_metrics = ["Bzy_MHz", "Avg_MHz"]
        if sname == TurbostatDFBuilder.TOTALS_SNAME:
            # Add uncore frequency tabs to the "Frequency" C-tab. Some versions of 'tubostat'
            # display uncore frequencies in descending order of domain ID, e.g. "UMHz3.0 UMHz2.0
            # UMHz1.0". So sort them into ascending order so that they are more intuitive.
            freq_metrics += sorted(udef.metric for udef in self._uncfreq_defs)
        freq_tab = build_ctab_cfg("Frequency", freq_metrics)

        # Add requested C-state residency tabs to a separate C-tab.
        req_res_tab = build_ctab_cfg("Residency", self._cstates["requested"]["residency"])
        req_cnt_tab = build_ctab_cfg("Count", self._cstates["requested"]["count"])
        req_tabs = TabConfig.CTabConfig("Requested", ctabs=[req_res_tab, req_cnt_tab])

        # Add hardware C-state residency tabs to a separate C-tab.
        hw_cstates = ["Busy%"] + self._cstates["hardware"]["core"]
        if sname == TurbostatDFBuilder.TOTALS_SNAME:
            hw_cstates += self._cstates["hardware"]["module"] + self._cstates["hardware"]["package"]
        hw_cs_tab = build_ctab_cfg("Hardware", hw_cstates)

        # Combine requeseted and hardware C-states into a single C-tab.
        cs_tab = TabConfig.CTabConfig("C-states", ctabs=[hw_cs_tab, req_tabs])

        # Add temperature/power-related D-tabs to a separate C-tab.
        tp_metrics = ["CorWatt", "CoreTmp"]
        if sname == TurbostatDFBuilder.TOTALS_SNAME:
            tp_metrics += ["PkgWatt", "PkgWatt%TDP", "GFXWatt", "RAMWatt", "PkgTmp"]
        tmp_tab = build_ctab_cfg("Temperature / Power", tp_metrics)

        # Add miscellaneous D-tabs to a separate C-tab.
        misc_tab = build_ctab_cfg("Misc", ["IRQ", "SMI", "IPC"])

        return TabConfig.CTabConfig(sname, ctabs=[freq_tab, cs_tab, tmp_tab, misc_tab])

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

        # Define which summary functions should be included in the summary table for each metric.
        smry_funcs = {}
        for metric in metrics:
            if metric in ("IRQ", "SMI"):
                smry_funcs[metric] = ["max", "avg", "min", "std"]
            else:
                smry_funcs[metric] = ["max", "99.999%", "99.99%", "99.9%", "99%",
                                      "med", "avg", "min", "std"]

        categorised_metrics = {}
        for metric in metrics:
            sname = TurbostatDFBuilder.get_col_scope(metric)
            if not sname:
                continue
            if sname not in categorised_metrics:
                categorised_metrics[sname] = {metric}
            else:
                categorised_metrics[sname].add(metric)

        l2_tabs = []
        for sname, scope_metrics in categorised_metrics.items():
            l2_tabs.append(self._get_default_tab_cfg(scope_metrics, smry_funcs, sname))

        return TabConfig.CTabConfig(self.name, ctabs=l2_tabs)

    def _parse_colnames(self, dfs):
        """
        Iterate through columns in 'dfs' to find common C-states and uncore frequency columns
        present in all results and categorise them into the 'self._cstates' dictionary and
        'self._uncfreq_defs' list respectively. Returns a list of all of the C-states with data in
        one or more of 'dfs'.
        """

        self._cstates = {
            "requested": {
                "residency": [],
                "count": []
            },
            "hardware": {
                "core": [],
                "module": [],
                "package": []
            }
        }

        # Maintain the order that C-states appear in turbostat so that they are not jumbled.
        all_colnames = []
        for df in dfs.values():
            for column in df.columns:
                if column not in all_colnames:
                    all_colnames.append(column)

        all_cstates = []
        for colname in all_colnames:

            try:
                rawname = self._col2rawnames[colname]
            except KeyError:
                continue

            if TurbostatDefs.ReqCSDef.check_metric(rawname):
                self._cstates["requested"]["residency"].append(rawname)
                all_cstates.append(TurbostatDefs.ReqCSDef(rawname).cstate)
            elif TurbostatDefs.ReqCSDefCount.check_metric(rawname):
                self._cstates["requested"]["count"].append(rawname)
                all_cstates.append(TurbostatDefs.ReqCSDefCount(rawname).cstate)
            elif TurbostatDefs.CoreCSDef.check_metric(rawname):
                self._cstates["hardware"]["core"].append(rawname)
                all_cstates.append(TurbostatDefs.CoreCSDef(rawname).cstate)
            elif TurbostatDefs.ModuleCSDef.check_metric(rawname):
                self._cstates["hardware"]["module"].append(rawname)
                all_cstates.append(TurbostatDefs.ModuleCSDef(rawname).cstate)
            elif TurbostatDefs.PackageCSDef.check_metric(rawname):
                self._cstates["hardware"]["package"].append(rawname)
                all_cstates.append(TurbostatDefs.PackageCSDef(rawname).cstate)
            elif TurbostatDefs.UncoreFreqDef.check_metric(rawname):
                self._uncfreq_defs.append(TurbostatDefs.UncoreFreqDef(rawname))

        return all_cstates

    def _load_dfs(self, rsts):
        """Load 'pandas.DataFrames' from raw turbostat statistics files in 'rsts'."""

        dfs = {}
        tstat_rsts = [res for res in rsts if "turbostat" in res.info["stinfo"]]

        for res in tstat_rsts:
            cpunum = res.info.get("cpunum")
            dfbldr = TurbostatDFBuilder.TurbostatDFBuilder(cpunum=cpunum)

            dfs[res.reportid] = res.load_stat("turbostat", dfbldr, "turbostat.raw.txt")
            self._col2rawnames.update(dfbldr.col2rawnames)
            self._hover_defs[res.reportid] = res.get_label_defs("turbostat")

        return dfs

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Adding a turbostat statistics container tab will create a "Turbostat"
        sub-directory and store level 2 tabs inside it. Level 2 tabs will represent metrics stored
        in the raw turbostat statistics file using data tabs.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following:
         * rsts - a list of 'RORawResult' instances for different results with statistics which
                  should be included in the turbostat tabs.
        """

        outdir = outdir / self.name
        self._time_metric = "Time"
        self._hover_defs = {}

        # Store C-states for which there is data in each raw turbostat statistics file. Initialised
        # in 'self._parse_colnames()'.
        self._cstates = None

        # Store metrics representing uncore frequency to update 'self._defs' accordingly.
        self._uncfreq_defs = []

        # Store a mapping between 'pandas.DataFrame' column names and the raw names used in the raw
        # turbostat statistics files.
        self._col2rawnames = {}

        dfs = self._load_dfs(rsts)
        all_cstates = self._parse_colnames(dfs)
        defs = TurbostatDefs.TurbostatDefs(all_cstates, self._uncfreq_defs)
        super().__init__(dfs, outdir, basedir=basedir, defs=defs)

        for colname, rawname in self._col2rawnames.items():
            if rawname not in self._defs.info:
                continue

            self._defs.info[colname] = self._defs.info[rawname].copy()
            self._defs.info[colname]["name"] = colname
