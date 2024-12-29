# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
An unfinished, quickly put together SPECjbb2015 controller output file parser.
"""

import re
from statscollectlibs.parsers import _ParserBase

class SPECjbb2015Parser(_ParserBase.ParserBase):
    """Provide API for parsing the SPECjbb2015 controller output file."""

    def _next(self):
        """Yield a dictionary containing SPECjbb2015 information."""

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
                    "max_jops": {
                        "group": 2,
                        "type": int,
                    },
                    "crit_jops": {
                        "group": 3,
                        "type": int,
                    },
                    "hbir": {
                        "group": 1,
                        "type": int,
                    },
                },
            },
        }

        result = {}

        for line in self._lines:
            for minfo in match_dict.values():
                match = re.match(minfo["regex"], line)
                if not match:
                    continue
                for key, kinfo in minfo["map"].items():
                    val = match.group(kinfo["group"])
                    result[key] = kinfo["type"](val)
                break

        yield result