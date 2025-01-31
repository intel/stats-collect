# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of populating the AC Power statistics tab.
"""

import pandas
from statscollectlibs.mdc import ACPowerMDC
from statscollectlibs.dfbuilders import _ACPowerDFBuilder
from statscollectlibs.htmlreport.tabs import _TabBuilderBase

class ACPowerTabBuilder(_TabBuilderBase.TabBuilderBase):
    """Provide the capability of populating the AC Power statistics tab."""

    name = "AC Power"
    stname = "acpower"

    def get_default_tab_cfg(self):
        """
        Return a 'TabConfig.DTabConfig' instance with the default 'AC Power' tab configuration.
        See '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.
        """

        power_metric = "P"

        dtab_cfg = self._build_def_dtab_cfg(power_metric, self._time_metric, None)

        # By default the tab will be titled 'power_metric'. Change the title to "AC Power".
        dtab_cfg.name = self.name
        return dtab_cfg

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. The arguments are the same as in '_TabBuilderBase.TabBuilderBase()'
        except for the following.
          * rsts - an iterable collection of 'RORawResult' instances for which data should be
                   included in the built tab.
        """

        self._time_metric = "TimeElapsed"

        dfs = {}
        dfbldr = _ACPowerDFBuilder.ACPowerDFBuilder()
        self._hover_defs = {}
        for res in rsts:
            if self.stname not in res.info["stinfo"]:
                continue

            dfs[res.reportid] = res.load_stat(self.stname, dfbldr)
            self._hover_defs[res.reportid] = res.get_label_defs(self.stname)

        mdo = ACPowerMDC.ACPowerMDC()
        super().__init__(dfs, mdo.mdd, outdir, basedir=basedir)

        # Convert the elapsed time metric to the "datetime" format so that diagrams use a
        # human-readable format.
        for df in self._dfs.values():
            df[self._time_metric] = pandas.to_datetime(df[self._time_metric], unit="s")
