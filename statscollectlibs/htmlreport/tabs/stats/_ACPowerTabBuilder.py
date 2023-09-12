# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the AC Power statistics tab.
"""

from statscollectlibs.defs import ACPowerDefs
from statscollectlibs.dfbuilders import ACPowerDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase

class ACPowerTabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    This class provides the capability of populating the AC Power statistics tab.

    Public methods overview:
    1. Generate a '_Tabs.DTabDC' instance containing a summary table and plots describing data in
       raw AC Power statistics files.
        * 'get_tab()'
    """

    name = "AC Power"
    stname = "acpower"

    def get_default_tab_cfg(self):
        """
        Returns a 'TabConfig.DTabConfig' instance with the default 'AC Power' tab configuration.
        """

        smry_funcs = {self._power_metric: ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg",
                                           "min", "std"]}
        dtab_cfg = self._build_def_dtab_cfg(self._power_metric, self._time_metric, smry_funcs, None)

        # By default the tab will be titled 'self._power_metric'. Change the title to "AC Power".
        dtab_cfg.name = self.name
        return dtab_cfg

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Adding an ACPower tab will create an 'ACPower' sub-directory and
        store plots and the summary table in it.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
        """

        self._power_metric = "P"
        self._time_metric = "T"

        dfs = {}
        dfbldr = ACPowerDFBuilder.ACPowerDFBuilder()
        self._hover_defs = {}
        for res in rsts:
            if self.stname not in res.info["stinfo"]:
                continue

            dfs[res.reportid] = res.load_stat(self.stname, dfbldr, "acpower.raw.txt")
            self._hover_defs[res.reportid] = res.get_label_defs(self.stname)

        super().__init__(dfs, outdir, basedir=basedir, defs=ACPowerDefs.ACPowerDefs())
