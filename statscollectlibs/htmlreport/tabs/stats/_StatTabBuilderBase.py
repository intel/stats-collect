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

from typing import cast
from pathlib import Path
import pandas
from pepclibs.helperlibs import Logging
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.dfbuilders import _DFHelpers
from statscollectlibs.htmlreport.tabs._TabConfig import CTabConfig, DTabConfig
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs import _TabBuilderBase
from statscollectlibs.htmlreport.tabs._TabBuilderBase import CDTypedDict

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

class StatTabBuilderBase(_TabBuilderBase.TabBuilderBase):
    """
    The base class for tab builder classes.
    """

    # The names of the statistics the class represents. Note, not all tabs represent statistics, so
    # 'stnames' is None for non-statistic tabs.
    stnames: list[str] | None = None

    def __init__(self,
                 lrsts: list[LoadedResult],
                 outdir: Path,
                 basedir: Path | None = None,
                 xcolname: str | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test result objects to include in the tab.
            outdir: The output directory where the sub-directory with tab files will be created
                    created.
            basedir: The base directory of the report. The 'outdir' is a sub-director y of
                     'basedir'. All links and pathes generated it the tab will be relative to
                     'basedir', as opposed to be absolute. Defaults to 'outdir'.
            xcolname: Name of the dataframe column to use for the X-axis of the plots. If not
                      provided, the X-axis will use the time elapsed since the beginning of the
                      measurements.
        """

        self._lrsts = lrsts

        dfs = self._load_dfs(lrsts)

        self._time_colname = self._get_time_colname(lrsts)
        self._colnames, self._snames = self._build_colnames_and_snames(dfs)

        if not xcolname:
            xcolname = self._select_xcolname(lrsts)

        mdd = self._get_merged_mdd(lrsts)
        cdd = self._build_cdd(mdd, colnames=self._colnames)

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

                # If there are multiple statistics supported by the child class, the statistics are
                # assumed to provide the same data. Pick only one of them. For example, pick either
                # IPMI in-band or out-of-band statistics, but not both.
                break

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

        cdd: dict[str, CDTypedDict] = {}

        if colnames is None:
            colnames = list(mdd)

        # Build a metrics definition dictionary describing all columns in the dataframe.
        for colname in colnames:
            sname, metric = _DFHelpers.split_colname(colname)
            cd = cdd[colname] = cast(CDTypedDict, mdd[metric].copy())
            cd["colname"] = colname
            if sname:
                cd["sname"] = sname

        return cdd

    def _build_colnames_and_snames(self,
                                   dfs: dict[str, pandas.DataFrame]) -> tuple[list[str], list[str]]:
        """
        Build a list of column names and a list of scope names present in dataframes.

        Args:
            dfs: The dataframes to build the column names and scope names from.

        Returns:
            A tuple with two lists:
                - all unique column names in dataframes
                - all unique scope names in dataframes
        """

        colnames = []
        colnames_set: set[str] = set()
        snames = []
        snames_set: set[str] = set()

        for df in dfs.values():
            for colname in df.columns:
                sname, _ = _DFHelpers.split_colname(colname)
                if sname is not None and sname not in snames_set:
                    snames_set.add(sname)
                    snames.append(sname)
                if colname not in colnames_set:
                    colnames.append(colname)
                    colnames_set.add(colname)

        return colnames, snames

    def _select_xcolname(self, lrsts: list[LoadedResult]) -> str:
        """
        Select the dataframe column name to use for the X-axis of the plots.

        Args:
            lrsts: The loaded test result objects to select the X-axis column name from.
        """

        lrsts_no_labels: list[LoadedResult] = []
        lrsts_have_labels: list[LoadedResult] = []

        assert self.stnames is not None

        # Get the time column name from the first loaded result.
        for lres in lrsts:
            for stname in self.stnames:
                if stname not in lres.lsts:
                    continue

                if lres.lsts[stname].ldd:
                    lrsts_have_labels.append(lres)
                else:
                    lrsts_no_labels.append(lres)

        if not lrsts_have_labels:
            # Use the time column for the X-axis if there are no labels.
            return self._time_colname

        if lrsts_no_labels:
            no_labels = "\n  * ".join([str(lres.res.dirpath) for lres in lrsts_no_labels])
            have_labels = "\n  * ".join([str(lres.res.dirpath) for lres in lrsts_have_labels])
            _LOG.notice(f"Will use {self._time_colname} for the X-axes, becomes some results have "
                        f"lables, some do not have labels.\n"
                        f"The following results have labels:\n"
                        f"  * {have_labels}\n"
                        f"The following results do not have labels:\n"
                        f"  * {no_labels}")
            return self._time_colname

        # The intetnion is to use the first label as the X-axis metric. But check that all
        # statistics have the same first label.
        xmetric_candidates: dict[str, list[LoadedResult]] = {}

        for lres in lrsts_have_labels:
            for stname in self.stnames:
                if stname not in lres.lsts:
                    continue

            first_label = next(iter(lres.lsts[stname].ldd))

            if first_label not in xmetric_candidates:
                xmetric_candidates[first_label] = []
            xmetric_candidates[first_label].append(lres)

        if len(xmetric_candidates) == 1:
            # All statistics have the same first label.
            xmetric = next(iter(xmetric_candidates))
            _LOG.info("Using '%s' as the X-axis metric.", xmetric)
            return xmetric

        msg = ""
        for label, lrsts in xmetric_candidates.items():
            msg += f"\n  * {label}:"
            for lres in lrsts:
                msg += f"\n    - {lres.res.dirpath}"

        _LOG.notice(f"Will use {self._time_colname} for the X-axes, test results have different "
                    f"first labels:{msg}")

        return self._time_colname

    def get_tab_cfg(self) -> CTabConfig | DTabConfig:
        """
        Create and return the statistic tab configuration object, whi describes how the HTML tab
        should be built.

        Returns:
            The statistic tab configuration object, which can be either a container tab
            configuration object ('CTabConfig') or a data tab configuration object ('DTabConfig').

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

        raise NotImplementedError()
