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
from statscollectlibs.mdc import MDCBase
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

class InterruptsTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability to populate the interrupts statistics tab."""

    name = "Interrupts"
    stname = "interrupts"

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test results to include in the tab.
            outdir: The output directory in which to create the sub-directory for the container tab.
            basedir: The base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._time_metric = "TimeElapsed"
        self._ts_metric = "Timestamp"

        # The column names to include in the interrupts statistics tab.
        self._tab_colnames: list[str] = []

        dfs = self._load_dfs(lrsts)

        # Compose the list of all column names and all metrics in all dataframes.
        colnames = []
        colnames_set = set()
        for df in dfs.values():
            for colname in df.columns:
                if colname not in colnames_set:
                    colnames.append(colname)
                    colnames_set.add(colname)

                    # Keep in mind that there may be columns not prefixed by scope, e.g., ones that
                    # came from the labels
                    split = colname.split("-", 1)
                    if len(split) == 2:
                        self._tab_colnames.append(colname)

        mdd = self._get_merged_mdd(lrsts)
        cdd = self._build_mdd(mdd, colnames)
        super().__init__(dfs, cdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")

    def _build_mdd(self, mdd: dict[str, MDCBase.MDTypedDict],
                   colnames: list[str]) -> dict[str, _TabBuilderBase.CDTypedDict]:
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

        # Scope -> Count/Rate -> list of 'TabConfig.DTabConfig' objects.
        dtabs: dict[str, dict[str, list[TabConfig.DTabConfig]]] = {}

        for colname in self._tab_colnames:
            scope, metric = colname.split("-", 1)
            if scope not in dtabs:
                dtabs[scope] = {"Interrupts Rate": [], "Interrupts Count": []}

            dtab = self._build_def_dtab_cfg(colname, self._time_metric, {}, title=metric)
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

    def _load_dfs(self, lrsts: list[LoadedResult]) -> dict[str, pandas.DataFrame]:
        """
        Load the interrupts statistics dataframes for results in 'lrsts'.

        Args:
            lrsts: The loaded test result objects to load the dataframes for.

        Returns:
            A dictionary with keys being report IDs and values being interrupts statistics
            dataframes.
        """

        dfs = {}
        for lres in lrsts:
            if self.stname not in lres.res.info["stinfo"]:
                continue

            lres.load_stat(self.stname)

            dfs[lres.reportid] = lres.lsts[self.stname].df

        return dfs

    def _get_merged_mdd(self, lrsts: list[LoadedResult]) -> dict[str, MDCBase.MDTypedDict]:
        """
        Merge MDDs from different results into a single dictionary (in case some results include
        metrics not present in other test results).

        Args:
            lrsts: The loaded test result objects to merge the MDDs for.

        Returns:
            The merged MDD.
        """

        mdd: dict[str, MDCBase.MDTypedDict] = {}
        for lres in lrsts:
            if self.stname not in lres.res.info["stinfo"]:
                continue

            mdd.update(lres.lsts[self.stname].mdd)

        return mdd
