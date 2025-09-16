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

from __future__ import annotations # Remove when switching to Python 3.10+.

import typing
from pathlib import Path
import pandas
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.parsers import SPECjbb2015CtrlOutParser, SPECjbb2015CtrlLogParser
from statscollectlibs.htmlreport.tabs import _TabBuilderBase
from statscollectlibs.htmlreport.tabs._TabConfig import CTabConfig, DTabConfig
from statscollectlibs.result.LoadedResult import LoadedResult
from statscollectlibs.result import RORawResult

if typing.TYPE_CHECKING:
    from typing import TypedDict
    from statscollectlibs.result.LoadedStatistic import TimeStampLimitsTypedDict
    from statscollectlibs.htmlreport._Plot import CDTypedDict

    class _SPECjbb2015InfoTypedDict(TypedDict, total=False):
        """
        A dictionary containing SPECjbb2015 information.

        Attributes:
            max_jops: The maximum jOPS value.
            crit_jops: The critical jOPS value.
            hbir: The high-bound injection rate (HBIR).
            first_level: The first level number in the RT-curve.
            last_level: The last level number in the RT-curve.
            first_level_ts: The time-stamp of the first level in the RT-curve.
            last_level_ts: The time-stamp of the last level in the RT-curve.
        """

        max_jops: int
        crit_jops: int
        hbir: int
        first_level: int
        last_level: int
        first_level_ts: float
        last_level_ts: float

# SPECjbb2015 metrics definition dictionary.
_SPECJBB_MDD: dict[str, CDTypedDict] = {
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

    def __init__(self, lrsts: list[LoadedResult], outdir: Path, basedir: Path | None = None):
        """
        Initialize a class instance.

        Args:
            lrsts: A list of loaded test result objects to include in the tab.
            outdir: The output directory where the sub-directory for the container tab will be
                    created.
            basedir: The base directory of the report. Paths in all refences and links will be made
                     relative to this directory. Defaults to 'outdir'.
        """

        self._lrsts = lrsts

        dfs = self._construct_dfs()
        super().__init__(dfs, _SPECJBB_MDD, outdir, basedir=basedir)

    def get_tab_cfg(self) -> CTabConfig:
        """
        Create and return a container tab (C-tab) configuration object describing how the
        SPECjbb2015 C-tab should be built.

        Returns:
            The SPECjbb2015 container tab (C-tab) configuration object ('CTabConfig').

        Notes:
            At the moment the SPECjbb2015 C-tab inlcudes a single D-tab, which contains a table with
            main SPECjbb2015 metrics.
        """

        dtab = DTabConfig(self.name)
        smrys: dict[str, list[str]] = {"max-jOPS": [],
                                       "critical-jOPS": [],
                                       "HBIR": []}
        dtab.set_smry_funcs(smrys)

        return CTabConfig(self.name, dtabs=[dtab])

    def _get_specjbb_info(self, res: RORawResult.RORawResult) -> _SPECjbb2015InfoTypedDict:
        """
        Parse the SPECjbb2015 controller logs and return a dictionary with SPECjbb information.

        Returns:
            A dictionary containing SPECjbb2015 performance metrics.
        """

        if not res.wldata_path:
            raise Error(f"BUG: no SPECjbb2015 workload data path for raw result {res.reportid}")

        log_path = res.wldata_path / "controller.log"
        if not log_path.exists():
            raise Error(f"SPECjbb2015 controller log file '{log_path}' does not exist")

        log_parser = SPECjbb2015CtrlLogParser.SPECjbb2015CtrlLogParser(path=log_path)
        # TODO: there should be a TypedDict for 'log_info' and 'out_info'.
        log_info = next(log_parser.next())

        # Both SPECjbb2015 controller log and stdout output are necessary.
        out_path = res.wldata_path / "controller.out"
        if not out_path.exists():
            raise Error(f"SPECjbb2015 controller stdout file '{out_path}' does not exist")

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
                log_range = Trivial.rangify(list(log_info["rt_curve"]["levels"]))
                out_range = Trivial.rangify(list(out_info["rt_curve"]["levels"]))
                raise Error(f"SPECjbb2015 load levels count mismatch:\n"
                            f"  * controller log: {log_levels_cnt} levels ({log_range})\n"
                            f"  * controller out: {out_levels_cnt} levels ({out_range})")

            info: _SPECjbb2015InfoTypedDict = {}
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

    def _construct_dfs(self) -> dict[str, pandas.DataFrame]:
        """
        Construct and return a dictionary of dataframes for SPECjbb2015 test results.

        Returns:
            A dictionary where keys are report IDs and values are dataframes containing the
            extracted metrics.

        Notes:
            In case of SPECjbb2015 tab builder, using dataframes is an overkill. But this is what
            the base class expects, so we have to do it this way.
        """

        dfs: dict[str, pandas.DataFrame] = {}

        for lres in self._lrsts:
            info = self._get_specjbb_info(lres.res)

            data = {"max-jOPS": [info["max_jops"]],
                    "critical-jOPS": [info["crit_jops"]],
                    "HBIR": [info["hbir"]]}

            # Limit the statistics data to the RT-curve, everything else is usually uninteresting
            # and only clutters the HTML report diagrams.
            ts_range: TimeStampLimitsTypedDict = {"begin": info["first_level_ts"],
                                                  "end": info["last_level_ts"],
                                                  "absolute": True}
            lres.set_timestamp_limits(ts_range)

            dfs[lres.reportid] = pandas.DataFrame(data)

        return dfs
