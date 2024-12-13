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
from pepclibs.helperlibs import Trivial
from statscollectlibs.parsers import _ParserBase

class SPECjbb2015Parser(_ParserBase.ParserBase):
    """Provide API for parsing the SPECjbb2015 controller output file."""

    def _next(self):
        """
        Yield a dictionary containing SPECjbb2015 scores. Nothing else, just quick partial
        implementation.
        """

        # Example of string to match:
        # RUN RESULT: hbIR (max attempted) = 882464, hbIR (settled) = 735487, max-jOPS = 644199, \
        # critical-jOPS = 271827
        regex = r"RUN RESULT: .* max-jOPS = (\d+), critical-jOPS = (\d+)$"

        for line in self._lines:
            match = re.match(regex, line)
            if not match:
                continue

            max_jops = Trivial.str_to_int(match.group(1), what="max-jOPS value")
            crit_jops = Trivial.str_to_int(match.group(2), what="critical-jOPS value")
            yield max_jops, crit_jops
