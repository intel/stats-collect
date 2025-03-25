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
from statscollectlibs.mdc import MDCBase
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import _TabBuilderBase, TabConfig

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")


class IPMITabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the IPMI statistics tab."""

    name = "IPMI"
    stnames = ["ipmi-inband", "ipmi-oob"]

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

        self._message_if_mixed(lrsts)

        dfs, mdd, self._categories = self._load(lrsts)

        cdd = self._build_cdd(mdd)
        super().__init__(dfs, cdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")

    def get_default_tab_cfg(self) -> TabConfig.CTabConfig:
        """
        Get a 'TabConfig.DTabConfig' instance with the default interrupts tab configuration.

        Returns:
            TabConfig.CTabConfig: The default configuration for the IPMI tab, including container
            tabs and their respective data tabs.

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

    def _load(self, lrsts: list[LoadedResult]) -> tuple[dict[str, pandas.DataFrame],
                                                        dict[str, MDCBase.MDTypedDict],
                                                        dict[str, list[str]]]:
        """
        Build pandas dataframes for the IPMI statistics data. Merge MDDs of test results into a
        single MDD (in case some test results include metric other test results do not include).
        Merge categories of test results into a single dictionary. Return the dataframes, merged MDD
        and merged categories dictionary.

        Args:
            lrsts: A list of loaded test result objects to process.

        Returns:
            tuple:
                - A dataframes dictionarie with report IDs as keys.
                - A merged metrdics definition dictionary (MDD).
                - A dmerged categories dictionary.
        """

        dfs = {}
        mdd: dict[str, MDCBase.MDTypedDict] = {}
        categories: dict[str, list[str]] = {}

        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                if lres.reportid in dfs:
                    # Include either in-band or out-of-band statistics, but not both. They are the
                    # same, just collected with different agents.
                    continue

                lres.load_stat(stname)

                lstat = lres.lsts[stname]
                dfs[lres.reportid] = lstat.df

                mdd.update(lstat.mdd)

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

        return dfs, mdd, categories
