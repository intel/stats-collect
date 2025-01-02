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
from statscollectlibs.mdc import MDCBase
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
    "HBIR": {"name": "HBIR",
                     "title": "high-bound injection rate",
                     "descr": "The high-bound injection rate (HBIR) is estimate for the maximum "
                              "injection rate (IR) the system can handle. In the "
                              "Response-Throughput (RT) curve building phase, the IR is gradually "
                              "increased from 0% of HBIR, with 1% of HBIR increment, until the "
                              "maximum system capacity is reached. Typically max-jOPS is lower "
                              "than HBIR, but sometimes it may be higher."
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
        smrys = {"max-jOPS": None,
                 "critical-jOPS": None,
                 "HBIR": None}
        dtab.set_smry_funcs(smrys)

        return TabConfig.CTabConfig(self.name, dtabs=[dtab])

    def _get_specjbb_info(self, res):
        """
        Parse the SPECjbb2015 logs and return SPECjbb information dictionary.
        """

        path = res.wldata_path / "controller.out"
        parser = SPECjbb2015Parser.SPECjbb2015Parser(path=path)

        try:
            specjbb_info = next(parser.next())
        except StopIteration:
            raise Error(f"failed to parse SPECjbb2015 controller output file at '{path}'") from None

        return specjbb_info

    def _construct_dfs(self):
        """Construct and return a SPECjbb2014 'Pandas.dataframe' objects."""

        dfs = {}
        for res in self._rsts:
            specjbb_info = self._get_specjbb_info(res)

            try:
                level = specjbb_info["rt_curve"]["levels"]["first_level"]
                begin_ts = specjbb_info["rt_curve"]["levels"][level]["ts"]
                level = specjbb_info["rt_curve"]["levels"]["last_level"]
                end_ts = specjbb_info["rt_curve"]["levels"][level]["ts"]

                data = {"max-jOPS": [specjbb_info["max_jops"]],
                        "critical-jOPS": [specjbb_info["crit_jops"]],
                        "HBIR": [specjbb_info["hbir"]]}
            except KeyError as err:
                raise Error(f"failed to find necessary information in SPECjbb2015 logs: "
                            f"{err}") from err

            # Limit the statistics data to the RT-curve, everything else is usually uninteresting
            # and only clutters the HTML report diagrams.
            res.set_timestamp_limits(begin_ts, end_ts, absolute=False)

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
        mdo = MDCBase.MDCBase("stats-collect", ToolInfo.TOOLNAME, mdd=_SPECJBB_DEFS)

        super().__init__(dfs, outdir, basedir=basedir, mdd=mdo.mdd)
