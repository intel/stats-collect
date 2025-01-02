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

from statscollectlibs.mdc import TurbostatMDC
from statscollectlibs.dfbuilders import _TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

class TurbostatTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the turbostat statistics tab."""

    name = "Turbostat"
    stname = "turbostat"

    def _get_default_tab_cfg(self, colnames, smry_funcs, sname):
        """
        Get the default tab configuration which is populated with 'metrics', 'smry_funcs' and using
        the C-states in 'self._hw_cstates' and 'self._req_cstates'.
        """

        def build_ctab_cfg(ctab_name, tab_metrics):
            """Build a C-tab config named 'ctab_name' for 'tab_metrics'."""

            tab_metrics = [col for col, raw in self._col2metric.items() if raw in tab_metrics]
            dtabs = []
            for metric in tab_metrics:
                if metric not in self._mdd or metric not in colnames:
                    continue
                dtab = self._build_def_dtab_cfg(metric, self._time_metric, smry_funcs,
                                                self._hover_defs, title=self._col2metric[metric])
                dtabs.append(dtab)
            return TabConfig.CTabConfig(ctab_name, dtabs=dtabs)

        # Add frequency D-tabs to a separate C-tab.
        metrics = []
        for names in self._mdo.categories["Frequency"].values():
            metrics += names
        freq_tab = build_ctab_cfg("Frequency", metrics)

        # Add requested C-state residency/count D-tabs tabs to separate C-tabs.
        csres_metrics = []
        csrate_metrics = []
        cstime_metrics = []
        cscnt_metrics = []
        for name in self._mdo.categories["C-state"]["Requested"]:
            unit = self._mdo.mdd[name].get("unit")
            if unit:
                if unit == "%":
                    csres_metrics.append(name)
                elif "requests/sec" in unit:
                    csrate_metrics.append(name)
                elif "microsecond" in unit:
                    cstime_metrics.append(name)
            else:
                cscnt_metrics.append(name)
        csres_tab = build_ctab_cfg("Residency", csres_metrics)
        csrate_tab = build_ctab_cfg("Request rate", csrate_metrics)
        cstime_tab = build_ctab_cfg("Time in C-state ", cstime_metrics)
        cscnt_tab = build_ctab_cfg("Count", cscnt_metrics)
        req_tabs = TabConfig.CTabConfig("Requested", ctabs=[csres_tab, csrate_tab, cstime_tab,
                                                            cscnt_tab])

        # Add hardware C-state residency D-tabs to a separate C-tab.
        metrics = ["Busy%"]
        for name in self._mdo.categories["C-state"]["Hardware"]:
            if sname == _TurbostatDFBuilder.TOTALS_SNAME:
                metrics.append(name)
            elif self._mdo.mdd[name].get("scope") in ("CPU", "core"):
                metrics.append(name)
        hw_cs_tab = build_ctab_cfg("Hardware", metrics)

        # Combine requested and hardware C-state C-tags into a single C-tab.
        cstates_tab = TabConfig.CTabConfig("C-states", ctabs=[hw_cs_tab, req_tabs])

        # Add frequency D-tabs to a separate C-tab.
        metrics = []
        for name in self._mdo.categories["S-state"]:
            metrics.append(name)
        sstates_tab = build_ctab_cfg("S-states", metrics)

        # Add temperature/power-related D-tabs to a separate C-tab.
        all_tp_metrics = self._mdo.categories["Power"] + self._mdo.categories["Temperature"]
        if sname == _TurbostatDFBuilder.TOTALS_SNAME:
            metrics = all_tp_metrics
        else:
            metrics = []
            for name in all_tp_metrics:
                if self._mdo.mdd[name].get("scope") in ("CPU", "core"):
                    metrics.append(name)
        tp_tab = build_ctab_cfg("Temperature / Power", metrics)

        # Add miscellaneous D-tabs to a separate C-tab.
        metrics = self._mdo.categories["Interrupts"] + self._mdo.categories["Instructions"]
        misc_tab = build_ctab_cfg("Misc", metrics)

        return TabConfig.CTabConfig(sname, ctabs=[freq_tab, cstates_tab, sstates_tab, tp_tab,
                                                  misc_tab])

    def get_default_tab_cfg(self):
        """
        Build and return a 'TabConfig.CTabConfig' instance, titled 'self.name', containing tab
        configurations which represent different metrics within raw turbostat statistic files.

        The hierarchy of the tabs will will only include turbostat metrics which are common to all
        results.

        See '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.
        """

        # Find metrics which appear in the raw turbostat statistic files.
        metric_sets = [set(sdf.columns) for sdf in self._dfs.values()]
        metrics = set.union(*metric_sets)

        # Limit metrics to only those with definitions.
        metrics.intersection_update(set(self._mdd.keys()))

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
            categorised_metrics[sname].add(metric)

        l2_tabs = []
        for sname, scope_metrics in categorised_metrics.items():
            l2_tabs.append(self._get_default_tab_cfg(scope_metrics, smry_funcs, sname))

        return TabConfig.CTabConfig(self.name, ctabs=l2_tabs)

    def _load_dfs(self, rsts):
        """Load 'pandas.DataFrames' from raw turbostat statistics files in 'rsts'."""

        dfs = {}
        tstat_rsts = [res for res in rsts if "turbostat" in res.info["stinfo"]]

        for res in tstat_rsts:
            cpunum = res.info.get("cpunum")
            dfbldr = _TurbostatDFBuilder.TurbostatDFBuilder(cpunum=cpunum)

            dfs[res.reportid] = res.load_stat("turbostat", dfbldr)
            self._col2metric.update(dfbldr.col2metric)
            self._hover_defs[res.reportid] = res.get_label_defs("turbostat")

        return dfs

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. The arguments are the same as in '_TabBuilderBase.TabBuilderBase()'
        except for the following.
          * rsts - an iterable collection of 'RORawResult' instances for which data should be
                   included in the built tab.
        """

        outdir = outdir / self.name
        self._time_metric = "TimeElapsed"
        self._hover_defs = {}
        self._mdo = None

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

        self._mdo = TurbostatMDC.TurbostatMDC(metrics)
        mdd = {}

        for colname, metric in self._col2metric.items():
            if metric not in self._mdo.mdd:
                continue

            mdd[colname] = self._mdo.mdd[metric].copy()
            mdd[colname]["name"] = colname

        mdd[self._time_metric] = self._mdo.mdd[self._time_metric].copy()
        super().__init__(dfs, outdir, basedir=basedir, mdd=mdd)
