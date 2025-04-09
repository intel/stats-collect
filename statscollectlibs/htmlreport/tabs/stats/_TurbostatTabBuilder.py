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
from typing import Any, cast
from pepclibs.helperlibs import Trivial, Human
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.parsers import TurbostatParser
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.htmlreport.tabs.stats import _StatTabBuilderBase
from statscollectlibs.htmlreport.tabs.stats._StatTabBuilderBase import CDTypedDict
from statscollectlibs.htmlreport.tabs._TabConfig import CTabConfig
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

    def _get_category_metrics(self, category_path: list[str]) -> list[str]:
        """
        Retrieve the list of metrics for a given category path.

        Args:
            category_path: A list of the 'self._categories' dictionary keys representing the path to
                           navigate through.

        Returns:
             A list of metrics for the specified category path, or an empty list if the path does
             not exist.
        """

        categories = self._categories
        for cat in category_path:
            if cat not in categories:
                return []
            categories = categories[cat]

        return cast(list[str], categories)

    def _get_hover_colnames(self, metric: str, sname: str) -> list[str]:
        """
        Generate a list of column names to display as scatter plot hover text for a given metric and
        scope.

        Hover columns are selectively added for specific metrics to optimize memory and storage
        usage.

        Args:
            metric: The name of the metric for which hover column names are to be generated.
            sname: The scope name associated with the metric.

        Returns:
            A list of column names relevant to the given metric to be included as hover text in the
            scatter plot.
        """

        colname = f"{sname}-{metric}"
        if colname not in self._cdd:
            return []

        cd = self._cdd[colname]

        hover_metrics: list[str] = []

        if metric == "Bzy_MHz":
            # Add power and C-state metrics.
            hover_metrics.append("PkgWatt")
            hover_metrics += self._get_category_metrics(["C-state", "Requested", "Residency"])
            hover_metrics += self._get_category_metrics(["C-state", "Hardware"])

        if cd["categories"] == ["Frequency", "Uncore"]:
            # Add other domains' uncore frequency metrics.
            hover_metrics += self._get_category_metrics(["Frequency", "Uncore"])

        if cd["categories"] == ["C-state", "Hardware"]:
            # Add other hardware C-states' residency and requested C-state residency.
            hover_metrics += self._get_category_metrics(["C-state", "Hardware"])
            hover_metrics += self._get_category_metrics(["C-state", "Requested", "Residency"])

        if cd["categories"] == ["C-state", "Requested", "Residency"]:
            # Add other requested C-states' residency and hardware C-state residency.
            hover_metrics += self._get_category_metrics(["C-state", "Requested", "Residency"])
            hover_metrics += self._get_category_metrics(["C-state", "Hardware"])

        if metric in ("PkgWatt", "PkgWatt%TDP"):
            # Add other power metrics, CPU frequency, hardware C-state residency, and uncore
            # frequency.
            hover_metrics += self._get_category_metrics(["Power"])
            hover_metrics.append("Bzy_MHz")
            hover_metrics += self._get_category_metrics(["C-state", "Hardware"])
            hover_metrics += self._get_category_metrics(["Frequency", "Uncore"])

        hover_colnames = [f"{sname}-{metric}" for metric in hover_metrics]
        return [colname for colname in hover_colnames if colname in self._cdd]

    def _get_last_level_ctab_cfg(self, tabname: str, metrics: list[str], sname: str):
        """
        Create and return a last level container tab (C-tab) configuration object. This C-tab
        includes D-tabs for each metric in the category (provided via the 'metrics' list).

        Args:
            tabname: The name of the C-tab (as it appears in the tab hierachy in the HTML report).
            metrics: A list of metrics to the C-tab configuration object shold include.
            sname: The scope name for the metrics.

        Returns:
            The configuration object for the C-tab, including a D-tab for each metric, or None if no
            relevant metrics are found.
        """

        dtabs = []
        for metric in metrics:
            colname = f"{sname}-{metric}"
            if colname not in self._cdd:
                continue

            hover_colnames = self._get_hover_colnames(metric, sname)

            dtab = self._get_dtab_cfg(colname, title=metric, hover_colnames=hover_colnames)
            dtabs.append(dtab)

        if dtabs:
            return CTabConfig(tabname, dtabs=dtabs)

        return None

    def _get_l2_ctab_cfg(self, sname: str) -> CTabConfig | None:
        """
        Return a "level 2" C-tab configuration object for the given scope name (e.g., a C-tab for
        system-wide metrics, or a C-tab for CPU-specific metrics). The level 2 C-tab includes
        sub-C-tabs for different categories of metrics.

        Args:
            sname: The scope name for which the C-tab configuration is being assembled.

        Returns:
            The C-tab configuration object for the given scope name, or None if no relevant metrics
            are found.
        """

        # Remember: 'self._categories' refers to metric names, while 'self._mdd' refers to
        # column names.

        l3_ctabs: list[CTabConfig] = []

        # Create a combined level 3 C-tab for frequency-related metrics, both core and uncore.
        if "Frequency" in self._categories:
            metrics: list[str] = []
            for cs_metrics in self._categories["Frequency"].values():
                metrics += cs_metrics

            l3_ctab = self._get_last_level_ctab_cfg("Frequency", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a level 3 C-tab for C-state metrics.
        if "C-state" in self._categories:
            cs_l3_ctabs: list[CTabConfig] = []

            if "Hardware" in self._categories["C-state"]:
                metrics = self._categories["C-state"]["Hardware"]
                l3_ctab = self._get_last_level_ctab_cfg("Hardware", metrics, sname)
                if l3_ctab:
                    cs_l3_ctabs.append(l3_ctab)

            if "Requested" in self._categories["C-state"]:
                # The requested C-states category and their sub-categories.
                subcats = self._categories["C-state"]["Requested"]

                l4_ctabs: list[CTabConfig] = []

                for subcat in ("Residency", "Count", "Request Rate", "Average Time"):
                    if subcat in subcats:
                        l3_ctab = self._get_last_level_ctab_cfg(subcat, subcats[subcat], sname)
                        if l3_ctab:
                            l4_ctabs.append(l3_ctab)

                if l4_ctabs:
                    cs_l3_ctabs.append(CTabConfig("Requested", ctabs=l4_ctabs))

            if cs_l3_ctabs:
                l3_ctab = CTabConfig("C-states", ctabs=cs_l3_ctabs)
                l3_ctabs.append(l3_ctab)

        # Add S-states level 3 C-tab.
        if "S-state" in self._categories:
            metrics = self._categories["S-state"]
            l3_ctab = self._get_last_level_ctab_cfg("S-states", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a combined level 3 C-tab for temperature and power metrics.
        metrics = []
        if "Power" in self._categories:
            metrics += self._categories["Power"]
        if "Temperature" in self._categories:
            metrics += self._categories["Temperature"]
        if metrics:
            l3_ctab = self._get_last_level_ctab_cfg("Power / Temperature", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        # Create a combined level 3 C-tab for the rest of the metrics.
        metrics = []
        if "Interrupts" in self._categories:
            metrics += self._categories["Interrupts"]
        if "Instructions" in self._categories:
            metrics += self._categories["Instructions"]
        if metrics:
            l3_ctab = self._get_last_level_ctab_cfg("Miscellaneous", metrics, sname)
            if l3_ctab:
                l3_ctabs.append(l3_ctab)

        if l3_ctabs:
            return CTabConfig(sname, ctabs=l3_ctabs)

        return None

    def get_tab_cfg(self) -> CTabConfig:
        """
        Return a container tab (C-tab) object for turbostat statistics. The object describes how the
        turbostat statistics HTML tabs should be built.

        The returned C-tab includes sub-C-tabs for each scope (e.g., CPU, System) and each sub-C-tab
        includes one or multiple levels of C-tab for different categories of metrics. The leaf level
        includes D-tabs for every metric in the category.

        Returns:
            The turbostat statistics container tab (C-tab) configuration object ('CTabConfig').
        """

        l2_ctabs = []
        for sname in self._snames:
            l2_ctab = self._get_l2_ctab_cfg(sname)
            if l2_ctab:
                l2_ctabs.append(l2_ctab)

        if l2_ctabs:
            return CTabConfig(self.name, ctabs=l2_ctabs)

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
