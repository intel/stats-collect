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
from pepclibs.helperlibs import Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.parsers import _ParserBase

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.stats-collect.{__name__}")

# The default regular expression for turbostat columns to parse.
_TABLE_START_REGEX = r".*\s*Avg_MHz\s+Busy%\s+Bzy_MHz\s+.*"

# Regular expression for matching requestable C-state names.
_REQ_CSTATES_REGEX = r"^((POLL)|(C\d+[ESP]*)|(C\d+ACPI))$"
_REQ_CSTATES_REGEX_COMPILED = re.compile(_REQ_CSTATES_REGEX)

# Turbostat topology keys in the heading.
_TOPOLOGY_KEYS = ("Package", "Node", "Die", "Core", "CPU")

# The functions used for calculating the totals.
TOTALS_FUNCS = {
    "sum": "sum",
    "avg": "average",
    "wavg": "weighted average (weights - C0 residency)",
    "max": "max",
    "min": "min",
}

def get_totals_func_name(metric):
    """
    Turbostat totals are "summarized" values for multiple (or all) CPUs in the system (e.g.,
    system-wide totals, or package totals). Different turbostat metrics are summarized with
    different functions.  Return the summary function name for metric 'metric'. The arguments are as
    follows.
      * metric - name of the metric to return the summary function name name for.
    """

    # For IRQ, SMI, and C-state requests count.
    if metric in ("IRQ", "SMI") or re.match(_REQ_CSTATES_REGEX_COMPILED, metric):
        return "sum"
    # Package, core, RAM and GFX power.
    if metric.endswith("Watt"):
        return "sum"
    # The C-states requests rate derivative metric.
    if metric.endswith("_rate"):
        return "sum"
    # Temperatures.
    if metric.endswith("Tmp"):
        return "max"
    # The time-stamp.
    if metric in ("Time_Of_Day_Seconds", "TimeElapsed"):
        return "min"
    # The average and busy frequencies are averaged using C0 residency (Busy%) as weights.
    if metric in ("Avg_MHz", "Bzy_MHz"):
        return "wavg"
    return "avg"

