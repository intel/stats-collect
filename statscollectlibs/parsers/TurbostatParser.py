# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2016-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
Provide the 'TurbostatParser' class which parses 'turbostat' tool output.

Terminology.
  * nontable - all the turbostat output except for the tables. Turbostat typically prints a lot of
               stuff that looks like debugging output at the very beginning, and this is referred to
               as "nontable" data. After that turbostat prints nice tables every measurement
               interval (like every 2 seconds).
  * totals - refers to the turbostat data lines (or data constructed by this parser) that
             "summarizes" metric values for multiple CPUs. For example, package totals are
             summarized values for a package. The summary function is typically an average, but may
             also be the sum or something else.
"""

import re
import logging
from itertools import zip_longest
from pepclibs.helperlibs import Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.parsers import _ParserBase

_LOG = logging.getLogger()

# The default regular expression for turbostat columns to parse.
_TABLE_START_REGEX = r".*\s*Avg_MHz\s+Busy%\s+Bzy_MHz\s+.*"

# Regular expression for matching requestable C-state names.
_REQ_CSTATES_REGEX = r"^((POLL)|(C\d+[ESP]*)|(C\d+ACPI))$"
_REQ_CSTATES_REGEX_COMPILED = re.compile(_REQ_CSTATES_REGEX)

# The functions used for calculating the totals.
TOTALS_FUNCS = {
    "sum": "sum",
    "avg": "average",
    "max": "max",
}

def get_totals_func_name(metric):
    """
    Turbostat totals are "summarized" values for multiple (or all) CPUs in the system (e.g.,
    system-wide totals, or package totals). Different turbostat metrics are summarized with
    different functions.  Return the summary function name for metric 'metric'. The arguments are as
    follows.
      * metric - name of the metric to return the summary function name name for.
    """

    # For IRQ, SMI, and C-state requests count - just return the sum.
    if metric in ("IRQ", "SMI") or re.match(_REQ_CSTATES_REGEX_COMPILED, metric):
        return "sum"
    # For temperatures, take the maximum value.
    if metric.endswith("Tmp"):
        return "max"
    return "avg"

class TurbostatParser(_ParserBase.ParserBase):
    """The 'turbostat' tool output parser."""

    def _construct_totals(self, packages):
        """
        Calculate "totals" for cores, packages, and system (all CPUs) in cases where turbostat does
        not provide them. Save them in the "totals" key of the corresponding level dictionary.
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

            agg_method = get_totals_func_name(key)
            if agg_method == "sum":
                return sum(vals)
            if agg_method == "avg":
                return sum(vals) / len(vals)
            if agg_method == "max":
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

    def _construct_tdict(self, cpus):
        """
        Construct and return the final dictionary corresponding to a parsed turbostat table.
        """

        tdict = {}
        tdict["nontable"] = self._nontable
        tdict["totals"] = self._sys_totals

        # Additionally provide the "packages" info sorted in the (Package,Core,CPU) order.
        tdict["packages"] = packages = {}
        cpu_count = core_count = pkg_count = 0
        pkgdata = {}
        coredata = {}

        for cpuinfo in cpus.values():
            # The turbostat may not include the "Package" column in case if there is only one CPU
            # package.
            package = cpuinfo.get("Package", 0)
            core = cpuinfo.get("Core", 0)

            if package not in packages:
                packages[package] = pkgdata = {}
                pkg_count += 1

            if "cores" not in pkgdata:
                pkgdata["cores"] = {}

            cores = pkgdata["cores"]
            if core not in cores:
                cores[core] = coredata = {}
                core_count += 1

            if "cpus" not in coredata:
                coredata["cpus"] = {}

            cpus = coredata["cpus"]
            cpus[cpuinfo["CPU"]] = cpuinfo
            cpu_count += 1

            # Remove the topology keys from 'cpuinfo', leaving only the metrics there.
            for key in ("Package", "Node", "Die", "Core", "CPU"):
                if key in cpuinfo:
                    del cpuinfo[key]

        tdict["cpu_count"] = cpu_count
        tdict["core_count"] = core_count
        tdict["pkg_count"] = pkg_count

        self._construct_totals(packages)

        return tdict

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

    def _parse_turbostat_line(self, line):
        """Parse a single turbostat line."""

        line_data = {}
        for metric, value in zip_longest(self._heading.keys(), line):
            # Turbostat adds "(neg)" values when it expects a positive value but reads a negative
            # one. In this case the data point should be considered invalid, so skip it.
            if value in (None, "-", "(neg)"):
                continue
            line_data[metric] = self._heading[metric](value)

        return line_data

    def _build_heading(self, heading, sys_totals):
        """
        Build the heading dictionary. They dictionary keys are the heading entries (metric names,
        CPU/core/package numbers), the values are heading value types.
        """

        self._heading = {}

        if len(heading) != len(sys_totals):
            raise ErrorBadFormat("heading and the system total lines have different amount of "
                                 "entries")

        for key, value in zip(heading, sys_totals):
            if Trivial.is_int(value):
                self._heading[key] = int
            elif Trivial.is_float(value):
                self._heading[key] = float
            else:
                self._heading[key] = str

    @staticmethod
    def _check_against_tdp(tdict, metric, multiplier):
        """
        Check if values for 'colname' are less than 'multiplier' times the package TDP.
        The arguments are as follows.
        * tdict - the turbostat table dictionary to check in.
        * colname - the name of the column to check.
        * multiplier - the number of times the TDP to compare the 'colname' values against.
        """

        if "TDP" not in tdict["nontable"]:
            return True

        tdp = tdict["nontable"]["TDP"]
        for package in tdict["packages"].values():
            if metric not in package["totals"]:
                return True

            threshold = tdp * multiplier
            val = package["totals"][metric]
            if val > threshold:
                _LOG.warning("met a turbostat datapoint with '%s' value (%sW) greater than %s "
                             "times the package TDP (%sW)", metric, val, multiplier, tdp)
                return False

        return True

    def _validate_tdict(self, tdict):
        """Validate the final turbostat table dictionary."""

        # Verify that package power does not exceed 4xTDP.
        valid = self._check_against_tdp(tdict, "PkgWatt", 4)
        if valid:
            self._invalid_tables += self._consecutive_invalid_tables
            self._consecutive_invalid_tables = 0
            return valid

        self._invalid_tables += 1
        self._consecutive_invalid_tables += 1
        if self._consecutive_invalid_tables > self._max_consecutive_invalid_tables:
            raise ErrorBadFormat(f"more than {self._max_consecutive_invalid_tables} "
                                 f"consecutive turbostat lines contain invalid data")

        if self._invalid_tables > self._tables_cnt / 2:
            pcnt = int((self._invalid_tables / self._tables_cnt) * 100)
            raise ErrorBadFormat(f"more than ({pcnt}%) of the turbostat lines contain "
                                 f"invalid data")

        return valid

    def _next(self):
        """
        Generator which yields a dictionary corresponding to one snapshot of turbostat output at a
        time.
        """

        cpus = {}

        for line in self._lines:
            # Ignore empty and 'jitter' lines like "turbostat: cpu65 jitter 2574 5881".
            if not line or line.startswith("turbostat: "):
                continue

            # Match the beginning of the turbostat table.
            if not self._sys_totals and not re.match(self._tbl_start_regex, line):
                self._add_nontable_data(line)
                continue

            self._orig_line = line
            line = line.split()
            if Trivial.is_float(line[0]):
                # This is the continuation of the table we are currently parsing. The system totals
                # line has already been parsed, and this line is for a CPU.
                line_dict = self._parse_turbostat_line(line)
                if "CPU" not in line_dict:
                    raise ErrorBadFormat(f"'CPU' value was not found in the following turbostat "
                                         f"line:\n{self._orig_line}")
                cpus[line_dict["CPU"]] = line_dict
            else:
                # This is the start of the new table.
                if cpus:
                    # Yield the turbostat table dictionary of the previous table.
                    tdict = self._construct_tdict(cpus)
                    if self._validate_tdict(tdict):
                        yield tdict
                        self._tables_cnt += 1
                    cpus = {}
                elif self._tables_cnt:
                    # This is not the first table, but nothing to yield from the previous table.
                    raise ErrorBadFormat(f"incomplete turbostat table: heading line found, but no "
                                         f"data or totals line\nLast read turbostat line:\n"
                                         f"{self._orig_line}")

                heading = line # The first line is the table heading.

                # The next line is total statistics across all CPUs, except if there is only one
                # single CPU in the system.
                line = next(self._lines)
                if not line:
                    _LOG.warning("incomplete turbostat table: no totals line after the heading "
                                 "line\nLast read turbostat line:\n%s", self._orig_line)
                    return

                self._orig_line = line
                line = line.split()
                if not self._heading:
                    self._build_heading(heading, line)

                # The very first line after the table heading is the system totals line. It does not
                # include any CPU number.
                #
                # Example (heading line, then system totals line):
                # Package Node    Core    CPU     Avg_MHz Busy%   Bzy_MHz TSC_MHz IPC     SMI ...
                # -       -       -       -       16      0.42    3762    2400    0.66    0   ...
                self._sys_totals = self._parse_turbostat_line(line)
                if "CPU" in self._sys_totals:
                    raise ErrorBadFormat(f"unexpected 'CPU' value in the following turbostat "
                                         f"system totals line:\n{self._orig_line}")

        if not cpus:
            _LOG.warning("incomplete turbostat table: no data line after the totals line\nLast "
                         "read turbostat line:\n%s", self._orig_line)
            return

        tdict = self._construct_tdict(cpus)
        if self._validate_tdict(tdict):
            yield tdict
            self._tables_cnt += 1

    def __init__(self, path=None, lines=None, derivatives=False):
        """
        TurbostatParser constructor. Arguments are as follows.
          * path - same as in ParserBase.__init__().
          * lines - same as in ParserBase.__init__().
          * derivatives - whether the derivative metrics should be added.
        """

        self._derivatives = derivatives

        # The last read turbostat line.
        self._orig_line = None

        # Count of parsed turbostat tables.
        self._tables_cnt = 0
        # Count of tables that included an invalid value.
        self._invalid_tables = 0
        # Count of consecutively met tables that included an invalid value.
        self._consecutive_invalid_tables = 0
        # Maximum amount of consecutive invalid tables.
        self._max_consecutive_invalid_tables = 4

        # Regular expression for matching the beginning of the turbostat table.
        self._tbl_start_regex = re.compile(_TABLE_START_REGEX)

        # The debug output that turbostat prints before printing the table(s).
        self._nontable = {}
        # The heading of the currently parsed turbostat table.
        self._heading = None
        # Then next line after the heading of the currently parsed turbostat table.
        self._sys_totals = None

        super().__init__(path, lines)
