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
from statscollectlibs.htmlreport.tabs import _DTabBuilder

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

    def get_tab(self):
        """
        Returns a '_Tabs.DTabDC' instance containing a summary table and plots describing data in
        raw AC Power statistics files.
        """

        dtab_bldr = _DTabBuilder.DTabBuilder(self._reports, self._outdir,
                                             self._defs.info[self._power_metric], self._basedir)
        scatter_axes = [(self._defs.info[self._time_metric], self._defs.info[self._power_metric])]

        dtab_bldr.add_plots(scatter_axes, [self._defs.info[self._power_metric]],
                            hover_defs=self._hover_defs)
        smry_funcs = {self._power_metric: ["max", "99.999%", "99.99%", "99.9%", "99%", "med", "avg",
                                           "min", "std"]}
        dtab_bldr.add_smrytbl(smry_funcs, self._defs)
        tab = dtab_bldr.get_tab()

        # By default the tab will be titled 'self._metric'. Change the title to "AC Power".
        tab.name = self.name
        return tab

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. Adding an ACPower tab will create an 'ACPower' sub-directory and
        store plots and the summary table in it. Arguments are as follows:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
         * outdir - the output directory in which to create the sub-directory for the built tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
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