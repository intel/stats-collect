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
from statscollectlibs.mdc.MDCBase import MDTypedDict
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.dfbuilders import _DFHelpers
from statscollectlibs.htmlreport.tabs.stats import _StatTabBuilderBase
from statscollectlibs.htmlreport.tabs.stats._StatTabBuilderBase import CDTypedDict
from statscollectlibs.htmlreport.tabs._TabConfig import CTabConfig, DTabConfig

class InterruptsTabBuilder(_StatTabBuilderBase.StatTabBuilderBase):
    """Provide the capability to populate the interrupts statistics tab."""

    name = "Interrupts"
    stnames = ["interrupts"]

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

        super().__init__(lrsts, outdir, basedir=basedir, xcolname=xmetric)

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
            sname, metric = _DFHelpers.split_colname(colname)

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

    def get_tab_cfg(self) -> CTabConfig:
        """
        Get a container tab (C-tab) configuration object for interrupt statistics. The C-tab
        includes sub-C-tabs for system-wide and CPU-specific interrupts. Each of these C-tabs
        includes sub-C-tabs for interrupt counts and interrupt rate. And those C-tabs include
        D-tabs for individual interrupts (metrics):

        Interrupts C-tab:
            - System-wide interrupts:
                - Interrupts Count
                    - D-tab for each system-wide interrupt metric.
                - Interrupts Rate
                    - D-tab for each system-wide interrupt rate metric.
            - CPU-specific interrupts:
                Similar to system-wide interrupts, but for CPU-specific metrics

        Returns:
            The interrupt statistics container tab (C-tab) configuration object ('CTabConfig').
        """

        # Scope -> Count/Rate -> list of 'DTabConfig' objects.
        dtabs: dict[str, dict[str, list[DTabConfig]]] = {}

        for colname in self._colnames:
            sname, metric = _DFHelpers.split_colname(colname)
            if sname is None:
                continue

            if sname not in dtabs:
                dtabs[sname] = {"Interrupts Rate": [], "Interrupts Count": []}
            dtab = self._get_dtab_cfg(colname, title=metric)
            if metric.endswith("_rate"):
                dtabs[sname]["Interrupts Rate"].append(dtab)
            else:
                dtabs[sname]["Interrupts Count"].append(dtab)

        ctabs = []
        for sname, scope_info in dtabs.items():
            category_ctabs = []
            for category, category_dtabs in scope_info.items():
                category_ctabs.append(CTabConfig(category, dtabs=category_dtabs))
            ctabs.append(CTabConfig(sname, ctabs=category_ctabs))

        return CTabConfig(self.name, ctabs=ctabs)
