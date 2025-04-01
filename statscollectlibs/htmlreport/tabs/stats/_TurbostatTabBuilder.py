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
from typing import Any
from pepclibs.helperlibs import Trivial, Human
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.parsers import TurbostatParser
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.htmlreport.tabs import TabConfig
from statscollectlibs.htmlreport.tabs.stats import _StatTabBuilderBase
from statscollectlibs.htmlreport.tabs.stats._StatTabBuilderBase import CDTypedDict
from statscollectlibs.result.LoadedResult import LoadedResult

class TurbostatTabBuilder(_StatTabBuilderBase.StatTabBuilderBase):
    """Provide the capability of populating the turbostat statistics tab."""

    name = "Turbostat"
    stnames = ["turbostat"]

    def __init__(self,
                 lrsts: list[LoadedResult],
                 outdir: Path,
                 basedir: Path | None = None,
                 xmetric: str | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test result objects to include in the tab.
            outdir: The output directory in which to create the sub-directory for the container tab.
            basedir: The base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
            xmetric: Name of the metric to use for the X-axis of the plots. If not provided, the
                     X-axis will use the time elapsed since the beginning of the measurements.
        """

        super().__init__(lrsts, outdir / self.name, basedir=basedir, xcolname=xmetric)

        self._categories = self._get_merged_categories(lrsts)

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

        # Build the MDC.
        cdd = super()._build_cdd(mdd, colnames=colnames)

        if not colnames:
            return cdd

        # The description in MDC is based on MDD description and does not mention the scope. Adjust
        # the description.
        for colname, cd in cdd.items():
            if not colname.startswith("System-"):
                continue

            short_func_name = TurbostatParser.get_totals_func_name(colname)
            full_func_name = TurbostatParser.TOTALS_FUNCS[short_func_name]
            title = Human.uncapitalize(cd["title"])
            cd["descr"] = f"{cd['descr']} Calculated by finding the {full_func_name} value of " \
                          f"the \"{title}\" metric across the system."

        return cdd

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
            colname = f"{sname}-{metric}"
            if colname not in self._cdd:
                # The metric does not exist for this scope, e.g., 'CPU0-Pkg%pc6'.
                continue

            dtab = self._build_dtab_cfg(colname, title=metric)
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

        # Remember: 'self._categories' refers to metric names, while 'self._mdd' refers to
        # column names.

        l3_ctabs: list[TabConfig.CTabConfig] = []

        # Create a combined level 3 C-tab for frequency-related metrics, both core and uncore.
        if "Frequency" in self._categories:
            metrics: list[str] = []
            for cs_metrics in self._categories["Frequency"].values():
                metrics += cs_metrics

            l3_ctab = self._build_ctab_cfg("Frequency", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a level 3 C-tab for C-state metrics.
        if "C-state" in self._categories:
            cs_l3_ctabs: list[TabConfig.CTabConfig] = []

            if "Hardware" in self._categories["C-state"]:
                metrics = self._categories["C-state"]["Hardware"]
                l3_ctab = self._build_ctab_cfg("Hardware", metrics, sname)
                if l3_ctab:
                    cs_l3_ctabs.append(l3_ctab)

            if "Requested" in self._categories["C-state"]:
                # The requested C-states category and their sub-categories.
                subcats = self._categories["C-state"]["Requested"]

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
        if "S-state" in self._categories:
            metrics = self._categories["S-state"]
            l3_ctab = self._build_ctab_cfg("S-states", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a combined level 3 C-tab for temperature and power metrics.
        metrics = []
        if "Power" in self._categories:
            metrics += self._categories["Power"]
        if "Temperature" in self._categories:
            metrics += self._categories["Temperature"]
        if metrics:
            l3_ctab = self._build_ctab_cfg("Power / Temperature", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a combined level 3 C-tab for the rest of the metrics.
        metrics = []
        if "Interrupts" in self._categories:
            metrics += self._categories["Interrupts"]
        if "Instructions" in self._categories:
            metrics += self._categories["Instructions"]
        if metrics:
            l3_ctab = self._build_ctab_cfg("Miscellaneous", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        if l3_ctabs:
            return TabConfig.CTabConfig(sname, ctabs=l3_ctabs)

        return None

    def get_tab_cfg(self) -> TabConfig.CTabConfig:
        """
        Get a 'TabConfig.DTabConfig' instance with the turbostat tab configuration.

        Returns:
            A 'TabConfig.DTabConfig' instance with the turbostat tab configuration.
        """

        l2_ctabs = []
        for sname in self._snames:
            l2_ctab = self._get_l2_tab_cfg(sname)
            if l2_ctab:
                l2_ctabs.append(l2_ctab)

        if l2_ctabs:
            return TabConfig.CTabConfig(self.name, ctabs=l2_ctabs)

        raise Error("no turbostat metrics found")

    def _get_merged_categories(self, lrsts: list[LoadedResult]) -> dict[str, Any]:
        """
        Merge categories from different results into a single dictionary (in case some of the test
        results include categories or metrics not present in other test results).

        Args:
            lrsts: The loaded test result objects to merge the categories for.

        Returns:
            The merged categories dictionary.
        """

        def _merge(merged_categories: dict[str, Any], categories: dict[str, Any]) -> None:
            """
            Recursively merge the contents of one dictionary into another. The recursion is because
            the categories dictionary can have nested dictionaries of varying depths.

            Args:
                merged_categories: The dictionary to merge into.
                categories: The dictionary to merge from.
            """

            cat_value: dict[str, Any] | list[str]

            for category, cat_value in categories.items():
                if category not in merged_categories:
                    if isinstance(cat_value, list):
                        merged_categories[category] = []
                    else:
                        merged_categories[category] = {}

                if isinstance(cat_value, list):
                    merged_categories[category] = Trivial.list_dedup(merged_categories[category] +
                                                                     cat_value)
                else:
                    _merge(merged_categories[category], cat_value)

        merged_categories: dict[str, Any] = {}

        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                lstat = lres.lsts[stname]
                _merge(merged_categories, lstat.categories)

        return merged_categories
