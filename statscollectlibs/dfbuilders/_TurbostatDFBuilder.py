# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
Provide the capability of building 'pandas.DataFrames' out of raw turbostat statistics files.
"""

import pandas
from pepclibs.helperlibs.Exceptions import Error, ErrorBadFormat
from statscollectlibs.dfbuilders import _DFBuilderBase
from statscollectlibs.parsers import TurbostatParser

def split_colname(colname):
    """
    Turbostat dataframe columns have the "<scope>-<metric>" format, where "<scope>" is the scope
    name, such as "CPU0", and "<metric>" is the metric name, such as "PkgPower". Split a turbostat
    dataframe column name and return the "<scope>" and "<metric>" parts as a tuple. The arguments
    are as follows.
      * colname - a dataframe column name to split.
    """

    split = colname.split("-")
    if len(split) == 1:
        return None, colname

    return split[0], split[1]

def format_colname(metric, sname):
    """Format and return a dataframe column name for metric 'metric' and scope 'sname'."""

    if metric in {"Time_Of_Day_Seconds", "TimeElapsed"}:
        return metric
    return f"{sname}-{metric}"

class TurbostatDFBuilder(_DFBuilderBase.DFBuilderBase):
    """
    Provide the capability of building a 'pandas.DataFrames' out of raw turbostat statistics files.
    """

    def _build_cols_dict(self, tstat, scope):
        """
        Build a "columns dictionary" suitable to be used with 'pandas.DataFrame.from_dict()', which
        requires the following format: '{column_name: [value]}'. The 'tstat' dictionary has the
        '{column_name: value}' format.

        Prefix the turbostat metrics from 'tstat' with the a prefix suitable for the scope.
        """

        cols_dict = {}
        dont_prefix_metrics = {"Time_Of_Day_Seconds", "TimeElapsed"}

        for metric, value in tstat.items():
            if metric in dont_prefix_metrics:
                colname = metric
            else:
                if scope == "System":
                    prefix = "System"
                elif scope == "CPU":
                    prefix = f"CPU{self._cpunum}"
                else:
                    raise Error("BUG: unsupported scope '{scope}'")
                colname = f"{prefix}-{metric}"

            self.col2metric[colname] = metric
            cols_dict[colname] = [value]

        return cols_dict

    def _extract_cpu_data(self, parsed_dp):
        """Extract turbostat data for the measured CPU."""

        try:
            cpu_tstat = parsed_dp["cpus"][self._cpunum]
        except KeyError:
            raise Error(f"no data for CPU '{self._cpunum}' found in turbostat statistics file "
                        f"'{self._path}") from None

        # Add core level values for the metrics absent at the CPU level, but present at the core
        # level.
        try:
            for metric, value in parsed_dp["cpu2coreinfo"][self._cpunum]["totals"].items():
                if metric not in cpu_tstat:
                    cpu_tstat[metric] = value
        except KeyError:
            raise Error(f"no data for CPU '{self._cpunum}' found in turbostat statistics file "
                        f"'{self._path}") from None

        return cpu_tstat

    def _turbostat_to_df(self, parsed_dp):
        """
        Convert a parsed turbostat datapoint dictionary to a dataframe. The dataframe columns will
        be prefixed with the scope name. The arguments are as follows.
          * parsed_dp - the parsed turbostat datapoint dictionary (from 'TurbostatParser').
        """

        # Prepare the "columns dictionary", which has the '{colname: [value]}' format. This format
        # is required by 'pandas.DataFrame.from_dict()'. Start with the system-wide scope metrics.
        cols_dict = self._build_cols_dict(parsed_dp["totals"], "System")
        if self._cpunum is not None:
            cpu_tstat = self._extract_cpu_data(parsed_dp)
            cols_dict.update(self._build_cols_dict(cpu_tstat, "CPU"))

        return pandas.DataFrame.from_dict(cols_dict)

    def _read_stats_file(self, path):
        """
        Return a 'pandas.DataFrame' containing the data stored in the raw turbostat statistics file
        at path 'path'.
        """

        self._path = path

        parser = TurbostatParser.TurbostatParser(path, derivatives=True)
        generator = parser.next()

        try:
            # Try to read the first data point from raw statistics file.
            parsed_dp = next(generator)
        except StopIteration:
            raise Error(f"empty or incorrectly formatted 'turbostat' statistics file "
                        f"'{path}") from None

        # Sanity check.
        if "Time_Of_Day_Seconds" not in parsed_dp["totals"]:
            raise ErrorBadFormat(f"rejecting turbostat statistics file '{path}' - it does not "
                                 f"include time-stamps.\nCollect turbostat statistics with the "
                                 f"'--enable Time_Of_Day_Seconds' option to include time-stamps.")

        # Initialise 'df' with the first datapoint in the raw statistics file.
        df = self._turbostat_to_df(parsed_dp)

        # Add the rest of the data from the raw turbostat statistics file to 'sdf'.
        for parsed_dp in generator:
            next_row_df = self._turbostat_to_df(parsed_dp)
            df = pandas.concat([df, next_row_df], ignore_index=True)

        return df

    def __init__(self, cpunum=None):
        """
        The class constructor. The arguments are as follows.
          * cpunum - the measured CPU number.
        """

        self._cpunum = cpunum
        self._path = None

        # A dictionary mapping dataframe column names to the corresponding turbostat metric name.
        # E.g., column "Totals-CPU%c1" will be mapped to 'CPU%c1'.
        self.col2metric = {}

        super().__init__("Time_Of_Day_Seconds")
