# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the capability of populating the IPMI statistics tab.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import ErrorNotFound
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs.stats import  _StatTabBuilderBase
from statscollectlibs.htmlreport.tabs._TabConfig import CTabConfig

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")


class IPMITabBuilder(_StatTabBuilderBase.StatTabBuilderBase):
    """Provide the capability of populating the IPMI statistics tab."""

    name = "IPMI"
    stnames = ["ipmi-inband", "ipmi-oob"]

    def __init__(self,
                 lrsts: list[LoadedResult],
                 outdir: Path,
                 basedir: Path | None = None,
                 xmetric: str | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test results to include in the tab.
            outdir: The output directory in which to create the sub-directory for the container tab.
            basedir: The base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
            xmetric: Name of the metric to use for the X-axis of the plots. If not provided, the
                     X-axis will use the time elapsed since the beginning of the measurements.
        """

        self._message_if_mixed(lrsts)

        super().__init__(lrsts, outdir, basedir=basedir, xcolname=xmetric)

        self._categories = self._get_merged_categories(lrsts)

    def get_tab_cfg(self) -> CTabConfig:
        """
        Get a container tab (C-tab) configuration object that sub-C-tab for every IPMI statistic
        categoriy, which includes D-tabs for every IPMI metric in the category.

        Returns:
            The IPMI statistics container tab (C-tab) configuration object ('CTabConfig').

        Notes:
            The IPMI tab configuration includes container tabs for metric categories, such as: Fan
            Speed, Temperature, and Power.

            Each container tab configuration object includes data tab configuration objects for each
            IPMI metric in the category. For example, the "Fan Speed" container tab may include data
            tabs such as "Fan1", "Fan2", etc.
        """

        def _build_ctab_cfg(category: str, metrics: list[str]) -> CTabConfig:
            """
            Build a container tab object for a given category and metrics.

            Args:
                category: The category name (e.g., "Power") for the C-tab.
                metrics A list of metric names to include in the C-tab.

            Returns:
                A container tab (C-tab) configuration object, describing how the HTML tabs for IPMI
                statistics should be built. The C-tab includes D-tabs (data tabs) for each metric in
                the provided list.
            """

            dtabs = []
            for metric in metrics:
                dtab = self._build_dtab_cfg(metric, title=metric)
                dtabs.append(dtab)

            return CTabConfig(category, dtabs=dtabs)

        ctabs = []

        for category, metrics in self._categories.items():
            ctab = _build_ctab_cfg(category, metrics)
            ctabs.append(ctab)

        return CTabConfig(self.name, ctabs=ctabs)

    def _message_if_mixed(self, lrsts: list[LoadedResult]):
        """Check if in-band and out-of-band IPMI statistics are mixed."""

        stpaths: dict[str, list[Path]] = {}

        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                try:
                    path = lres.res.get_stats_path(stname)
                except ErrorNotFound:
                    continue

                if stname not in stpaths:
                    stpaths[stname] = []

                # Save the path to the raw statistics file.
                stpaths[stname].append(path)

        if len(stpaths) < 2:
            return

        msg = ""
        for stname, paths in stpaths.items():
            msg += f"\n  * {stname}:"
            for path in paths:
                msg += f"\n    * {path}"

        _LOG.notice("A mix of in-band and out-of-band IPMI statistics detected:%s", msg)

    def _get_merged_categories(self, lrsts: list[LoadedResult]) -> dict[str, list[str]]:
        """
        Merge categories from different results into a single dictionary (in case some of the test
        results include categories or metrics not present in other test results).

        Args:
            lrsts: The loaded test result objects to merge the categories for.

        Returns:
            The merged categories dictionary.
        """

        categories: dict[str, list[str]] = {}

        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                lstat = lres.lsts[stname]

                for category, cat_metrics in lstat.categories.items():
                    if category not in categories:
                        categories[category] = []
                    categories[category] += cat_metrics

                break

        for category in categories:
            categories[category] = Trivial.list_dedup(categories[category])

        if "Timestamp" in categories:
            # Remove the "Timestamp" category from the categories dictionary to avoid a "Timestamp"
            # container tab in the report.
            del categories["Timestamp"]

        return categories
