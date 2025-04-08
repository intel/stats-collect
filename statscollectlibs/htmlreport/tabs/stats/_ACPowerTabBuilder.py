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
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.htmlreport.tabs.stats import  _StatTabBuilderBase
from statscollectlibs.htmlreport.tabs._TabConfig import DTabConfig

class ACPowerTabBuilder(_StatTabBuilderBase.StatTabBuilderBase):
    """Provide the capability of populating the AC Power statistics tab."""

    name = "AC Power"
    stnames = ["acpower"]

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

    def get_tab_cfg(self) -> DTabConfig:
        """
        Get a 'DTabConfig' instance with the AC power data tab configuration.

        Returns:
            A data tab (D-tab) configuration object describing how the AC power HTML tab should be
            built.
        """

        power_metric = "P"

        dtab_cfg = self._build_dtab_cfg(power_metric)

        # By default the tab will be titled 'power_metric'. Change the title to "AC Power".
        dtab_cfg.name = self.name
        return dtab_cfg
