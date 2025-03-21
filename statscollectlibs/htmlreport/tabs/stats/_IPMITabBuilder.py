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
import pandas
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import ErrorNotFound
from statscollectlibs.dfbuilders import _IPMIDFBuilder
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")


class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the IPMI statistics tab."""

    name = "IPMI"
    stnames = (
        "ipmi-inband",
        "ipmi-oob",
    )

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

        # Metric definition dictionary for all metrics in all raw results.
        self._mdd = {}
        # Categories dictionary for all metrics in all results. Keys are the category name, values
        # are list of IPMI metrics belonging to the category.
        self._categories: dict[str, list[str]] = {}

        self._message_if_mixed(lrsts)

        dfs = self._load_dfs(lrsts)

        # There will be C-tab for each category, except for the time-stamps.
        del self._categories["Timestamp"]

        super().__init__(dfs, self._mdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")

    def get_default_tab_cfg(self) -> TabConfig.CTabConfig:
        """
        Get a 'TabConfig.DTabConfig' instance with the default interrupts tab configuration.

        Returns:
            TabConfig.CTabConfig: The default configuration for the IPMI tab, including 
            container tabs and their respective data tabs.

        Notes:
            The IPMI default tab configuration includes container tabs for the following categories:
            - "Fan Speed"
            - "Temperature"
            - "Power"

            Each container tab configuration contains data tab configurations for each IPMI metric
            that is common across all results. For example, the "Fan Speed" container  tab may
            include data tabs such as "Fan1", "Fan2", etc., if these measurements are present in all
            raw IPMI statistics files. If no common IPMI metrics exist for a given category, the
            corresponding container tab will not be generated.

            Refer to '_TabBuilderBase.TabBuilderBase' for additional details on default tab
            configurations.
        """

        def _build_ctab_cfg(category: str, metrics: list[str]) -> TabConfig.CTabConfig:
            """
            Build a container tab (C-tab) configuration for a given category and metrics.

            Args:
                category: The category name (e.g., "Power") for the C-tab.
                metrics A list of metric names to include in the C-tab.

            Returns:
                TabConfig.CTabConfig: A configuration object for the C-tab, containing
                                       D-tabs (data tabs) for each metric in the provided list.

            Notes:
                Each metric in the 'metrics' list will have a corresponding D-tab
                created and added to the C-tab.
            """

            dtabs = []
            for metric in metrics:
                dtab = self._build_def_dtab_cfg(metric, self._time_metric, {}, title=metric)
                dtabs.append(dtab)

            return TabConfig.CTabConfig(category, dtabs=dtabs)

        ctabs = []

        for category, metrics in self._categories.items():
            ctab = _build_ctab_cfg(category, metrics)
            ctabs.append(ctab)

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

        dfbldr = _IPMIDFBuilder.IPMIDFBuilder()

        dfs = {}
        found_stnames = set()
        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                dfs[lres.reportid] = lres.res.load_stat(stname, dfbldr)

                self._mdd.update(dfbldr.mdo.mdd)

                for category, cat_metrics in dfbldr.mdo.categories.items():
                    if category not in self._categories:
                        self._categories[category] = []
                    self._categories[category] += cat_metrics

                found_stnames.add(stname)
                break

        for category in self._categories:
            self._categories[category] = Trivial.list_dedup(self._categories[category])

        return dfs

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
