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

from pathlib import Path
import pandas
from statscollectlibs.mdc import MDCBase
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.dfbuilders import _TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase
from statscollectlibs.htmlreport.tabs._TabBuilderBase import CDTypedDict

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
        cdd = self._build_cdd(mdd, colnames=colnames)
        super().__init__(dfs, cdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")

    def _build_cdd(self,
                   mdd: dict[str, MDTypedDict],
                   colnames: list[str] | None = None) -> dict[str, CDTypedDict]:
        """
        Build a columns definition dictionary (CDD) that describes columns in dataframes.

        Args:
            mdd: The metrics definition dictionary (MDD) for metrics that will be included in the
                 tab. It describes metrics, while CDD describes columns. Coulumns may include the
                 scope as well. For example, there is a "C1%" metric, which may have 2 columns -
                 "System-C1%" for system-wide C1 residency, and "CPU5-C1%" C1 residency for CPU5.
            colnames: list of dataframe column names to use for the CDD. By default, assume column
                      names are the same as metric names.

        Returns:
            CDTypedDict: The Columns Definition Dictionary.
        """

        cdd = super()._build_cdd(mdd, colnames=colnames)

        if not colnames:
            return cdd

        # Adjust the descriptions of the columns.
        for colname in colnames:
            cd = cdd[colname]
            sname, metric = _TurbostatDFBuilder.split_colname(colname)

            if sname == "System":
                if cd["scope"] == "system":
                    # The metric is already system-wide, the current description already describes
                    # this aspect.
                    continue

                if not metric.endswith("_rate"):
                    cd["descr"] += f" This represents the total {cd['title']} across all CPUs in " \
                                   f"the system."
                else:
                    cd["descr"] += f" This represents the average {cd['title']} across all CPUs " \
                                   f"in the system."

        return cdd

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
