# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating the "Measured CPU" turbostat level 2 tab.

Please, refer to '_TurbostatL2TabBuilderBase' for more information about level 2 tabs.
"""

from statscollectlibs.dfbuilders import TurbostatDFBuilder
from statscollectlibs.htmlreport.tabs.stats.turbostat import _TurbostatL2TabBuilderBase

class MCPUL2TabBuilder(_TurbostatL2TabBuilderBase.TurbostatL2TabBuilderBase):
    """
    This class provides the capability of populating the "Measured CPU" turbostat level 2 tab.
    """

    name = "Measured CPU"

    def __init__(self, rsts, outdir, basedir):
        """
        The class constructor. Adding a "measured CPU" turbostat level 2 tab will create a
        "MeasuredCPU" sub-directory and store data tabs inside it for metrics stored in the raw
        turbostat statistics files for each measured CPU.

        Arguments are the same as in '_TabBuilderBase.TabBuilderBase()' except for the following:
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
        """

        dfs = {}
        hover_defs = {}
        for res in rsts:
            if "turbostat" not in res.info["stinfo"]:
                continue

            cpunum = res.info.get("cpunum", None)
            if cpunum is None:
                continue

            dfbldr = TurbostatDFBuilder.MCPUDFBuilder(str(cpunum))
            dfs[res.reportid] = res.load_stat("turbostat", dfbldr, "turbostat.raw.txt")

            hover_defs[res.reportid] = res.get_label_defs("turbostat")

        super().__init__(dfs, outdir / self.name, basedir, hover_defs)
