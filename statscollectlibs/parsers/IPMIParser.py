# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2025 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Erik Veijola <erik.veijola@intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Parse raw IPMI statistics, which may contain multiple snapshots of 'ipmitool' output (data sets),
separated with the "timestamp | <time_since_epoch>" lines.
"""

import re
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import ErrorBadFormat
from statscollectlibs.parsers import _ParserBase

class IPMIParser(_ParserBase.ParserBase):
    """Parse raw IPMI statistics."""

    def _next_entry(self):
        """Yield entries from raw IPMI statistics."""

        # Example of a line with the timestamp format:
        # timestamp | 1705672515.054093
        ts_regex = re.compile(r"^(timestamp) \| (\d+\.\d+)$")
        entry_regex = re.compile(r"^(.+)\|(.+)\|(.+)$")
        get_ts = Trivial.str_to_num

        ts_line = next(self._lines, None).strip()
        match = re.match(ts_regex, ts_line)
        if not match:
            raise ErrorBadFormat(f"unrecognized raw IPMI statistics file format.\nExpected to find "
                                 f"the time-stamp (example: 'timestamp | 1705672515.054093'), got: "
                                 f"'{ts_line}'")
        yield (match[1].strip(), get_ts(match[2].strip()), "")

        for line in self._lines:
            line = line.strip()
            match = re.match(ts_regex, line)
            if match:
                timestamp = get_ts(match[2].strip())
                yield (match[1].strip(), timestamp, "")
            else:
                # Example of the string:
                # System Fan 4     | 2491 RPM          | ok
                match = re.match(entry_regex, line)
                if match:
                    val = match[2].strip()
                    data = val.split(" ", 1)
                    if val not in ["no reading", "disabled"] and len(data) > 1:
                        yield (match[1].strip(), Trivial.str_to_num(data[0]), data[1])
                    else:
                        yield (match[1].strip(), None, None)

    def _add_derivatives(self, data_set):
        """"Add derivative metrics to the data set."""

        if not self._derivatives:
            return

        if self._first_ts is None:
            self._first_ts = data_set["timestamp"]

        data_set["TimeElapsed"] = (data_set["timestamp"][0] - self._first_ts[0], self._first_ts[1])

    def _next(self):
        """Yield a dictionary corresponding to one snapshot of ipmitool output at a time."""

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
                    self._add_derivatives(data_set)
                    yield data_set

                data_set = {key: entry[1:]}
                duplicates = {}

        # Yield the last data set.
        self._add_derivatives(data_set)
        yield data_set

    def __init__(self, path=None, lines=None, derivatives=False):
        """
        The class constructor. Arguments are as follows.
          * path - same as in ParserBase.__init__().
          * lines - same as in ParserBase.__init__().
          * derivatives - whether the derivative metrics should be added.
        """

        self._derivatives = derivatives
        self._first_ts = None

        super().__init__(path, lines)
