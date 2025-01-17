# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

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

    def _get_smry_funcs(self, colname):
        """
        Return the list of summary function names to include to the D-tab for dataframe column
        'colname'.
        """

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
            colname = _TurbostatDFBuilder.format_colname(metric, sname)
            if colname not in self._mdd:
                # The metric does not exist in for this scope, e.g., 'CPU0-Pkg%pc6'.
                continue

            smry_funcs = {}
            smry_funcs[colname] = self._get_smry_funcs(colname)
            dtab = self._build_def_dtab_cfg(colname, self._time_metric, smry_funcs,
                                            self._hover_defs, title=metric)
            dtabs.append(dtab)

        if dtabs:
            return TabConfig.CTabConfig(title, dtabs=dtabs)

        return None

    def _get_l2_tab_cfg(self, sname):
        """Assemble the C-tab configuration object for scope 'sname'."""

        # Remember: 'self._mdo.categories' refers to metric names, while 'self._mdd' refers to
        # column names.

        l3_ctabs = []

        # Create a combined level 3 C-tab for frequency-related metrics, both core and uncore.
        if "Frequency" in self._mdo.categories:
            metrics = []
            for cs_metrics in self._mdo.categories["Frequency"].values():
                metrics += cs_metrics

            l3_ctab = self._build_ctab_cfg("Frequency", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a level 3 C-tab for C-state metrics.
        if "C-state" in self._mdo.categories:
            cs_l3_ctabs = []

            if "Hardware" in self._mdo.categories["C-state"]:
                metrics = self._mdo.categories["C-state"]["Hardware"]
                l3_ctab = self._build_ctab_cfg("Hardware", metrics, sname)
                if l3_ctab:
                    cs_l3_ctabs.append(l3_ctab)

            if "Requested" in self._mdo.categories["C-state"]:
                # The level 3 "Requested" C-tab is going to have level 4 C-tabs for different
                # sub-categories of metrics.
                csres_metrics = []
                csrate_metrics = []
                cstime_metrics = []
                cscnt_metrics = []

                for metric in self._mdo.categories["C-state"]["Requested"]:
                    unit = self._mdo.mdd[metric].get("unit")
                    if unit:
                        if unit == "%":
                            csres_metrics.append(metric)
                        elif "requests/sec" in unit:
                            csrate_metrics.append(metric)
                        elif "microsecond" in unit:
                            cstime_metrics.append(metric)
                    else:
                        cscnt_metrics.append(metric)

                l4_ctabs = []

                l3_ctab = self._build_ctab_cfg("Residency", csres_metrics, sname)
                if l3_ctab:
                    l4_ctabs.append(l3_ctab)

                l3_ctab = self._build_ctab_cfg("Request rate", csrate_metrics, sname)
                if l3_ctab:
                    l4_ctabs.append(l3_ctab)

                l3_ctab = self._build_ctab_cfg("Time in C-state ", cstime_metrics, sname)
                if l3_ctab:
                    l4_ctabs.append(l3_ctab)

                l3_ctab = self._build_ctab_cfg("Count", cscnt_metrics, sname)
                if l3_ctab:
                    l4_ctabs.append(l3_ctab)

                if l4_ctabs:
                    cs_l3_ctabs.append(TabConfig.CTabConfig("Requested", ctabs=l4_ctabs))

            if cs_l3_ctabs:
                l3_ctab = TabConfig.CTabConfig("C-states", ctabs=cs_l3_ctabs)
                l3_ctabs.append(l3_ctab)

        # Add S-states level 3 C-tab.
        if "S-state" in self._mdo.categories:
            metrics = self._mdo.categories["S-state"]
            l3_ctab = self._build_ctab_cfg("S-states", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a combined level 3 C-tab for temperature and power metrics.
        metrics = []
        if "Power" in self._mdo.categories:
            metrics += self._mdo.categories["Power"]
        if "Temperature" in self._mdo.categories:
            metrics += self._mdo.categories["Temperature"]
        if metrics:
            l3_ctab = self._build_ctab_cfg("Power / Temperature", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a combined level 3 C-tab for the rest of the metrics.
        metrics = []
        if "Interrupts" in self._mdo.categories:
            metrics += self._mdo.categories["Interrupts"]
        if "Instructions" in self._mdo.categories:
            metrics += self._mdo.categories["Instructions"]
        if metrics:
            l3_ctab = self._build_ctab_cfg("Miscellaneous", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        if l3_ctabs:
            return TabConfig.CTabConfig(sname, ctabs=l3_ctabs)

        return None

    def get_default_tab_cfg(self):
        """
        Build and return the "root" container tab ('CTabConfig') instance, titled 'self.name'. It
        will include level 2 C-tabs representing the scope (e.g., "System"), then level 3 C-tabs for
        categories of metrics (e.g., "C-states"). The leaf level is going to be D-tabs (data tabs),
        one D-tab for a metric. See 'TabBuilderBase' for more information on default tab
        configurations.
        """

        l2_ctabs = []
        for sname in self._snames:
            l2_ctab = self._get_l2_tab_cfg(sname)
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
        self._snames = []
        self._time_metric = "TimeElapsed"

        # A dictionary mapping 'pandas.DataFrame' column names to the corresponding turbostat metric
        # name. E.g., column "Totals-CPU%c1" will be mapped to 'CPU%c1'.
        self._col2metric = {}

        self._cpunum = self._get_and_check_cpunum(rsts)
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
            mdd[colname]["colname"] = colname

        outdir = outdir / self.name
        super().__init__(dfs, mdd, outdir, basedir=basedir)

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
