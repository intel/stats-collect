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

import logging
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc import TurbostatMDC
from statscollectlibs.dfbuilders import _TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

_LOG = logging.getLogger()

class TurbostatTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the turbostat statistics tab."""

    name = "Turbostat"
    stname = "turbostat"

    def _get_summary_funcs(self, metric, sname):
        """
        Return the list of summary function names to include to the D-tab for metric 'metric'.
        """

        colname = _TurbostatDFBuilder.format_colname(metric, sname)
        colinfo = self._mdd[colname]
        unit = colinfo.get("unit")
        if not unit:
            funcs = ["max", "avg", "min", "std"]
        else:
            funcs = ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min", "std"]

        return funcs

    def _build_ctab_cfg(self, title, metrics, sname):
        """
        Build a and return a leaf level C-tab with a D-tab for every metric in 'metrics' and scope
        'sname'.
        """

        dtabs = []
        for metric in metrics:
            funcs = self._get_summary_funcs(metric, sname)
            dtab = self._build_def_dtab_cfg(metric, self._time_metric, funcs, self._hover_defs,
                                            title=metric)
            dtabs.append(dtab)

        if dtabs:
            return TabConfig.CTabConfig(title, dtabs=dtabs)

        return None

    def _get_default_tab_cfg(self, sname):
        """Get the C-tab for scope 'sname'."""

        l2_ctabs = []

        # Create an L2 C-tab for frequency-related metrics, both core and uncore.
        if "Frequency" in self._mdo.categories:
            metrics = []
            for freq_colnames in self._mdo.categories["Frequency"].values():
                metrics += freq_colnames

            ctab = self._build_ctab_cfg("Frequency", metrics, sname)
            if ctab:
                l2_ctabs.append(ctab)

#        # C-states are going to have the "C-states" L2 C-tab, and two nested L3 C-tabs for
#        # requestable and hardware C-states.
#        if "C-state" in self._mdo.categories:
#            cstate_l2_ctabs = []
#            if "Requested" in self._mdo.categories["C-state"]:
#                csres_colnames = []
#                csrate_colnames = []
#                cstime_colnames = []
#                cscnt_colnames = []
#
#                for colnames in self._mdo.categories["C-state"]["Requested"]:
#                    unit = self._mdo.mdd[colnames].get("unit")
#                    if unit:
#                        if unit == "%":
#                            csres_colnames.append(colnames)
#                        elif "requests/sec" in unit:
#                            csrate_colnames.append(colnames)
#                        elif "microsecond" in unit:
#                            cstime_colnames.append(colnames)
#                    else:
#                        cscnt_colnames.append(colnames)
#
#                l3_ctabs = []
#                l3_ctabs.append(build_ctab_cfg("Residency", csres_colnames))
#                l3_ctabs.append(build_ctab_cfg("Request rate", csrate_colnames))
#                l3_ctabs.append(build_ctab_cfg("Time in C-state ", cstime_colnames))
#                l3_ctabs.append(build_ctab_cfg("Count", cscnt_colnames))
#
#                cstate_l2_ctabs.append(TabConfig.CTabConfig("Requested", ctabs=l3_ctabs))
#
#            if "Hardware" in self._mdo.categories["C-state"]:
#                # Add hardware C-state residency D-tabs to a separate C-tab.
#                for colnames in self._mdo.categories["C-state"]["Hardware"]:
#                    if sname == "System":
#                        colnames.append(colnames)
#                    elif self._mdo.mdd[colnames].get("scope") in ("CPU", "core"):
#                        colnames.append(colnames)
#                hw_cs_tab = build_ctab_cfg("Hardware", colnames)
#
#        # Combine requested and hardware C-state C-tags into a single C-tab.
#        cstates_tab = TabConfig.CTabConfig("C-states", ctabs=[hw_cs_tab, req_tabs])
#
#        # Add frequency D-tabs to a separate C-tab.
#        if "S-state" in self._mdo.categories:
#            colnames = []
#            for colnames in self._mdo.categories["S-state"]:
#                colnames.append(colnames)
#            sstates_tab = build_ctab_cfg("S-states", colnames)
#
#        # Add temperature/power-related D-tabs to a separate C-tab.
#        all_tp_metrics = self._mdo.categories["Power"] + self._mdo.categories["Temperature"]
#        if sname == "System":
#            colnames = all_tp_metrics
#        else:
#            colnames = []
#            for colnames in all_tp_metrics:
#                if self._mdo.mdd[colnames].get("scope") in ("CPU", "core"):
#                    colnames.append(colnames)
#        tp_tab = build_ctab_cfg("Temperature / Power", colnames)
#
#        # Add miscellaneous D-tabs to a separate C-tab.
#        colnames = self._mdo.categories["Interrupts"] + self._mdo.categories["Instructions"]
#        misc_tab = build_ctab_cfg("Misc", colnames)

        if l2_ctabs:
            return TabConfig.CTabConfig(sname, ctabs=l2_ctabs)
        return None 

    def get_default_tab_cfg(self):
        """
        Build and return the "root" container tab ('CTabConfig') instance, titled 'self.name'. It
        will include "level 2" sub-tabs representing categories of metrics, such as "C-states". Some
        of the level 2 C-stabs may include level 3 C-tabs. And the leaf level is going ot be a D-tab
        (data tab). See 'TabBuilderBase' for more information on default tab configurations.
        """

        l2_ctabs = []
        for sname in self._snames:
            l2_ctab = self._get_default_tab_cfg(sname)
            if l2_ctab:
                l2_ctabs.append(l2_ctab)

        if l2_ctabs:
            return TabConfig.CTabConfig(self.name, ctabs=l2_ctabs)

        raise Error("no turbostat metrics found")

    def _load_dfs(self, rsts):
        """Load 'pandas.DataFrames' from raw turbostat statistics files in 'rsts'."""

        dfs = {}
        dfbldr = _TurbostatDFBuilder.TurbostatDFBuilder(cpunum=self._cpunum)

        for res in rsts:
            if "turbostat" not in res.info["stinfo"]:
                continue
            dfs[res.reportid] = res.load_stat("turbostat", dfbldr)
            self._col2metric.update(dfbldr.col2metric)
            self._hover_defs[res.reportid] = res.get_label_defs("turbostat")

        return dfs

    def _check_cpunum(self, rsts):
        """Check if the results are for the same CPU number."""

        stname = "turbostat"
        infos = {}

        for res in rsts:
            if stname not in res.info["stinfo"]:
                continue
            cpunum = res.info.get("cpunum")
            if cpunum not in infos:
                infos[cpunum] = []
            infos[cpunum].append(res.dirpath)
            self._cpunum = cpunum

        if len(infos) < 2:
            return

        msg = ""
        max_cnt = 0
        for cpunum, paths in infos.items():
            if len(paths) > max_cnt:
                max_cnt = len(paths)
                self._cpunum = cpunum
            if cpunum is None:
                cpustr = "no measured CPU"
            else:
                cpustr = f"CPU{cpunum}:"

            msg += f"\n  * {cpustr}"
            for path in paths:
                msg += f"\n    * {path}"

        _LOG.notice("a mix of measured CPU numbers in %s statistics detected:%s", stname, msg)
        _LOG.notice("will use the following measured CPU number for all results: %s", str(self._cpunum))

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. The arguments are the same as in '_TabBuilderBase.TabBuilderBase()'
        except for the following.
          * rsts - an iterable collection of 'RORawResult' instances for which data should be
                   included in the built tab.
        """

        self._cpunum = None
        self._mdo = None
        self._hover_defs = {}
        self._time_metric = "TimeElapsed"
        self._snames = []

        # A dictionary mapping 'pandas.DataFrame' column names to the corresponding turbostat metric
        # name. E.g., column "Totals-CPU%c1" will be mapped to 'CPU%c1'.
        self._col2metric = {}

        self._check_cpunum(rsts)
        dfs = self._load_dfs(rsts)

        # Build a list of all the available turbostat metric names. Maintain the turbostat-defined
        # order.
        metrics = []
        metrics_set = set()
        for metric in self._col2metric.values():
            if metric not in metrics_set:
                metrics.append(metric)
                metrics_set.add(metric)

        # Create a metrics definition object which covers all metrics across all the results.
        self._mdo = TurbostatMDC.TurbostatMDC(metrics)

        # Build a metrics definition dictionary describing all columns in the dataframe.
        mdd = {}
        time_colnames = []
        for colname, metric in self._col2metric.items():
            if metric not in self._mdo.mdd:
                continue

            if metric == "TimeElapsed":
                time_colnames.append(colname)
            mdd[colname] = self._mdo.mdd[metric].copy()
            mdd[colname]["name"] = colname

        outdir = outdir / self.name
        super().__init__(dfs, outdir, basedir=basedir, mdd=mdd)

        # Convert the elapsed time columns in the dataframe to the "datetime" format so that
        # diagrams use a human-readable format.
        for time_colname in time_colnames:
            for df in dfs.values():
                df[time_colname] = pandas.to_datetime(df[time_colname], unit="s")

        # Build the list of scope names.
        found_snames = set()
        for colname in self._mdd:
            sname, _ = _TurbostatDFBuilder.split_colname(colname)
            if not sname:
                continue
            if sname not in found_snames:
                found_snames.add(sname)
                self._snames.append(sname)
