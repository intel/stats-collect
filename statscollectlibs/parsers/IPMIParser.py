# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Erik Veijola <erik.veijola@intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module implements parsing for the output of the "ipmitool" utility. The input file may contain
multiple snapshots of measurement data which we call "data sets". The data sets are always separated
with the "timestamp | XYZ" lines.
"""

import datetime
import re
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error
from statscollectlibs.parsers import _ParserBase

class IPMIParser(_ParserBase.ParserBase):
    """This class represents the IPMI parser."""

    def _next_entry(self):
        """Generator which yields entries from IPMI log files."""

        # Example of a line with the timestamp format:
        # timestamp | 1705672515.054093
        ts_regex = re.compile(r"^(timestamp) \| (\d+\.\d+)$")
        entry_regex = re.compile(r"^(.+)\|(.+)\|(.+)$")
        get_ts = Trivial.str_to_num

        # Timestamps in raw 'ipmi' statistics files were changed in 'stats-collect v1.0.21' from a
        # human readable, but time-zone sensitive, format to an epoch timestamp. So catch and handle
        # each case separately. To remove support for this format, simply remove the following code
        # block. Example of a line with the old timestamp format: timestamp | 2017_01_04_11:02:46
        ts_fmt = "%Y_%m_%d_%H:%M:%S"
        old_ts_regex = re.compile(r"^(timestamp) \| (\d+_\d+_\d+_\d+:\d+:\d+)$")
        ts_line = next(self._lines, None).strip()
        if ts_line is None:
            raise Error("empty 'ipmi' statistics file")
        match = re.match(old_ts_regex, ts_line)
        if match:
            ts_regex = old_ts_regex
            # pylint: disable=unnecessary-lambda-assignment
            get_ts = lambda ts: int(datetime.datetime.strptime(ts, ts_fmt).strftime("%s"))
            # pylint: enable=unnecessary-lambda-assignment
        else:
            match = re.match(ts_regex, ts_line)
        yield (match.group(1).strip(), get_ts(match.group(2).strip()), "")

        for line in self._lines:
            line = line.strip()
            match = re.match(ts_regex, line)
            if match:
                timestamp = get_ts(match.group(2).strip())
                yield (match.group(1).strip(), timestamp, "")
            else:
                # Example of the string:
                # System Fan 4     | 2491 RPM          | ok
                match = re.match(entry_regex, line)
                if match:
                    val = match.group(2).strip()
                    data = val.split(' ', 1)
                    if val not in ["no reading", "disabled"] and len(data) > 1:
                        yield (match.group(1).strip(), Trivial.str_to_num(data[0]), data[1])
                    else:
                        yield (match.group(1).strip(), None, None)

    def _next(self):
        """
        Generator which yields a dictionary corresponding to one snapshot of ipmitool output at a
        time.
        """

        data_set = {}
        duplicates = {}

        for entry in self._next_entry():
            key = entry[0]
            if key != "timestamp":
                # IPMI records are not necessarily unique.
                if key in duplicates:
                    duplicates[key] += 1
                    key = f"{key}_{duplicates[key]}"
                duplicates[key] = 0
                data_set[key] = entry[1:]
            else:
                if data_set:
                    yield data_set

                data_set = {key: entry[1:]}
                duplicates = {}
                data_set[key] = entry[1:]

        # Yield the last data point, which is not followed by another timestamp.
        yield data_set
