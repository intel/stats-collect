# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2054 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
#          Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the base class and common logic for tab builder classes.
"""

from __future__ import annotations # Remove when switching to Python 3.10+.

from pathlib import Path
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import _TabBuilderBase
from statscollectlibs.htmlreport.tabs._TabBuilderBase import CDTypedDict

class StatTabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for tab builder classes.
    """

    # The names of the statistics the class represents. Note, not all tabs represent statistics, so
    # 'stnames' is None for non-statistic tabs.
    stnames: list[str] | None = None

    def __init__(self,
                 dfs: dict[str, pandas.DataFrame],
                 cdd: dict[str, CDTypedDict],
                 outdir: Path,
                 basedir: Path | None = None,
                 xcolname: str | None = None):
        """
        Initialize a class instance.

        Args:
            outdir: The output directory where the sub-directory with tab files will be created
                    created.
            dfs: A the dataframes dictionary with report IDs as the keys and dataframes as values.
            cdd: A columns definition dictionary describing the dataframe columns to include in the
                 tab.
            basedir: The base directory of the report. The 'outdir' is a sub-director y of
                     'basedir'. All links and pathes generated it the tab will be relative to
                     'basedir', as opposed to be absolute. Defaults to 'outdir'.
            xcolname: Name of the dataframe column to use for the X-axis of the plots. If not
                      provided, the X-axis will use the time elapsed since the beginning of the
                      measurements.
        """

        super().__init__(dfs, cdd, outdir, basedir=basedir, xcolname=xcolname)

    def _get_time_colname(self, lrsts: list[LoadedResult]) -> str:
        """
        Get the dataframe column name for the time elapsed since the beginning of the measurement.

        Args:
            lrsts: The loaded results to get the time column name for.

        Returns:
            str: The time column name.
        """

        time_colname = new_time_colname = ""

        assert self.stnames is not None

        # Get the time column name from the first loaded result.
        for lres in lrsts:
            for stname in self.stnames:
                if not lres.lsts.get(stname):
                    continue

                new_time_colname = lres.lsts[stname].time_colname
                if not time_colname:
                    time_colname = new_time_colname
                elif time_colname != new_time_colname:
                    raise Error(f"BUG: time column names mismatch for '{stname}': one result "
                                f"has '{time_colname}', another has '{new_time_colname}'")

        if not time_colname:
            raise Error(f"BUG: no time column found for tab '{self.name}'")

        return time_colname

    def _load_dfs(self, lrsts: list[LoadedResult]) -> dict[str, pandas.DataFrame]:
        """
        Load the statistics dataframes for results in 'lrsts'.

        Args:
            lrsts: The loaded test result objects to load the dataframes for.

        Returns:
            A dictionary with keys being report IDs and values being statistics dataframes.
        """

        assert self.stnames is not None

        dfs = {}
        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                lres.load_stat(stname)

                dfs[lres.reportid] = lres.lsts[stname].df

        return dfs

    def _get_merged_mdd(self, lrsts: list[LoadedResult]) -> dict[str, MDTypedDict]:
        """
        Merge MDDs from different results into a single dictionary (in case some results include
        metrics not present in other test results).

        Args:
            lrsts: The loaded test result objects to merge the MDDs for.

        Returns:
            The merged MDD.
        """

        assert self.stnames is not None

        mdd: dict[str, MDTypedDict] = {}
        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.res.info["stinfo"]:
                    continue

                mdd.update(lres.lsts[stname].mdd)

        return mdd

    def get_tab_cfg(self):
        """
        Generate a 'TabConfig.DTabConfig' or 'TabConfig.CTabConfig' instance representing the tab
        configuration.
        """

        raise NotImplementedError()
