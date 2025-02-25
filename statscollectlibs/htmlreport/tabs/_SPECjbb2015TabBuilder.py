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

import pandas
from pepclibs.helperlibs import Logging, Human
from pepclibs.helperlibs.Exceptions import Error
from statscollecttools import ToolInfo
from statscollectlibs.mdc import MDCBase
from statscollectlibs.parsers import SPECjbb2015CtrlOutParser, SPECjbb2015CtrlLogParser
from statscollectlibs.htmlreport.tabs import TabConfig, _TabBuilderBase

_LOG = Logging.getLogger(f"stats-collect.{__name__}")

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
        """Parse the SPECjbb2015 controller logs and return SPECjbb information dictionary."""

        log_path = res.wldata_path / "controller.log"
        if not log_path.exists():
            return False

        log_parser = SPECjbb2015CtrlLogParser.SPECjbb2015CtrlLogParser(path=log_path)
        log_info = next(log_parser.next())

        # Both SPECjbb2015 controller log and stdout output are necessary.
        out_path = res.wldata_path / "controller.out"
        if not out_path.exists():
            return False

        out_parser = SPECjbb2015CtrlOutParser.SPECjbb2015CtrlOutParser(path=out_path)
        out_info = next(out_parser.next())

        try:
            # Sanity checks.
            log_hbir = log_info["hbir"]
            out_hbir = out_info["hbir"]
            if log_hbir != out_hbir:
                raise Error(f"SPECjbb2015 HBIR mismatch:\n"
                            f"  * controller log: HBIR is {log_hbir}\n"
                            f"  * controller out: HBIR is {out_hbir}")

            log_max_jops = log_info["max_jops"]
            out_max_jops = out_info["max_jops"]
            if log_max_jops != out_max_jops:
                raise Error(f"SPECjbb2015 max-jOPS mismatch:\n"
                            f"  * controller log: max-jOPS is {log_max_jops}\n"
                            f"  * controller out: max-jOPS is {out_max_jops}")

            log_first_level = log_info["rt_curve"]["first_level"]
            out_first_level = log_info["rt_curve"]["first_level"]
            if log_first_level != out_first_level:
                raise Error(f"SPECjbb2015 load levels count mismatch:\n"
                            f"  * controller log: first level number is {log_first_level}\n"
                            f"  * controller out: first level number is {out_first_level}")

            log_last_level = log_info["rt_curve"]["last_level"]
            out_last_level = log_info["rt_curve"]["last_level"]
            if log_last_level != out_last_level:
                raise Error(f"SPECjbb2015 load levels count mismatch:\n"
                            f"  * controller log: last level number is {log_last_level}\n"
                            f"  * controller out: last level number is {out_last_level}")

            log_levels_cnt = len(log_info["rt_curve"]["levels"])
            out_levels_cnt = len(out_info["rt_curve"]["levels"])
            if log_levels_cnt != out_levels_cnt:
                log_range = Human.rangify(list(log_info["rt_curve"]["levels"]))
                out_range = Human.rangify(list(out_info["rt_curve"]["levels"]))
                raise Error(f"SPECjbb2015 load levels count mismatch:\n"
                            f"  * controller log: {log_levels_cnt} levels ({log_range})\n"
                            f"  * controller out: {out_levels_cnt} levels ({out_range})")

            info = {}
            info["max_jops"] = out_max_jops
            info["crit_jops"] = out_info["crit_jops"]
            info["hbir"] = out_hbir
            info["first_level"] = out_first_level
            info["last_level"] = out_last_level
            # Use absolute time-stamps which come from controller and are missing from controller
            # stdout.
            info["first_level_ts"] = log_info["rt_curve"]["levels"][log_first_level]["ts"]
            info["last_level_ts"] = log_info["rt_curve"]["levels"][log_last_level]["ts"]
        except KeyError as err:
            raise Error(f"failed to find necessary information in SPECjbb2015 logs: {err}") from err

        return info

    def _construct_dfs(self):
        """Construct and return a SPECjbb2014 'Pandas.dataframe' objects."""

        dfs = {}
        for res in self._rsts:
            info = self._get_specjbb_info(res)

            data = {"max-jOPS": [info["max_jops"]],
                    "critical-jOPS": [info["crit_jops"]],
                    "HBIR": [info["hbir"]]}

            # Limit the statistics data to the RT-curve, everything else is usually uninteresting
            # and only clutters the HTML report diagrams.
            res.set_timestamp_limits(info["first_level_ts"], info["last_level_ts"], absolute=True)

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

        super().__init__(dfs, mdo.mdd, outdir, basedir=basedir)