class TurbostatParser(_ParserBase.ParserBase):
    """The 'turbostat' tool output parser."""

    @staticmethod
    def _summarize(fname, vals, weights=None, count=None):
        """Apply the 'fname' function to the 'vals' values."""

        if fname == "sum":
            return sum(vals)
        if fname == "avg":
            return sum(vals) / count
        if fname == "wavg":
            return sum(val * weight for val, weight in zip(vals, weights)) / count
        if fname == "min":
            return min(vals)
        if fname == "max":
            return max(vals)
        raise Error(f"BUG: unknown summary function '{fname}'")

    @staticmethod
    def _get_core_metric_values(coreinfo, metric):
        """Yield 'metric' values for all CPUs in a core."""

        for cpuinfo in coreinfo["cpus"].values():
            if metric in cpuinfo:
                yield cpuinfo[metric]

    @staticmethod
    def _get_package_metric_values(pkginfo, metric):
        """Yield 'metric' values for all CPUs in a package."""

        for cpuinfo in pkginfo["cpus"].values():
            if metric in cpuinfo:
                yield cpuinfo[metric]

    @staticmethod
    def _get_system_metric_values(tdict, metric):
        """Yield 'metric' values for all CPUs in the system."""

        for cpuinfo in tdict["cpus"].values():
            if metric in cpuinfo:
                yield cpuinfo[metric]

    def _summarize_metric(self, info, metric, level_name):
        """Calculate the 'level_name' level "total" value for metric 'metric'."""

        method_name = f"_get_{level_name}_metric_values"
        get_values_method = getattr(self, method_name)
        vals = get_values_method(info, metric)

        fname = self._metric2fname[metric]
        count = weights = None
        if fname in ("avg", "wavg"):
            count = sum(1 for _ in get_values_method(info, metric))
            if fname == "wavg":
                weights = get_values_method(info, "Busy%")

        val = self._summarize(fname, vals, weights=weights, count=count)
        return self._heading2type[metric](val)

    @staticmethod
    def _get_requestable_cstate_metrics(info):
        """Yield metric names related to requestable C-states."""

        for cnt_metric in list(info):
            if not re.match(_REQ_CSTATES_REGEX_COMPILED, cnt_metric):
                continue

            rate_metric = f"{cnt_metric}_rate" # C-state requests rate.
            time_metric = f"{cnt_metric}_time" # Avg. time in C-state per request.
            resd_metric = f"{cnt_metric}%"     # Requestable C-state residency.

            yield cnt_metric, rate_metric, time_metric, resd_metric

    def _construct_totals(self, tdict):
        """
        Calculate the totals for package and core levels. Whenever possible, use the totals provided
        by turbostat. The totals are added to the "totals" key of the corresponding level dictionary
        in 'tdict'.
        """

        if self._derivatives:
            if self._time_elapsed_metric:
                summary = self._summarize_metric(tdict, self._time_elapsed_metric, "system")
                tdict["totals"][self._time_elapsed_metric] = summary

            if self._pkgwatt_tdp_metric:
                summary = self._summarize_metric(tdict, self._pkgwatt_tdp_metric, "system")
                tdict["totals"][self._pkgwatt_tdp_metric] = summary

            iterator = self._get_requestable_cstate_metrics(tdict["totals"])
            for _, rate_metric, time_metric, _ in iterator:
                tdict["totals"][rate_metric] = self._summarize_metric(tdict, rate_metric, "system")
                tdict["totals"][time_metric] = self._summarize_metric(tdict, time_metric, "system")

        for pkginfo in tdict["packages"].values():
            pkginfo["totals"] = {}
            for metric in self._metrics["package"]:
                if metric in self._dropped_metrics:
                    continue
                pkginfo["totals"][metric] = self._summarize_metric(pkginfo, metric, "package")

            for pkginfo in pkginfo["cores"].values():
                pkginfo["totals"] = {}
                for metric in self._metrics["core"]:
                    if metric in self._dropped_metrics:
                        continue
                    pkginfo["totals"][metric] = self._summarize_metric(pkginfo, metric, "core")

        # Turbostat adds package level metrics to the first CPU data line of a package.
        # Remove them, because they are now available in package totals.
        for pkginfo in tdict["packages"].values():
            cpuinfo = pkginfo["cpus"][pkginfo["first_cpu"]]
            for metric in self._ts_totals["package"]:
                if metric in self._dropped_metrics:
                    continue
                del cpuinfo[metric]

        # Turbostat adds core level metrics to the first CPU data line of a core.
        # Remove them, because they are now available in core totals.
        for pkginfo in tdict["packages"].values():
            for coreinfo in pkginfo["cores"].values():
                for cpuinfo in coreinfo["cpus"].values():
                    for metric in self._ts_totals["core"]:
                        if metric in self._dropped_metrics:
                            continue
                        del cpuinfo[metric]
                    break

    def _construct_metrics(self, tlines):
        """
        Construct the metrics dictionary, which contains names of metrics for every topology level.
        Also construct the turbostat-provided totals dictionary, which contains names of metrics
        turbostat provides the totals for.

        Here is a stripped example of turbostat output and some discussion, for reference.

        1   Package Core  CPU  Busy%  Bzy_MHz TSC_MHz CPU%c1 CPU%c6 CoreTmp PkgTmp Pkg%pc6 PkgWatt
        2   -       -     -    0.51   3803    2401    0.53   98.34  37      40     3.18    192.41
        3   0       0     0    7.05   3798    2400    4.29   87.68  36      38     3.17    98.00
        4   0       0     192  0.02   3571    2400    4.29
        5   0       1     1    0.94   3792    2400    0.68   97.94  37
        6   0       1     193  0.30   3743    2400    0.68
        7   0       2     2    0.19   3728    2400    0.42   99.21  36
        8   0       2     194  0.14   3722    2400    0.42
        ... snip ...
        9   1       0     96   0.28   3750    2400    0.42   98.34  36      40     3.19    94.37
        10  1       0     288  0.82   3790    2400    0.42
        11  1       1     97   0.42   3748    2400    0.46   98.51  36
        12  1       1     289  0.50   3783    2400    0.46
        13  1       2     98   0.22   3720    2400    0.42   98.69  36
        14  1       2     290  0.56   3792    2400    0.42

        Line 1 - the heading line.
        Line 2 - the system totals line.
        Line 3 - CPU 0 data. But PkgTmp, Pkg%pc6, and PkgWatt are package level totals. And CPU%c6
                 and CoreTmp are core level totals.
        Line 4 - CPU 192 data. Only CPU level data, no core level totals are present.
        Line 5 - CPU 1 data. But CPU%c6 and CoreTmp are core level totals.
        Line 6 - CPU 193. Only CPU level data, no core level totals are present.
        Line 9 - CPU 96 data. Similar to CPU0, includes package and core level totals.
        Line 10 - CPU 288 data. Similar to CPU192, does not include any totals.
        Line 11 - CPU 97 data. Similar to CPU1, includes core level totals.
        """

        for cpu in tlines:
            first_cpu = cpu
            break
        else:
            raise Error("BUG: there are no CPU lines in turbostat data")

        # Build the system level metric names, which include all metrics from the turbostat totals
        # line - the first line after the heading.
        self._metrics["system"] = {metric: None for metric in self._sys_totals}

        # Build the package level metric names. The first turbostat line after the totals line is a
        # mix of core data and package level totals (line 3 in the docstring example).
        self._metrics["package"] = {metric: None for metric in tlines[first_cpu]}

        # Build the core level metric names. The turbostat line for the first CPU of a non-first
        # core (line 5 in the docstring example) provides the core level totals. However, if there
        # is only one core, use package level metric names.
        first_core = tlines[first_cpu]["Core"]
        first_package = tlines[first_cpu]["Package"]

        second_core = None
        for tline in tlines.values():
            if tline["Core"] == first_core:
                continue

            if tline["Package"] != first_package:
                break

            if second_core is None:
                # This must be the first CPU of the second core.
                self._metrics["core"] = {metric: None for metric in tline}
                second_core = tline["Core"]
            elif tline["Core"] == second_core:
                # This must be the second CPU of the second core.
                self._metrics["CPU"] = {metric: None for metric in tline}
            else:
                # There is only one CPU per core.
                break

        if "core" not in self._metrics:
            self._metrics["core"] = self._metrics["package"]
        if "CPU" not in self._metrics:
            self._metrics["CPU"] = self._metrics["core"]

        # Build the system level turbostat provides all the metrics.
        self._ts_totals["system"] = self._metrics["system"]

        # Build the list of package level totals metrics provided by turbostat.
        self._ts_totals["package"] = {}
        for metric in self._metrics["package"]:
            if metric not in self._metrics["core"]:
                self._ts_totals["package"][metric] = None

        # Build the list of core level totals metrics provided by turbostat.
        self._ts_totals["core"] = {}
        for metric in self._metrics["core"]:
            if metric not in self._metrics["CPU"]:
                self._ts_totals["core"][metric] = metric

        # Remove the topology keys.
        for key, names_dict in self._metrics.items():
            for key in _TOPOLOGY_KEYS:
                if key in names_dict:
                    del names_dict[key]
        for key, names_dict in self._ts_totals.items():
            for key in _TOPOLOGY_KEYS:
                if key in names_dict:
                    del names_dict[key]

    def _construct_metric2fname(self):
        """
        Build the dictionary mapping metric names to names of the functions that should be used for
        constructing the "totals" of the metric.
        """

        for metric in self._metrics["system"]:
            self._metric2fname[metric] = get_totals_func_name(metric)

        if not self._derivatives:
            return

        if self._time_elapsed_metric:
            totals_fname = get_totals_func_name(self._time_elapsed_metric)
            self._metric2fname[self._time_elapsed_metric] = totals_fname

        if self._pkgwatt_tdp_metric:
            totals_fname = get_totals_func_name(self._pkgwatt_tdp_metric)
            self._metric2fname[self._pkgwatt_tdp_metric] = totals_fname

        iterator = self._get_requestable_cstate_metrics(self._metrics["system"])
        for _, rate_metric, time_metric, _ in iterator:
            self._metric2fname[rate_metric] = get_totals_func_name(rate_metric)
            self._metric2fname[time_metric] = get_totals_func_name(time_metric)

    def _add_cstate_derivatives(self, info, prev_info):
        """Add a derivative C-state metrics to the 'info' metrics dictionary."""

        iterator = self._get_requestable_cstate_metrics(info)
        for cnt_metric, rate_metric, time_metric, resd_metric in iterator:
            if prev_info is None:
                # This is the very first table, but 2 tables are needed to get 2 time-stamps to
                # calculate the interval.
                info[rate_metric] = 0
                if resd_metric in info:
                    info[time_metric] = 0
                continue

            if "Time_Of_Day_Seconds" not in info:
                # The time-stamps are required to calculate the interval.
                info[rate_metric] = 0
                if resd_metric in info:
                    info[time_metric] = 0
                continue

            time = info["Time_Of_Day_Seconds"] - prev_info["Time_Of_Day_Seconds"]
            if time:
                # Add the average requests rate.
                info[rate_metric] = info[cnt_metric] / time
            else:
                # Can't divide by 0.
                info[rate_metric] = 0

            if resd_metric not in info:
                continue

            if info[cnt_metric]:
                # Calculate the spent in the C-state (in seconds).
                time = time * info[resd_metric] / 100
                # Add the average time spent in a single C-state request in microseconds.
                info[time_metric] = (time / info[cnt_metric]) * 1000000
            else:
                info[time_metric] = 0

            # Ensure the correct types.
            info[rate_metric] = self._heading2type[cnt_metric](info[rate_metric])
            info[time_metric] = self._heading2type[cnt_metric](info[time_metric])
            info[resd_metric] = self._heading2type[cnt_metric](info[resd_metric])

    def _update_heading2type(self, tdict):
        """Update the '_heading2type' dictionary with derivative metrics."""

        if self._time_elapsed_metric:
            self._heading2type[self._time_elapsed_metric] = float

        if self._pkgwatt_tdp_metric:
            self._heading2type[self._pkgwatt_tdp_metric] = float

        iterator = self._get_requestable_cstate_metrics(tdict["totals"])
        for cnt_metric, rate_metric, time_metric, resd_metric in iterator:
            if not re.match(_REQ_CSTATES_REGEX_COMPILED, cnt_metric):
                continue

            self._heading2type[rate_metric] = float
            self._heading2type[time_metric] = float
            self._heading2type[resd_metric] = float

    def _add_derivatives(self, tdict):
        """
        Add derivative metrics, which are derived from other turbostat metrics. For example, the
        C-states requests rate.
        """

        if self._time_elapsed_metric:
            if "Time_Of_Day_Seconds" not in self._heading2type:
                self._time_elapsed_metric = None

        if self._pkgwatt_tdp_metric:
            if "PkgWatt" not in self._heading2type:
                self._pkgwatt_tdp_metric = None
            if "TDP" not in self._nontable:
                if "PkgWatt" in self._heading2type:
                    _LOG.warning("TDP was not found, drop the '%s' derivative metric",
                                 self._pkgwatt_tdp_metric)
                self._pkgwatt_tdp_metric = None

        if not self._heading2type_updated:
            self._update_heading2type(tdict)
            self._heading2type_updated = True

        if self._time_elapsed_metric:
            tods = "Time_Of_Day_Seconds"
            if self._first_ts is None:
                # Calculate the smallest time-stamp value.
                self._first_ts = min([cpuinfo[tods] for cpuinfo in tdict["cpus"].values()])
            for cpuinfo in tdict["cpus"].values():
                cpuinfo[self._time_elapsed_metric] = cpuinfo[tods] - self._first_ts

        if self._pkgwatt_tdp_metric:
            for pkginfo in tdict["packages"].values():
                for cpuinfo in pkginfo["cpus"].values():
                    val = (cpuinfo["PkgWatt"] / self._nontable["TDP"]) * 100
                    type_func = self._heading2type[self._pkgwatt_tdp_metric]
                    cpuinfo[self._pkgwatt_tdp_metric] = type_func(val)
                    break

        for cpu, cpuinfo in tdict["cpus"].items():
            try:
                prev = self._prev_tdict["cpus"][cpu]
            except KeyError:
                prev = None
            self._add_cstate_derivatives(cpuinfo, prev)

    def _construct_tdict(self, tlines):
        """
        Construct and return the final dictionary corresponding to a parsed turbostat table.
        """

        tdict = {}
        tdict["nontable"] = self._nontable
        tdict["totals"] = self._sys_totals

        # Step 1.
        #
        # Build the packages -> cores -> CPUs hierarchy. The structure is going to be as follows.
        #
        # tdict = {
        #   "nontable": {...},
        #   "totals": {...},
        #   "cpus": {...},
        #   "cpu2coreinfo": {...}
        #   "packages" : {
        #       0: {
        #           "first_cpu": 0,
        #           "cpus": {...},
        #           "cores": {
        #               0: {
        #                   "cpus": {
        #                       0: {
        #                           metric: value,
        #                           ... and so on for every metric ...
        #                       },
        #                       1: {...},
        #                       ... and so on for every CPU number ...
        #                   },
        #               },
        #               1: {...},
        #               ... and so on for every core number ...
        #           },
        #       },
        #       1: {...},
        #       ... and so on for every package number ...
        #   },
        # }
        #
        # The structure is final, but there will be adjustments later, such as adding "totals" for
        # every level and removing topology keys.

        tdict["packages"] = packages = {}
        tdict["cpus"] = {}
        tdict["cpu2coreinfo"] = {}
        cpu_count = core_count = pkg_count = 0
        pkginfo = {}
        coreinfo = {}

        for cpuinfo in tlines.values():
            # Make sure there is always the "Core" and "Package" keys.
            if "Package" not in cpuinfo:
                cpuinfo["Package"] = 0
            if "Core" not in cpuinfo:
                cpuinfo["Core"] = 0

            package = cpuinfo["Package"]
            core = cpuinfo["Core"]
            cpu = cpuinfo["CPU"]

            tdict["cpus"][cpu] = cpuinfo

            if package not in packages:
                packages[package] = pkginfo = {"first_cpu": cpu, "cpus": {}}
                pkg_count += 1
            else:
                pkginfo = packages[package]

            pkginfo["cpus"][cpu] = cpuinfo

            if "cores" not in pkginfo:
                pkginfo["cores"] = {}

            if core not in pkginfo["cores"]:
                pkginfo["cores"][core] = coreinfo = {}
                core_count += 1
            else:
                coreinfo = pkginfo["cores"][core]

            tdict["cpu2coreinfo"][cpu] = coreinfo

            if "cpus" not in coreinfo:
                coreinfo["cpus"] = {}

            coreinfo["cpus"][cpu] = cpuinfo
            cpu_count += 1

        tdict["cpu_count"] = cpu_count
        tdict["core_count"] = core_count
        tdict["pkg_count"] = pkg_count

        if self._derivatives:
            self._add_derivatives(tdict)

        if not self._metrics:
            self._construct_metrics(tlines)
        if not self._metric2fname:
            self._construct_metric2fname()

        # Remove the topology keys from all turbostat lines (will also get rid for them from the CPU
        # level in 'tdict').
        for cpuinfo in tlines.values():
            for key in _TOPOLOGY_KEYS:
                if key in cpuinfo:
                    del cpuinfo[key]

        self._construct_totals(tdict)
        return tdict

    def _parse_cpu_flags(self, line):
        """Parse turbostat CPU flags."""

        prefix = "CPUID(6):"
        if line.startswith(prefix):
            tsflags = line[len(prefix):].split(",")
            self._nontable["flags"] = [tsflag.strip() for tsflag in tsflags]

    def _add_nontable_data(self, line):
        """
        Turbostat provides a log of useful information. Store some if it in the "nontable"
        dictionary.
        """

        # pylint: disable=pepc-comment-no-dot
        # Example:
        # turbostat version 2022.07.28 - Len Brown <lenb@kernel.org>
        match = re.match(r"turbostat version ([^\s]+) .*", line)
        if match:
            self._nontable["TurbostatVersion"] = match[0]
            return

        # Example:
        # 10 * 100 = 1000 MHz max efficiency frequency
        match = re.match(r"\d+ \* [.\d]+ = ([.\d]+) MHz max efficiency frequency", line)
        if match:
            self._nontable["MaxEfcFreq"] = float(match[1])
            return

        # Example:
        # 18 * 100 = 1800 MHz base frequency
        match = re.match(r"\d+ \* [.\d]+ = ([.\d]+) MHz base frequency", line)
        if match:
            self._nontable["BaseFreq"] = float(match[1])
            return

        # Example:
        # 22 * 100 = 2200 MHz max turbo 8 active cores
        match = re.match(r"\d+ \* [.\d]+ = ([.\d]+) MHz max turbo (\d+) active cores", line)
        if match:
            if "MaxTurbo" not in self._nontable:
                self._nontable["MaxTurbo"] = {}
            self._nontable["MaxTurbo"][match[2]] = float(match[1])
            return

        # Example:
        # cpu0: MSR_PKG_POWER_INFO: 0xf0ce803980528 (165 W TDP, RAPL 115 - 413 W, 0.014648 sec.)
        match = re.match(r"cpu\d+: MSR_PKG_POWER_INFO: .+ \(([.\d]+) W TDP, .+\)", line)
        if match:
            self._nontable["TDP"] = int(match[1])
            return

        self._parse_cpu_flags(line)

    def _parse_turbostat_line(self, line):
        """Parse a single turbostat line."""

        line_data = {}
        for key, value in zip(self._heading2type.keys(), line):
            # Turbostat adds "(neg)" values when it expects a positive value but reads a negative
            # one. In this case the data point should be considered invalid, so skip it.
            if value in ("-", "(neg)"):
                self._dropped_metrics.add(key)
                continue

            line_data[key] = self._heading2type[key](value)

        return line_data

    def _construct_heading2type(self, heading, sys_totals):
        """
        Build the dictionary mapping heading entries (metric names, topology keys) to the python
        the values are heading value types.
        """

        if len(heading) != len(sys_totals):
            raise ErrorBadFormat("heading and the system total lines have different amount of "
                                 "entries")

        topology_keys = set(_TOPOLOGY_KEYS)

        for key, value in zip(heading, sys_totals):
            if key in topology_keys:
                self._heading2type[key] = int
            elif Trivial.is_int(value):
                self._heading2type[key] = int
            elif Trivial.is_float(value):
                self._heading2type[key] = float
            else:
                self._heading2type[key] = str

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

    # TODO: why is the entire table dropped when only PkgWatt is invalid? How about dropping only
    # PkgWatt and keep the tdict. Yield it without PkgWatt.
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

        # Parsed turbostat data lines indexed by CPU number.
        tlines = {}

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
                tlines[line_dict["CPU"]] = line_dict
            else:
                # This is the start of the new table.
                if tlines:
                    # Yield the turbostat table dictionary of the previous table.
                    tdict = self._construct_tdict(tlines)
                    if self._validate_tdict(tdict):
                        yield tdict
                        self._prev_tdict = tdict
                        self._tables_cnt += 1
                        self._dropped_metrics = set()
                    tlines = {}
                elif self._tables_cnt:
                    # This is not the first table, but nothing to yield from the previous table.
                    raise ErrorBadFormat(f"incomplete turbostat table: heading line found, but no "
                                         f"data or totals line\nLast read turbostat line:\n"
                                         f"{self._orig_line}")

                heading = line # The first line is the table heading.

                # The next line is the system level totals.
                try:
                    line = next(self._lines)
                except StopIteration:
                    _LOG.warning("incomplete turbostat table: no totals line after the heading "
                                 "line\nLast read turbostat line:\n%s", self._orig_line)
                    return

                self._orig_line = line.strip()
                line = line.split()
                if not self._heading2type:
                    self._construct_heading2type(heading, line)

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

        if not tlines:
            _LOG.warning("incomplete turbostat table: no data line after the totals line\nLast "
                         "read turbostat line:\n%s", self._orig_line)
            return

        tdict = self._construct_tdict(tlines)
        if self._validate_tdict(tdict):
            yield tdict
            self._prev_tdict = tdict
            self._tables_cnt += 1
            self._dropped_metrics = set()

    def __init__(self, path=None, lines=None, derivatives=False):
        """
        The class constructor. Arguments are as follows.
          * path - same as in ParserBase.__init__().
          * lines - same as in ParserBase.__init__().
          * derivatives - whether the derivative metrics should be added.
        """

        self._derivatives = derivatives
        self._pkgwatt_tdp_metric = None
        self._time_elapsed_metric = None
        self._first_ts = None

        if self._derivatives:
            self._pkgwatt_tdp_metric = "PkgWatt%TDP"
            self._time_elapsed_metric = "TimeElapsed"

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

        # A dictionary indexed by topology level name (package, core, CPU) and containing metric
        # names metrics for every level.
        self._metrics = {}
        # A dictionary indexed by topology level name (package, core, CPU) and containing the metric
        # names of totals calculated and provided by turbostat. Note, turbostat does not provide
        # totals for everything. For example, for package level, turbostat does not provide the
        # C-state residency totals.
        self._ts_totals = {}

        # Regular expression for matching the beginning of the turbostat table.
        self._tbl_start_regex = re.compile(_TABLE_START_REGEX)

        # The debug output that turbostat prints before printing the table(s).
        self._nontable = {}
        # The dictionary mapping turbostat heading keys (metrics and topology keys) to python type
        # that should be used for the key.
        self._heading2type = {}
        # Whether the 'self._heading2type' dictionary was updated with derivative metrics.
        self._heading2type_updated = False
        # The dictionary mapping turbostat metric name to the summary function name.
        self._metric2fname = {}
        # Then next line after the heading of the currently parsed turbostat table.
        self._sys_totals = None
        # The previously yielded turbostat dictionary (tdict).
        self._prev_tdict = {}
        # Names of metrics that were dropped during table parsing, because of a bad value.
        self._dropped_metrics = set()

        super().__init__(path, lines)
