# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the tab builder for the SPECjbb2015 workload.
"""

import logging
import pandas
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import ToolInfo
from statscollectlibs.defs import DefsBase
from statscollectlibs.parsers import SPECjbb2015Parser
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

_LOG = logging.getLogger()

# SPECjbb2015 metrics definition dictionary.
_SPECJBB_DEFS = {
    "max-jOPS": {"name": "max-jOPS",
                 "title": "max-jOPS",
                 "descr": "max-jOPS is the SPECjbb2015 metric characterizing the throughput and "
                          "defined as the injection rate of the last successful step level. Refer "
                          "to the SPECjbb2015 user guide for a more precise definition.",
    },
    "critical-jOPS": {"name": "critical-jOPS",
                      "title": "critical-jOPS",
                      "descr": "critical-jOPS is the SPECjbb2015 metric the responsiveness and "
                               "defined as average of the 99th percentile of the response time a "
                               "across various transaction types, load levels, and response time "
                               "SLAs. Refer to the SPECjbb2015 user guide for a more precise "
                               "definition.",
    },
}

class SPECjbb2015TabBuilder(_TabBuilderBase.TabBuilderBase):
    """
    The tab builder class for the SPECjbb2015 workload.
    """

    name = "SPECjbb2105"

    def get_default_tab_cfg(self):
        """
        Return a 'TabConfig.DTabConfig' instance with the default 'SPECjbb2015' tab configuration.
        See '_TabBuilderBase.TabBuilderBase' for more information on default tab configurations.
        """

        dtab = TabConfig.DTabConfig(self.name)
        dtab.set_smry_funcs({"max-jOPS": None, "critical-jOPS": None})

        return TabConfig.CTabConfig(self.name, dtabs=[dtab])

    def _get_scores(self, res):
        """
        Parse the SPECjbb2015 controller output file, fetch max. and critical jOPS values, and
        return as a tuple.
        """

        path = res.wldata_path / "controller.out"
        parser = SPECjbb2015Parser.SPECjbb2015Parser(path=path)

        try:
            max_jops, crit_jops = next(parser.next())
        except StopIteration:
            raise Error(f"failed to parse SPECjbb2015 controller output file at '{path}'") from None

        return max_jops, crit_jops

    def _construct_dfs(self):
        """
        Construct and return a SPECjbb2014 "defs" object.
        """

        dfs = {}
        for res in self._rsts:
            max_jops, crit_jops = self._get_scores(res)
            data = {"max-jOPS": [max_jops], "critical-jOPS": [crit_jops]}
            dfs[res.reportid] = pandas.DataFrame(data)

        return dfs

    def __init__(self, rsts, outdir, basedir=None):
        """
        The class constructor. The arguments are as follows.
         * rsts - a list of 'RORawResult' instances for which data should be included in the built
                  tab.
         * outdir - the output directory in which to create the sub-directory for the container tab.
         * basedir - base directory of the report. All paths should be made relative to this.
                     Defaults to 'outdir'.
        """

        self._rsts = rsts

        dfs = self._construct_dfs()
        defs = DefsBase.DefsBase("stats-collect", ToolInfo.TOOLNAME, info=_SPECJBB_DEFS)

        super().__init__(dfs, outdir, basedir=basedir, defs=defs)
