# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the 'TurbostatParser' class which parses 'turbostat' tool output.
"""

import logging
import re
from itertools import zip_longest
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.parsers import _ParserBase

_LOG = logging.getLogger()

# The default regular expression for turbostat columns to parse.
_TABLE_START_REGEX = r".*\s*Avg_MHz\s+Busy%\s+Bzy_MHz\s+.*"

# Regular expression for matching requestable C-state names.
_REQ_CSTATES_REGEX = r"^((POLL)|(C\d+[ESP]*)|(C\d+ACPI))$"

# Aggregation methods used by turbostat to summarize columns.
SUM = "sum"
AVG = "average"
MAX = "max"

def get_aggregation_method(metric):
    """
    Turbostat summaries are aggregations of values for all CPUs in the system. Different turbostat
    metrics are aggregated with different methods. The arguments are as follows.
      * metric - name of the metric to return the aggregation method name for.

    Return the aggregation method name for metric 'metric'.
    """

    # For IRQ, SMI, and C-state requests count - just return the sum.
    if metric in ("IRQ", "SMI") or re.match(_REQ_CSTATES_REGEX, metric):
        return SUM
    # For temperatures, take the maximum value.
    if metric.endswith("Tmp"):
        return MAX
    return AVG

def _check_totals_val(result, colname, multiplier):
    """
    Helper function for '_result_is_valid()'. Check if values for 'colname' in 'result' are less
    than 'multiplier' times the package TDP. Arguments are as follows:
      * result - the turbostat result dictionary.
      * colname - the name of the column to check.
      * multiplier - the number of times the TDP to compare the 'colname' values against.
    """

    tdp = result["nontable"]["TDP"]
    for package in result["packages"].values():
        totals = package["totals"]
        threshold = tdp * multiplier
        val = totals.get(colname, 0)
        if val > threshold:
            _LOG.warning("skipping a turbostat datapoint with '%s' value (%sW) greater than %s "
                         "times the TDP of the package (%sW)", colname, val, multiplier, tdp)
            return False
    return True

def _result_is_valid(result):
    """Sanity check 'result' to make sure that it does not contain any obviously wrong data."""

    # Skip the data point if it contains power values which are greater than twice the TDP of the
    # package. This check is to look for values which are extremely off and are likely the result
    # of a bug in another program. Double the TDP to account for values which are slightly over the
    # TDP.
    valid = _check_totals_val(result, "PkgWatt", 2)

    # Also skip if the data point contains RAM power values which are greater than 10 times the TDP
    # of the package to check for extremely high values.
    if valid:
        valid = _check_totals_val(result, "RAMWatt", 10)
    return valid

class TurbostatParser(_ParserBase.ParserBase):
    """The 'turbostat' tool output parser."""

    def _construct_totals(self, packages):
        """
        Turbostat provide package and core totals in some lines of the table. This function moves
        them to the "totals" key of the package hierarchy.
        """

        def calc_total(vals, key):
            """
            Calculate the "total" value for a piece of turbostat statistics defined by 'key'. The
            resulting "total" value is usually the average, but some statistics require just the
            sum, for example the IRQ count. This function returns the proper "total" value depending
            on the 'key' contents. Arguments are as follows.
              * vals - an iterable containing all of the different values of 'key'.
              * key - the name of the turbostat metric which the values in 'vals' represent.
            """

            agg_method = get_aggregation_method(key)
            if agg_method == SUM:
                return sum(vals)
            if agg_method == AVG:
                return sum(vals) / len(vals)
            if agg_method == MAX:
                return max(vals)
            raise Error(f"BUG: unable to summarize turbostat column '{key}' with method "
                        f"'{agg_method}'")

        for pkginfo in packages.values():
            for coreinfo in pkginfo["cores"].values():
                metrics = {}
                for cpuinfo in coreinfo["cpus"].values():
                    for metric, val in cpuinfo.items():
                        if metric not in metrics:
                            metrics[metric] = []
                        metrics[metric].append(val)

                if "totals" not in coreinfo:
                    coreinfo["totals"] = {}
                for metric, vals in metrics.items():
                    coreinfo["totals"][metric] = calc_total(vals, metric)

            metrics = {}
            for coreinfo in pkginfo["cores"].values():
                for metric, val in coreinfo["totals"].items():
                    if metric not in metrics:
                        metrics[metric] = []
                    metrics[metric].append(val)

            if "totals" not in pkginfo:
                pkginfo["totals"] = {}
            for metric, vals in metrics.items():
                pkginfo["totals"][metric] = calc_total(vals, metric)

        # Remove the CPU information keys that are actually not CPU-level but rather core or package
        # level. We already have these keys in core or package totals.
        common_keys = None
        for pkginfo in packages.values():
            for coreinfo in pkginfo["cores"].values():
                for cpuinfo in coreinfo["cpus"].values():
                    if common_keys is None:
                        common_keys = set(cpuinfo)
                    else:
                        common_keys &= set(cpuinfo)

        for pkginfo in packages.values():
            for coreinfo in pkginfo["cores"].values():
                for cpuinfo in coreinfo["cpus"].values():
                    for metric in list(cpuinfo):
                        if metric not in common_keys:
                            del cpuinfo[metric]

        # The the '*_MHz' totals provided by turbostat are weighted averages of the per-CPU values.
        # The weights are the amount of cycles the CPU spent executing instructions instead of being
        # in a C-state. Remove the incorrectly calculated non-weighted averages, because I was too
        # lazy to implement weighted averages calculations.
        ignore_keys = ("Avg_MHz", "Bzy_MHz")
        for pkginfo in packages.values():
            for metric in ignore_keys:
                del pkginfo["totals"][metric]
            for coreinfo in pkginfo["cores"].values():
                for metric in ignore_keys:
                    del coreinfo["totals"][metric]

    def _construct_the_result(self, cpus):
        """
        Construct and return the final dictionary corresponding to a parsed turbostat table.
        """

        result = {}
        result["nontable"] = self._nontable
        result["totals"] = self._totals

        # Additionally provide the "packages" info sorted in the (Package,Core,CPU) order.
        result["packages"] = packages = {}
        cpu_count = core_count = pkg_count = 0
        pkgdata = {}
        coredata = {}

        for cpuinfo in cpus.values():
            if "Package" not in cpuinfo:
                # The turbostat table does not include the "Package" column in case if there is only
                # one CPU package. Emulate it.
                cpuinfo["Package"] = "0"
            if cpuinfo["Package"] not in packages:
                packages[cpuinfo["Package"]] = pkgdata = {}
                pkg_count += 1
            if "cores" not in pkgdata:
                pkgdata["cores"] = {}

            cores = pkgdata["cores"]
            if cpuinfo["Core"] not in cores:
                cores[cpuinfo["Core"]] = coredata = {}
                core_count += 1

            if "cpus" not in coredata:
                coredata["cpus"] = {}
            cpus = coredata["cpus"]
            cpus[cpuinfo["CPU"]] = cpuinfo
            cpu_count += 1

            # The package/core/CPU number keys in 'cpuinfo' are not needed anymore.
            for key in ("Package", "Core", "CPU"):
                del cpuinfo[key]

        result["cpu_count"] = cpu_count
        result["core_count"] = core_count
        result["pkg_count"] = pkg_count

        self._construct_totals(packages)

        return result

    def _parse_cpu_flags(self, line):
        """Parse turbostat CPU flags."""

        prefix = "CPUID(6):"
        if line.startswith(prefix):
            tsflags = line[len(prefix):].split(",")
            self._nontable["flags"] = [tsflag.strip() for tsflag in tsflags]

    def _add_nontable_data(self, line):
        """
        Turbostat prints lots of useful information when used with the '-d' option. Try to identify
        the useful bits and add them to the "nontable" dictionary.
        """

        # pylint: disable=pepc-comment-no-dot
        # Example:
        # turbostat version 2022.07.28 - Len Brown <lenb@kernel.org>
        match = re.match(r"turbostat version ([^\s]+) .*", line)
        if match:
            self._nontable["TurbostatVersion"] = match.group(0)
            return

        # Example:
        # 10 * 100 = 1000 MHz max efficiency frequency
        match = re.match(r"\d+ \* [.\d]+ = ([.\d]+) MHz max efficiency frequency", line)
        if match:
            self._nontable["MaxEfcFreq"] = float(match.group(1))
            return

        # Example:
        # 18 * 100 = 1800 MHz base frequency
        match = re.match(r"\d+ \* [.\d]+ = ([.\d]+) MHz base frequency", line)
        if match:
            self._nontable["BaseFreq"] = float(match.group(1))
            return

        # Example:
        # 22 * 100 = 2200 MHz max turbo 8 active cores
        match = re.match(r"\d+ \* [.\d]+ = ([.\d]+) MHz max turbo (\d+) active cores", line)
        if match:
            if "MaxTurbo" not in self._nontable:
                self._nontable["MaxTurbo"] = {}
            self._nontable["MaxTurbo"][match.group(2)] = float(match.group(1))
            return

        # Example:
        # cpu0: MSR_PKG_POWER_INFO: 0xf0ce803980528 (165 W TDP, RAPL 115 - 413 W, 0.014648 sec.)
        match = re.match(r"cpu\d+: MSR_PKG_POWER_INFO: .+ \(([.\d]+) W TDP, .+\)", line)
        if match:
            self._nontable["TDP"] = int(match.group(1))
            return

        self._parse_cpu_flags(line)

    def _add_cstate_derivatives(self, cst_name, line_data):
        """
        Calculate derivatives for a C-state metric and add them to the 'line_data' dictionary.
        """

        cnt_metric = cst_name
        rate_metric = f"{cnt_metric}_rate"
        time_metric = f"{cnt_metric}_time"
        res_metric = f"{cnt_metric}%"

        if not self._prev_totals:
            # This is the very first table, but 2 tables are needed to get 2 time-stamps to
            # calculate the interval.
            line_data[rate_metric] = 0
            if res_metric in line_data:
                line_data[time_metric] = 0
            return

        if "Time_Of_Day_Seconds" not in line_data:
            # Without timestamps the interval is not known, cannot calculate the derivatives.
            line_data[rate_metric] = 0
            if res_metric in line_data:
                line_data[time_metric] = 0
            return

        time = line_data["Time_Of_Day_Seconds"] - self._prev_totals["Time_Of_Day_Seconds"]
        if time:
            # Add the average requests rate.
            line_data[rate_metric] = line_data[cnt_metric] / time
        else:
            line_data[rate_metric] = 0

        if res_metric not in line_data:
            return

        if line_data[cnt_metric]:
            # Calculate the spent in the C-state (in seconds).
            time = time * line_data[res_metric] / 100
            # Add the average time spent in a single C-state request in microseconds.
            line_data[time_metric] = (time / line_data[cnt_metric]) * 1000000
        else:
            line_data[time_metric] = 0

    def _parse_turbostat_line(self, line):
        """Parse a single turbostat line."""

        line_data = {}
        for metric, value in zip_longest(self._heading.keys(), line):
            # Turbostat adds "(neg)" values when it expects a positive value but reads a negative
            # one. In this case the data point should be considered invalid, so skip it.
            if value is not None and value != "-" and value != "(neg)":
                if not self._heading[metric]:
                    if Trivial.is_int(value):
                        self._heading[metric] = int
                    elif Trivial.is_float(value):
                        self._heading[metric] = float
                    else:
                        self._heading[metric] = str

                line_data[metric] = self._heading[metric](value)

        if self._derivatives:
            for metric in list(line_data):
                if re.match(_REQ_CSTATES_REGEX, metric):
                    self._add_cstate_derivatives(metric, line_data)
        return line_data

    def _next(self):
        """
        Generator which yields a dictionary corresponding to one snapshot of turbostat output at a
        time.
        """

        cpus = {}
        tables_started = False

        # Keep track of how many lines are skipped because they contain invalid data so that we can
        # warn the user if the file contains a large amount.
        lines_cnt = 0
        skipped_lines = 0

        # Also limit how many consecutive lines can be skipped because of invalid data.
        consecutively_skipped_lines = 0
        limit = 4

        tbl_regex = re.compile(self._tbl_start_regex)

        for line in self._lines:
            # Ignore empty and 'jitter' lines like "turbostat: cpu65 jitter 2574 5881".
            if not line or line.startswith("turbostat: "):
                continue

            lines_cnt += 1

            # Match the beginning of the turbostat table.
            if not tables_started and not re.match(tbl_regex, line):
                self._add_nontable_data(line)
                continue

            line = line.split()
            if Trivial.is_float(line[0]):
                # This is the continuation of the table we are currently parsing. It starts either
                # with a floating-point 'Time_Of_Day_Seconds' an integer 'Core' value. Each line
                # describes a single CPU.
                cpu_data = self._parse_turbostat_line(line)
                cpus[cpu_data["CPU"]] = cpu_data
            else:
                # This is the start of the new table.
                if cpus or tables_started:
                    if not cpus:
                        # This is the the special case for single-CPU systems. Turbostat does not
                        # print the totals because there is only one CPU and totals is the the same
                        # as the CPU information.
                        cpus[0] = self._totals
                    result = self._construct_the_result(cpus)
                    if _result_is_valid(result):
                        skipped_lines += consecutively_skipped_lines
                        consecutively_skipped_lines = 0
                        yield result
                    else:
                        consecutively_skipped_lines += 1
                        if consecutively_skipped_lines > limit:
                            raise ErrorBadFormat(f"more than {limit} consecutive turbostat lines "
                                                 f"contain invalid data")
                    cpus = {}

                self._heading = {}
                for key in line:
                    if "%" in key or "Watt" in key or key in {"Time_Of_Day_Seconds", "IPC"}:
                        self._heading[key] = float
                    elif key in ("Package", "Core", "CPU"):
                        self._heading[key] = str
                    else:
                        self._heading[key] = None

                # The next line is total statistics across all CPUs, except if there is only one
                # single CPU in the system.

                # False pylint warning, see issue: https://github.com/PyCQA/pylint/issues/1830.
                line = next(self._lines).split() # pylint: disable=stop-iteration-return

                # On systems with a single core turbostat does not include the "Core" column.
                # Similar to single CPU systems - the CPU column is excluded. Make sure we always
                # have them.
                for key in ("Core", "CPU"):
                    if key not in self._heading:
                        self._heading[key] = str
                        line.append("0")

                self._prev_totals = self._totals
                self._totals = self._parse_turbostat_line(line)

            tables_started = True

        result = self._construct_the_result(cpus)
        if _result_is_valid(result):
            yield result
        else:
            skipped_lines += 1

        if skipped_lines > lines_cnt / 2:
            pcnt = int((skipped_lines / lines_cnt) * 100)
            raise ErrorBadFormat(f"more than half ({pcnt}%) of the turbostat lines contain "
                                 f"invalid data")

    def __init__(self, path=None, lines=None, derivatives=False):
        """
        TurbostatParser constructor. Arguments are as follows.
          * path - same as in ParserBase.__init__().
          * lines - same as in ParserBase.__init__().
          * derivatives - whether the derivative metrics should be added.
        """

        self._derivatives = derivatives

        # Regular expression for matching the beginning of the turbostat table.
        self._tbl_start_regex = _TABLE_START_REGEX
        # The debug output that turbostat prints before printing the table(s).
        self._nontable = {}
        # The heading of the currently parsed turbostat table.
        self._heading = None
        # Then next line after the heading of the currently parsed turbostat table.
        self._totals = None
        # The "totals" line of the previously parsed table.
        self._prev_totals = None

        super().__init__(path, lines)
