# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Build and populate the turbostat statistics tab.
"""

from statscollectlibs.defs import TurbostatDefs
from statscollectlibs.dfbuilders import _TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

class TurbostatTabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    Build and populate the turbostat statistics tab.

    Public methods overview:
    1. Optionally, retrieve the default 'TabConfig.CTabConfig' instance. See 'TabConfig' for more
       information on tab configurations.
       * 'get_default_tab_cfg()'
    2. Generate a '_Tabs.CTabDC' instance containing turbostat level 2 tabs. Optionally provide a
       tab configuration as a 'CTabConfig' to customize the tab. This can be based on the default
       configuration retrieved using 'get_default_tab_cfg()'.
       * 'get_tab()'
    """

    name = "Turbostat"
    stname = "turbostat"

    def _get_default_tab_cfg(self, metrics, smry_funcs, sname):
        """
        Get the default tab configuration which is populated with 'metrics', 'smry_funcs' and using
        the C-states in 'self._hw_cstates' and 'self._req_cstates'.
        """

        def build_ctab_cfg(ctab_name, tab_metrics):
            """Build a C-tab config named 'ctab_name' for 'tab_metrics'."""

            tab_metrics = [col for col, raw in self._col2metric.items() if raw in tab_metrics]
            dtabs = []
            for metric in tab_metrics:
                if metric not in self._defs.info or metric not in metrics:
                    continue
                dtab = self._build_def_dtab_cfg(metric, self._time_metric, smry_funcs,
                                                self._hover_defs, title=self._col2metric[metric])
                dtabs.append(dtab)
            return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

        # Add frequency-related D-tabs to a separate C-tab.
        freq_metrics = ["Bzy_MHz", "Avg_MHz"]
        if sname == _TurbostatDFBuilder.TOTALS_SNAME:
            freq_metrics += self._categories["uncore"]["frequency"]
        # Add uncore frequency tabs to the "Frequency" C-tab.
        freq_tab = build_ctab_cfg("Frequency", freq_metrics)

        # Add requested C-state residency tabs to a separate C-tab.
        req_res_tab = build_ctab_cfg("Residency", self._categories["requested"]["residency"])
        req_cnt_tab = build_ctab_cfg("Count", self._categories["requested"]["count"])
        req_tabs = TabConfig.CTabConfig("Requested", ctabs=[req_res_tab, req_cnt_tab])

        # Add hardware C-state residency tabs to a separate C-tab.
        hw_cstates = ["Busy%"] + self._categories["hardware"]["core"]
        if sname == _TurbostatDFBuilder.TOTALS_SNAME:
            hw_cstates += self._categories["hardware"]["module"]
            hw_cstates += self._categories["hardware"]["package"]
        hw_cs_tab = build_ctab_cfg("Hardware", hw_cstates)

        # Combine C-states into a single C-tab.
        idle_tab = TabConfig.CTabConfig("C-states", ctabs=[hw_cs_tab, req_tabs])

        # Add temperature/power-related D-tabs to a separate C-tab.
        tp_metrics = ["CorWatt", "CoreTmp"]
        if sname == _TurbostatDFBuilder.TOTALS_SNAME:
            tp_metrics += ["PkgWatt", "PkgWatt%TDP", "GFXWatt", "RAMWatt", "PkgTmp"]
        tmp_tab = build_ctab_cfg("Temperature / Power", tp_metrics)

        # Add miscellaneous D-tabs to a separate C-tab.
        misc_tab = build_ctab_cfg("Misc", ["IRQ", "SMI", "IPC"])

        return TabConfig.CTabConfig(sname, ctabs=[freq_tab, idle_tab, tmp_tab, misc_tab])

    def get_default_tab_cfg(self):
        """
        Build and return a 'TabConfig.CTabConfig' instance, titled 'self.name', containing tab
        configurations which represent different metrics within raw turbostat statistic files.

        The hierarchy of the tabs will will only include turbostat metrics which are common to all
        results.

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
            sname = _TurbostatDFBuilder.get_col_scope(metric)
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

    def _categorize_metrics(self, metrics):
        """
        Categorize C-states and uncore frequency metrics into the 'self._categories' dictionary.
        """

        self._categories = {
            "requested": {
                "residency": [],
                "count": []
            },
            "hardware": {
                "core": [],
                "module": [],
                "package": []
            },
            "uncore": {
                "frequency": []
            }
        }

        for metric in metrics:
            if TurbostatDefs.ReqCSDef.check_metric(metric):
                self._categories["requested"]["residency"].append(metric)
            elif TurbostatDefs.ReqCSDefCount.check_metric(metric):
                self._categories["requested"]["count"].append(metric)
            elif TurbostatDefs.CoreCSDef.check_metric(metric):
                self._categories["hardware"]["core"].append(metric)
            elif TurbostatDefs.ModuleCSDef.check_metric(metric):
                self._categories["hardware"]["module"].append(metric)
            elif TurbostatDefs.PackageCSDef.check_metric(metric):
                self._categories["hardware"]["package"].append(metric)
            elif TurbostatDefs.UncoreFreqDef.check_metric(metric):
                self._categories["uncore"]["frequency"].append(metric)

    def _load_dfs(self, rsts):
        """Load 'pandas.DataFrames' from raw turbostat statistics files in 'rsts'."""

        dfs = {}
        tstat_rsts = [res for res in rsts if "turbostat" in res.info["stinfo"]]

        for res in tstat_rsts:
            cpunum = res.info.get("cpunum")
            dfbldr = _TurbostatDFBuilder.TurbostatDFBuilder(cpunum=cpunum)

            dfs[res.reportid] = res.load_stat("turbostat", dfbldr, "turbostat.raw.txt")
            self._col2metric.update(dfbldr.col2metric)
            self._hover_defs[res.reportid] = res.get_label_defs("turbostat")

        return dfs

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Add a turbostat statistics container tab, which will create a
        "Turbostat" sub-directory and store level 2 tabs inside it. Level 2 tabs will represent
        metrics stored in the raw turbostat statistics file using data tabs.

        The arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the
        following:
          * rsts - a collection of 'RORawResult' instances for different results with statistics
                   which should be included in the turbostat tabs.
        """

        outdir = outdir / self.name
        self._time_metric = "Time"
        self._hover_defs = {}

        # Categories of turbostat metrics.
        self._categories = None

        # A dictionary mapping 'pandas.DataFrame' column names to the corresponding turbostat metric
        # name. E.g., column "Totals-CPU%c1" will be mapped to 'CPU%c1'.
        self._col2metric = {}

        dfs = self._load_dfs(rsts)

        # Build a list of all the available turbostat metric names. Maintain the turbostat-defined
        # order.
        metrics = []
        metrics_set = set()
        for metric in self._col2metric.values():
            if metric not in metrics_set:
                metrics.append(metric)
                metrics_set.add(metric)

        self._categorize_metrics(metrics)
        defs = TurbostatDefs.TurbostatDefs(metrics)
        super().__init__(dfs, outdir, basedir=basedir, defs=defs)

        for colname, metric in self._col2metric.items():
            if metric not in self._defs.info:
                continue

            self._defs.info[colname] = self._defs.info[metric].copy()
            self._defs.info[colname]["name"] = colname
