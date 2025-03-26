# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>
#          Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the capability of populating the AC Power statistics tab.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
import pandas
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

class ACPowerTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the AC Power statistics tab."""

    name = "AC Power"
    stnames = ["acpower"]

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test results to include in the tab.
            outdir: The output directory in which to create the sub-directory for the container tab.
            basedir: The base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        dfs = self._load_dfs(lrsts)

        self._time_colname = self._get_time_colname(lrsts)

        mdd = self._get_merged_mdd(lrsts)

        cdd = self._build_cdd(mdd)
        super().__init__(dfs, cdd, outdir, basedir=basedir)

    def get_default_tab_cfg(self) -> TabConfig.CTabConfig:
        """
        Get a 'TabConfig.DTabConfig' instance with the default interrupts tab configuration. See
        '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.

        Returns:
            A 'TabConfig.DTabConfig' instance with the default interrupts tab configuration.
        """

        power_metric = "P"

        dtab_cfg = self._build_def_dtab_cfg(power_metric, self._time_colname, {})

        # By default the tab will be titled 'power_metric'. Change the title to "AC Power".
        dtab_cfg.name = self.name
        return dtab_cfg

    def _load_dfs(self, lrsts: list[LoadedResult]) -> dict[str, pandas.DataFrame]:
        """
        Load the AC power statistics dataframes for results in 'lrsts'.

        Args:
            lrsts: The loaded test result objects to load the dataframes for.

        Returns:
            A dictionary with keys being report IDs and values being AC power statistics dataframes.
        """

        dfs = {}
        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                lres.load_stat(stname)

                dfs[lres.reportid] = lres.lsts[stname].df

        return dfs
