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

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.parsers import TurbostatParser
from statscollectlibs.mdc import MDCBase, TurbostatMDC
from statscollectlibs.dfbuilders import _TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase
from statscollectlibs.result.LoadedResult import LoadedResult

class TurbostatTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the turbostat statistics tab."""

    name = "Turbostat"
    stname = "turbostat"

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test result objects to include in the tab.
            outdir: The output directory in which to create the sub-directory for the container tab.
            basedir: The base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._time_metric = "TimeElapsed"

        self._mdo: TurbostatMDC.TurbostatMDC
        self._snames: list[str] = []

        dfs = self._load_dfs(lrsts)

        metrics: list[str] = []
        metrics_set: set[str] = set()
        snames_set: set[str] = set()

        # Build a the list metrics and scope names.
        for df in dfs.values():
            for colname in df.columns:
                sname, metric = _TurbostatDFBuilder.split_colname(colname)
                if sname is not None and sname not in snames_set:
                    snames_set.add(sname)
                    self._snames.append(sname)
                if metric not in metrics_set:
                    metrics_set.add(metric)
                    metrics.append(metric)

        # Create a metrics definition object which covers all metrics across all the results.
        self._mdo = TurbostatMDC.TurbostatMDC(metrics)

        # The 'slf.mdo.mdd' Metrics Definition Dictionary includes metric names. But the dataframes
        # include column names. Build a Metrics Definition Dictionary for column names.
        colnames: list[str] = []
        colnames_set: set[str] = set()

        for df in dfs.values():
            for colname in df.columns:
                _, metric = _TurbostatDFBuilder.split_colname(colname)
                if metric not in self._mdo.mdd:
                    continue
                if colname not in colnames_set:
                    colnames.append(colname)
                    colnames_set.add(colname)

        mdd = self._build_mdd(self._mdo.mdd, colnames)

        super().__init__(dfs, mdd, outdir / self.name, basedir=basedir)

        # Convert the elapsed time column in dataframes to the "datetime" format so that
        # diagrams use a human-readable format.
        for df in dfs.values():
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

        for metric, mdef in mdd.items():
            name = TurbostatParser.get_totals_func_name(metric)
            if name is not None:
                name = TurbostatParser.TOTALS_FUNCS[name] # Get user-friendly name.
                mdef["descr"] = f"{mdef['descr']} Calculated by finding the {name} of " \
                                f"\"{mdef['name']}\" across the system."

        return new_mdd

    def _build_ctab_cfg(self, title: str, metrics: list[str], sname: str):
        """
        Build and return a leaf-level C-tab with a D-tab for every metric in 'metrics' and scope
        'sname'.

        Args:
            title: The title of the C-tab.
            metrics: A list of metrics to include in the D-tabs.
            sname: The scope name for the metrics.

        Returns:
            TabConfig.CTabConfig: The configuration for the C-tab containing D-tabs for each metric.
            None: If no valid metrics are found for the given scope.
        """

        dtabs = []
        for metric in metrics:
            colname = _TurbostatDFBuilder.format_colname(metric, sname)
            if colname not in self._mdd:
                # The metric does not exist for this scope, e.g., 'CPU0-Pkg%pc6'.
                continue

            dtab = self._build_def_dtab_cfg(colname, self._time_metric, {}, title=metric)
            dtabs.append(dtab)

        if dtabs:
            return TabConfig.CTabConfig(title, dtabs=dtabs)

        return None

    def _get_l2_tab_cfg(self, sname: str) -> TabConfig.CTabConfig | None:
        """
        Assemble the C-tab configuration object for the given scope name.

        This method creates a hierarchical configuration of tabs (C-tabs) based on various metric
        categories such as Frequency, C-state, and so on.

        Args:
            sname: The scope name for which the C-tab configuration is being assembled.

        Returns:
            TabConfig.CTabConfig: The assembled C-tab configuration object for the given scope name.
            None: If no relevant metrics are found.
        """

        # Remember: 'self._mdo.categories' refers to metric names, while 'self._mdd' refers to
        # column names.

        l3_ctabs: list[TabConfig.CTabConfig] = []

        # Create a combined level 3 C-tab for frequency-related metrics, both core and uncore.
        if "Frequency" in self._mdo.categories:
            metrics: list[str] = []
            for cs_metrics in self._mdo.categories["Frequency"].values():
                metrics += cs_metrics

            l3_ctab = self._build_ctab_cfg("Frequency", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a level 3 C-tab for C-state metrics.
        if "C-state" in self._mdo.categories:
            cs_l3_ctabs: list[TabConfig.CTabConfig] = []

            if "Hardware" in self._mdo.categories["C-state"]:
                metrics = self._mdo.categories["C-state"]["Hardware"]
                l3_ctab = self._build_ctab_cfg("Hardware", metrics, sname)
                if l3_ctab:
                    cs_l3_ctabs.append(l3_ctab)

            if "Requested" in self._mdo.categories["C-state"]:
                # The requested C-states category and their sub-categories.
                subcats = self._mdo.categories["C-state"]["Requested"]

                l4_ctabs: list[TabConfig.CTabConfig] = []

                for subcat in ("Residency", "Count", "Request Rate", "Average Time"):
                    if subcat in subcats:
                        l3_ctab = self._build_ctab_cfg(subcat, subcats[subcat], sname)
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

    def get_default_tab_cfg(self) -> TabConfig.CTabConfig:
        """
        Get a 'TabConfig.DTabConfig' instance with the default turbostat tab configuration. See
        '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.

        Returns:
            A 'TabConfig.DTabConfig' instance with the default turbostat tab configuration.
        """

        l2_ctabs = []
        for sname in self._snames:
            l2_ctab = self._get_l2_tab_cfg(sname)
            if l2_ctab:
                l2_ctabs.append(l2_ctab)

        if l2_ctabs:
            return TabConfig.CTabConfig(self.name, ctabs=l2_ctabs)

        raise Error("no turbostat metrics found")

    def _load_dfs(self, lrsts: list[LoadedResult]) -> dict[str, pandas.DataFrame]:
        """
        Load the turbostat statistics dataframes for results in 'lrsts'.

        Args:
            lrsts: The loaded test result objects to load the dataframes for.

        Returns:
            A dictionary with keys being report IDs and values being turbostat statistics
            dataframes.
        """

        dfs = {}
        for lres in lrsts:
            if self.stname not in lres.res.info["stinfo"]:
                continue

            lres.load_stat(self.stname)

            dfs[lres.reportid] = lres.lsts[self.stname].df

        return dfs
