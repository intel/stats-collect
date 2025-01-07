# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
SPECjbb2015 controller stdout output parser.
"""

import re
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import ErrorBadFormat
from statscollectlibs.parsers import _ParserBase

class SPECjbb2015CtrlOutParser(_ParserBase.ParserBase):
    """Provide API for parsing the SPECjbb2015 controller stdout output."""

    def _parse_rt_curve(self, result, line):
        """
        Match and parse the RT-curve load levels.
        """
        # The RT-cure load level start. Example of the string to match:
        # 856s: ( 1%)   IR =   8825 ....|......... (rIR:aIR:PR = 8825:8825:8825) (tPR = 130938) [OK]
        part1 = r"^\s*(\d+)s: \(\s*(\d+)%\)\s+IR =\s+\d+ [.|?]+ "
        part2 = r"\(rIR:aIR:PR = (\d+):(\d+):(\d+)\) \(tPR = (\d+)\) \[OK\]\s+$"
        rt_ll_start_regex = re.compile(part1 + part2)

        match = re.match(rt_ll_start_regex, line)
        if not match:
            return

        if "rt_curve" not in result:
            result["rt_curve"] = {}
        if "levels" not in result["rt_curve"]:
            result["rt_curve"]["levels"] = {}

        levels = result["rt_curve"]["levels"]

        # The load levels are indexed by the HBIR percent.
        pcnt = Trivial.str_to_int(match[2], what="Load level percent index")

        levels[pcnt] = {}
        levels[pcnt]["ts"] = Trivial.str_to_int(match[1], what=f"Load level {pcnt}% time-stamp")
        levels[pcnt]["rir"] = Trivial.str_to_int(match[3], what=f"Load level {pcnt}% rIR")
        levels[pcnt]["air"] = Trivial.str_to_int(match[4], what=f"Load level {pcnt}% raIR")
        levels[pcnt]["pr"] = Trivial.str_to_int(match[5], what=f"Load level {pcnt}% PR")
        levels[pcnt]["tpr"] = Trivial.str_to_int(match[6], what=f"Load level {pcnt}% tPR")

        # The last found load level percentage.
        if "first_level" not in levels:
            levels["first_level"] = pcnt
        levels["last_level"] = pcnt

    def probe(self):
        """
        Return 'True' if the data does look like SPECjbb2015 controller stdout output, raise
        'ErrorBadFormat' otherwise.
        """

        if self._probe_status is not None:
            if self._probe_status is True:
                return True
            raise self._probe_status

        _marker_regex = re.compile("^SPECjbb2015 Java Business Benchmark$")
        for line in self._lines:
            if re.match(_marker_regex, line):
                self._probe_status = True
                return True

        self._probe_status = ErrorBadFormat("not SPECjbb2015 controller stdout output")
        raise self._probe_status

    def _next(self):
        """Yield a dictionary containing SPECjbb2015 information."""

        self.probe()

        # Example of the string to match.
        # 608s: high-bound for max-jOPS is measured to be 882464
        substring = "high-bound for max-jOPS is measured to be"
        hbir_regex = rf"^\s*\d+s: {substring} (\d+)$"

        # Example of the string to match:
        # RUN RESULT: hbIR (max attempted) = 882464, hbIR (settled) = 735487, max-jOPS = 644199, \
        # critical-jOPS = 271827
        max_crit_jops_regex = r"^RUN RESULT: .* hbIR \(settled\) = (\d+), max-jOPS = (\d+), " \
                              r"critical-jOPS = (\d+)$"

        match_dict = {
            "max_crit_jops": {
                "regex": re.compile(max_crit_jops_regex),
                "onetime": True,
                "map": {
                    "max_jops": {"group": 2, "type": int},
                    "crit_jops": {"group": 3, "type": int},
                    "hbir_settled": {"group": 1, "type": int},
                },
            },
            "hbir": {
                "regex": re.compile(hbir_regex),
                "onetime": True,
                "map": {
                    "hbir": {"group": 1, "type": int},
                },
            },
        }

        # The RT-curve start marker. Example of the string to match:
        # 792s: Building throughput-responsetime curve
        rt_start_regex = r"^\s*(\d+)s: Building throughput-responsetime curve$"

        rt_started = False
        result = {}

        for line in self._lines:
            if not rt_started:
                match = re.match(rt_start_regex, line)
                if match:
                    rt_started = True
                    continue

            if rt_started:
                if self._parse_rt_curve(result, line):
                    continue

            for mkey, minfo in match_dict.items():
                match = re.match(minfo["regex"], line)
                if not match:
                    continue
                for key, kinfo in minfo["map"].items():
                    val = match.group(kinfo["group"])
                    result[key] = kinfo["type"](val)
                break
            else:
                continue

            if match_dict[mkey]["onetime"]:
                del match_dict[mkey]

        if not result:
            raise ErrorBadFormat("no parsable information found in the SPECjbb2015 controller "
                                 "stdout output")

        yield result

    def __init__(self, path=None, lines=None):
        """
        The class constructor. Arguments are as follows.
          * path - same as in ParserBase.__init__().
          * lines - same as in ParserBase.__init__().
        """

        self._probe_status = None

        super().__init__(path, lines)
