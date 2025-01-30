# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the capability to populate the interrupts statistics tab.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

import string
from pathlib import Path
import pandas
from statscollectlibs.mdc import MDCBase, InterruptsMDC
from statscollectlibs.dfbuilders import _InterruptsDFBuilder
from statscollectlibs.rawresultlibs.RORawResult import RORawResult
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

class InterruptsTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability to populate the interrupts statistics tab."""

    name = "Interrupts"
    stname = "interrupts"

    def __init__(self, rsts: list[RORawResult], outdir: Path, basedir: Path | None = None):
        """
        Class constructor.

        Args:
            rsts: A list of raw results to include in the tab.
            outdir: The output directory in which to create the sub-directory for the container tab.
            basedir: The base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._time_metric = "TimeElapsed"
        self._ts_metric = "Timestamp"

        self._hover_defs: dict[str, dict[str, _TabBuilderBase.MDTypedDict]] = {}

        # The column names to include in the interrupts statistics tab.
        self._tab_colnames: list[str] = []

        self._cpunum = self._get_and_check_cpunum(rsts)

        dfs = self._load_dfs(rsts)

        # Compose the list of all column names and all metrics in all dataframes.
        colnames = []
        colnames_set = set()
        metrics = []
        metrics_set = set()
        for df in dfs.values():
            for colname in df.columns:
                if colname not in colnames_set:
                    colnames.append(colname)
                    colnames_set.add(colname)

                    if colname not in (self._time_metric, self._ts_metric):
                        self._tab_colnames.append(colname)

                metric = colname.split("-", 1)[-1]
                if metric not in metrics_set:
                    metrics.append(metric)
                    metrics_set.add(metric)

        mdo = InterruptsMDC.InterruptsMDC()
        mdo.mangle(metrics)

        mdd = self._build_mdd(mdo.mdd, colnames)

        super().__init__(dfs, mdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")

    def _build_mdd(self, mdd: dict[str, MDCBase.MDTypedDict],
                   colnames: list[str]) -> dict[str, _TabBuilderBase.MDTypedDict]:
        """
        Build a new metrics definition dictionary that describes all columns in the dataframe. This
        is applicable to dataframes where columns follow the "<scope name>-<metric name>" format.

        Args:
            mdd: The metrics definition dictionary from one of the 'MCDBase' sub-classes. This
                 dictionary should include all the metrics referenced in 'colnames'.
            colnames: the list of column names in the dataframe.

        Returns:
            A new metrics definition dictionary that describes all columns in the dataframe.
        """

        new_mdd = super()._build_mdd(mdd, colnames)

        # Adjust the descriptions of the columns.
        for colname in self._tab_colnames:
            md = new_mdd[colname]
            scope, metric = colname.split("-", 1)

            # Turn column scope like "CPU5" to "CPU", to make it comparable to metric scopes.
            column_scope = scope.rstrip(string.digits)
            # Capitalize the metric scope to make it comparable to the column scope.
            metric_scope = md["scope"].capitalize()

            if column_scope == metric_scope:
                continue

            if column_scope == "System":
                if md["scope"] == "System":
                    # The metric is already system-wide, the description takes this into account.
                    continue

                if not metric.endswith("_rate"):
                    md["descr"] += f" This represents the total {md['title']} across all CPUs in " \
                                   f"the system."
                else:
                    md["descr"] += f" This represents the average {md['title']} across all CPUs " \
                                   f"in the system."

        return new_mdd

    def get_default_tab_cfg(self) -> TabConfig.CTabConfig:
        """
        Get a 'TabConfig.DTabConfig' instance with the default interrupts tab configuration. See
        '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.

        Returns:
            A 'TabConfig.DTabConfig' instance with the default interrupts tab configuration.
        """

        # Define which summary functions should be included in the generated summary table.
        smry_funcs = {}
        for colname in self._tab_colnames:
            smry_funcs[colname] = ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg", "min",
                                   "std"]

        # Scope -> Count/Rate -> list of 'TabConfig.DTabConfig' objects.
        dtabs: dict[str, dict[str, list[TabConfig.DTabConfig]]] = {}

        for colname in self._tab_colnames:
            scope, metric = colname.split("-", 1)
            if scope not in dtabs:
                dtabs[scope] = {"Interrupts Rate": [], "Interrupts Count": []}

            dtab = self._build_def_dtab_cfg(colname, self._time_metric, smry_funcs,
                                            self._hover_defs, title=metric)
            if metric.endswith("_rate"):
                dtabs[scope]["Interrupts Rate"].append(dtab)
            else:
                dtabs[scope]["Interrupts Count"].append(dtab)

        ctabs = []
        for scope, scope_info in dtabs.items():
            category_ctabs = []
            for category, category_dtabs in scope_info.items():
                category_ctabs.append(TabConfig.CTabConfig(category, dtabs=category_dtabs))
            ctabs.append(TabConfig.CTabConfig(scope, ctabs=category_ctabs))

        return TabConfig.CTabConfig(self.name, ctabs=ctabs)

    def _load_dfs(self, rsts: list[RORawResult]) -> dict[str, pandas.DataFrame]:
        """
        Load the interrupts statistics dataframes for raw results in 'rsts'.

        Args:
            rsts: The raw results to process and load the dataframes for.

        Returns:
            A dictionary with keys being report IDs and values being interrupts statistics
            dataframes.
        """

        dfbldr = _InterruptsDFBuilder.InterruptsDFBuilder(cpunum=self._cpunum)

        dfs = {}
        for res in rsts:
            if self.stname not in res.info["stinfo"]:
                continue

            dfs[res.reportid] = res.load_stat(self.stname, dfbldr)
            self._hover_defs[res.reportid] = res.get_label_defs(self.stname)

        return dfs
